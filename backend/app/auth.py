"""
Authentication module - handles user authentication, token creation/validation, and password hashing.
Framework-agnostic: uses only jose, bcrypt, and sqlalchemy (no FastAPI).
"""
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import jwt, JWTError
import bcrypt
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import os
from dotenv import load_dotenv
from .models import User
from .qradar_logger import qradar_logger

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day
REFRESH_TOKEN_EXPIRE_DAYS = 7
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)

# Pydantic models for request/response
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list = []

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

# Password utilities - use bcrypt directly
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password using bcrypt"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Hash a plain password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# Token utilities
def create_tokens(data: dict, expires_delta: Optional[timedelta] = None) -> tuple:
    """Create access and refresh JWT tokens"""
    to_encode = data.copy()
    
    # Access token
    access_expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": access_expire, "type": "access"})
    access_token = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    
    # Refresh token
    refresh_expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": refresh_expire, "type": "refresh"})
    refresh_token = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    
    return access_token, refresh_token

def decode_token(token: str) -> Optional[dict]:
    """Decode JWT token and return payload or None if invalid"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Authentication
def authenticate_user(db: Session, username: str, password: str, ip_address: str) -> Union[User, bool]:
    """Authenticate user with username/password; returns User or False"""
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        qradar_logger.log_login_attempt(username, ip_address, False, {"reason": "user_not_found"})
        return False
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        qradar_logger.log_login_attempt(username, ip_address, False, {
            "reason": "account_locked",
            "locked_until": user.locked_until.isoformat()
        })
        return False
    
    if not verify_password(password, user.hashed_password):
        user.login_attempts += 1
        
        if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
            user.locked_until = datetime.utcnow() + LOCKOUT_DURATION
            qradar_logger.log_suspicious_activity(username, ip_address, "multiple_failed_logins")
        
        db.commit()
        qradar_logger.log_login_attempt(username, ip_address, False, {
            "reason": "invalid_password",
            "attempts": user.login_attempts
        })
        return False
    
    # Successful login
    user.login_attempts = 0
    user.last_login = datetime.utcnow()
    user.locked_until = None
    db.commit()
    
    qradar_logger.log_login_attempt(username, ip_address, True)
    return user

def get_current_user(db: Session, token: str) -> Optional[User]:
    """Get user from token; returns User or None if invalid"""
    payload = decode_token(token)
    if not payload:
        return None
    username = payload.get("sub")
    if not username:
        return None
    user = db.query(User).filter(User.username == username).first()
    return user

def is_admin(user: User) -> bool:
    """Check if user has admin role"""
    return user and user.role == "admin"
