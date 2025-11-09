"""
CloudFlux AI - JWT Authentication Service
Handles user authentication, token generation, and password hashing
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
import hashlib

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "cloudflux-super-secret-key-change-in-production-2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    # Simple hash verification using SHA-256
    if '$' in hashed_password:
        salt, hash_value = hashed_password.split('$', 1)
        computed_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
        return computed_hash == hash_value
    return False

def get_password_hash(password: str) -> str:
    """Hash a password for storage"""
    # Generate a simple salt
    salt = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
    # Create hash with salt
    password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${password_hash}"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary containing claims to encode in the token
        expires_delta: Optional expiration time delta
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency to get the current authenticated user from JWT token
    
    Args:
        token: JWT token from Authorization header
    
    Returns:
        User info dict
    
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Return user info from token including role
    return {
        "user_id": user_id, 
        "sub": user_id,  # Add 'sub' key for compatibility
        "email": payload.get("email"),
        "role": payload.get("role", "admin")  # Include role from token, default to admin
    }

async def get_current_active_user(current_user = Depends(get_current_user)):
    """Dependency to ensure user is active"""
    if isinstance(current_user, dict):
        return current_user
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def create_user_token(user_id: str, email: str) -> dict:
    """
    Create authentication tokens for a user
    
    Args:
        user_id: User's unique ID
        email: User's email
    
    Returns:
        Dictionary with access_token and token_type
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id, "email": email},
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds
    }
