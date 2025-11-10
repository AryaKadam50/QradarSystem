from datetime import datetime, timedelta
from typing import Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import os
from dotenv import load_dotenv
from .db import get_db
from .models import User
from .qradar_logger import qradar_logger

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day
REFRESH_TOKEN_EXPIRE_DAYS = 7
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = []

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_tokens(data: dict, expires_delta: Optional[timedelta] = None) -> tuple[str, str]:
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

async def authenticate_user(db: Session, username: str, password: str, ip_address: str) -> Union[User, bool]:
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

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    
    return user

def require_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires admin privileges"
        )
