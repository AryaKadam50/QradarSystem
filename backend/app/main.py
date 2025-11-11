"""
Flask-based REST API for secure login and activity monitoring with QRadar integration.
Endpoints:
  POST /auth/signup - Register new user
  POST /auth/login - Login and get JWT tokens
  GET /users/me - Get current user profile
  PUT /users/me - Update user profile
  GET /admin/users - List all users (admin only)
  GET /admin/logs - View activity logs (admin only)
  GET /health - Health check
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import os
from dotenv import load_dotenv

from .db import SessionLocal, engine, Base
from .models import User, ActivityLog
from .auth import (
    authenticate_user, get_current_user, is_admin,
    create_tokens, UserCreate, Token, decode_token
)
from .qradar_logger import qradar_logger
from .logger_conf import logger

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# CORS configuration - restrict to frontend origin
CORS(app, resources={
    r"/auth/*": {"origins": "http://localhost:8080"},
    r"/users/*": {"origins": "http://localhost:8080"},
    r"/admin/*": {"origins": "http://localhost:8080"},
    r"/health": {"origins": "*"}
})

# ==================== HELPER FUNCTIONS ====================

def get_token_from_header():
    """Extract JWT token from Authorization header"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    return auth_header[7:]  # Remove 'Bearer ' prefix

def require_auth(f):
    """Decorator to require valid JWT token"""
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return jsonify({"detail": "Missing authorization token"}), 401
        
        db = SessionLocal()
        user = get_current_user(db, token)
        db.close()
        
        if not user:
            return jsonify({"detail": "Invalid or expired token"}), 401
        
        # Pass user to the route handler
        request.current_user = user
        return f(*args, **kwargs)
    
    decorated.__name__ = f.__name__
    return decorated

def require_admin(f):
    """Decorator to require admin role"""
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return jsonify({"detail": "Missing authorization token"}), 401
        
        db = SessionLocal()
        user = get_current_user(db, token)
        db.close()
        
        if not user:
            return jsonify({"detail": "Invalid or expired token"}), 401
        
        if not is_admin(user):
            return jsonify({"detail": "Insufficient permissions"}), 403
        
        request.current_user = user
        return f(*args, **kwargs)
    
    decorated.__name__ = f.__name__
    return decorated

# ==================== ROUTES ====================

@app.post('/auth/signup')
def signup():
    """Register a new user"""
    db = SessionLocal()
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({"detail": "Missing required fields"}), 400
        
        # Check if user exists
        if db.query(User).filter(User.username == data['username']).first():
            return jsonify({"detail": "Username already exists"}), 400
        
        if db.query(User).filter(User.email == data['email']).first():
            return jsonify({"detail": "Email already exists"}), 400
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data.get('full_name', '')
        )
        user.set_password(data['password'])
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Log signup
        ActivityLog.log_activity(
            db=db,
            user_id=user.id,
            action="SIGNUP",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            status="success"
        )
        
        logger.info(f"User signup: {user.username}")
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }), 201
        
    except IntegrityError:
        db.rollback()
        return jsonify({"detail": "Database error - user may already exist"}), 400
    finally:
        db.close()

@app.post('/auth/login')
def login():
    """Login user and return JWT tokens"""
    db = SessionLocal()
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"detail": "Missing username or password"}), 400
        
        user = authenticate_user(db, data['username'], data['password'], request.remote_addr)
        
        if not user:
            return jsonify({"detail": "Invalid credentials"}), 401
        
        # Create tokens
        access_token, refresh_token = create_tokens({'sub': user.username, 'role': user.role})
        
        logger.info(f"User login success: {user.username}")
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }), 200
        
    finally:
        db.close()

@app.get('/users/me')
@require_auth
def get_profile():
    """Get current user profile"""
    user = request.current_user
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "last_login": user.last_login.isoformat() if user.last_login else None
    }), 200

@app.put('/users/me')
@require_auth
def update_profile():
    """Update current user profile"""
    db = SessionLocal()
    try:
        user = request.current_user
        data = request.get_json()
        
        # Update fields
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'email' in data:
            user.email = data['email']
        
        # Handle password change
        if data.get('new_password') and data.get('current_password'):
            if not user.check_password(data['current_password']):
                return jsonify({"detail": "Incorrect password"}), 400
            user.set_password(data['new_password'])
        
        db.commit()
        
        # Log update
        ActivityLog.log_activity(
            db=db,
            user_id=user.id,
            action="PROFILE_UPDATE",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            status="success"
        )
        
        logger.info(f"User profile updated: {user.username}")
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }), 200
        
    finally:
        db.close()

@app.get('/admin/users')
@require_admin
def list_users():
    """List all users (admin only)"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return jsonify([{
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "last_login": u.last_login.isoformat() if u.last_login else None
        } for u in users]), 200
        
    finally:
        db.close()

@app.get('/admin/logs')
@require_admin
def get_logs():
    """Get activity logs (admin only)"""
    db = SessionLocal()
    try:
        logs = db.query(ActivityLog).order_by(ActivityLog.timestamp.desc()).limit(500).all()
        return jsonify([{
            "id": l.id,
            "user_id": l.user_id,
            "username": l.user.username if l.user else None,
            "timestamp": l.timestamp.isoformat(),
            "action": l.action,
            "ip_address": l.ip_address,
            "status": l.status,
            "details": l.details
        } for l in logs]), 200
        
    finally:
        db.close()

@app.get('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"detail": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"detail": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"detail": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
