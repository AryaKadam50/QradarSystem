from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, constr, validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

from .db import SessionLocal, engine, Base
from .models import User, ActivityLog
from .auth import (
    authenticate_user, get_current_user, require_admin,
    create_tokens, UserCreate, Token
)
from .qradar_logger import qradar_logger
from .logger_conf import logger

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="Secure Login App",
    description="A secure web application with QRadar integration",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Restrict to frontend origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserUpdateRequest(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    current_password: Optional[str]
    new_password: Optional[str]

    @validator('new_password')
    def validate_password(cls, v):
        if v:
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters')
            if not any(c.isupper() for c in v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not any(c.islower() for c in v):
                raise ValueError('Password must contain at least one lowercase letter')
            if not any(c.isdigit() for c in v):
                raise ValueError('Password must contain at least one number')
            if not any(c in '!@#$%^&*()' for c in v):
                raise ValueError('Password must contain at least one special character')
        return v

class ActivityLogResponse(BaseModel):
    id: int
    timestamp: datetime
    action: str
    ip_address: str
    status: str
    details: Optional[dict]
    username: str
    
    class Config:
        from_attributes = True

# Endpoints
@app.post("/auth/signup", response_model=UserResponse)
async def signup(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(lambda: SessionLocal())
):
    try:
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name
        )
        user.set_password(user_data.password)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Log successful signup
        ActivityLog.log_activity(
            db=db,
            user_id=user.id,
            action="SIGNUP",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            status="success"
        )
        
        qradar_logger.log_suspicious_activity(
            username=user.username,
            ip_address=request.client.host,
            activity_type="new_account_created"
        )
        
        return user
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )

@app.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(lambda: SessionLocal())
):
    user = await authenticate_user(
        db,
        form_data.username,
        form_data.password,
        request.client.host
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token, refresh_token = create_tokens(
        data={"sub": user.username, "role": user.role}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

@app.put("/users/me", response_model=UserResponse)
async def update_user(
    user_update: UserUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(lambda: SessionLocal())
):
    if user_update.current_password and user_update.new_password:
        if not current_user.check_password(user_update.current_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )
        current_user.set_password(user_update.new_password)
    
    if user_update.email:
        current_user.email = user_update.email
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    
    db.commit()
    
    ActivityLog.log_activity(
        db=db,
        user_id=current_user.id,
        action="PROFILE_UPDATE",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        status="success"
    )
    
    return current_user

@app.get("/admin/users", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(lambda: SessionLocal())
):
    return db.query(User).all()

@app.get("/admin/logs", response_model=List[ActivityLogResponse])
async def get_activity_logs(
    current_user: User = Depends(require_admin),
    db: Session = Depends(lambda: SessionLocal())
):
    logs = db.query(ActivityLog).order_by(ActivityLog.timestamp.desc()).all()
    return logs

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# NOTE: Additional helper endpoints (profile alias) for compatibility with frontend
@app.get("/profile", response_model=UserResponse)
async def profile_alias(current_user: User = Depends(get_current_user)):
    return current_user

@app.put("/profile", response_model=UserResponse)
async def profile_update_alias(upd: UserUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(lambda: SessionLocal())):
    if upd.full_name is not None:
        current_user.full_name = upd.full_name
    if upd.email is not None:
        current_user.email = upd.email
    if upd.new_password and upd.current_password:
        if not current_user.check_password(upd.current_password):
            raise HTTPException(status_code=400, detail="Incorrect current password")
        current_user.set_password(upd.new_password)
    db.add(current_user)
    db.commit()
    ActivityLog.log_activity(
        db=db,
        user_id=current_user.id,
        action="PROFILE_UPDATE",
        ip_address="unknown",
        user_agent=None,
        status="success"
    )
    return current_user
