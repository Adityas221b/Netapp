"""
CloudFlux AI - Authentication Routes
User registration, login, and profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import hashlib
import logging

from app.database import get_db
from app.models import User, AuditLog
from app.auth import (
    get_password_hash,
    verify_password,
    create_user_token,
    get_current_active_user
)
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# ==================== In-Memory User Store ====================
# Fallback authentication when database is not available

IN_MEMORY_USERS = {}
SALT = "cloudflux2025"

def hash_password_simple(password: str) -> str:
    """Simple SHA256 hashing for in-memory users"""
    return f"{SALT}${hashlib.sha256((SALT + password).encode()).hexdigest()}"

def verify_password_simple(plain_password: str, hashed_password: str) -> bool:
    """Verify password against simple hash"""
    if "$" not in hashed_password:
        return False
    salt, hash_value = hashed_password.split("$", 1)
    computed_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
    return computed_hash == hash_value

# Initialize default test user
def create_default_users():
    """Create default test users in memory"""
    user_id = str(uuid.uuid4())
    IN_MEMORY_USERS["testuser"] = {
        "id": user_id,
        "email": "test@cloudflux.ai",
        "username": "testuser",
        "hashed_password": "cloudflux2025$810a7d13610b318e76f8cad883916a86367a333c2b2835039547d482405ed182",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False,
        "created_at": datetime.now()
    }
    logger.info("✅ Default test user created: testuser / testpass123")

create_default_users()

# ==================== Request/Response Models ====================

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

# ==================== Public Endpoints ====================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user account
    
    - **email**: Valid email address (must be unique)
    - **username**: Username (must be unique)
    - **password**: Password (min 8 characters recommended)
    - **full_name**: Optional full name
    
    Returns JWT token and user information
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Validate password strength
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    # Create new user
    new_user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create audit log AFTER user is committed
    audit = AuditLog(
        id=str(uuid.uuid4()),
        action="register",
        entity_type="user",
        entity_id=new_user.id,
        user_id=new_user.id,
        user_email=new_user.email,
        description=f"User registered: {new_user.email}"
    )
    db.add(audit)
    db.commit()
    
    # Generate token
    token = create_user_token(new_user.id, new_user.email)
    
    return {
        **token,
        "user": new_user
    }

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email/username and password
    
    Accepts OAuth2 password flow (username + password)
    Returns JWT token for authenticated requests
    """
    user = None
    is_memory_user = False
    
    # First, check in-memory users (for demo/testing)
    mem_user = IN_MEMORY_USERS.get(form_data.username)
    if not mem_user:
        # Try by email
        for username, user_data in IN_MEMORY_USERS.items():
            if user_data.get("email") == form_data.username:
                mem_user = user_data
                break
    
    if mem_user:
        # Verify password using simple hash
        if not verify_password_simple(form_data.password, mem_user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not mem_user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        # Generate token for in-memory user
        token = create_user_token(mem_user["id"], mem_user["email"])
        logger.info(f"✅ In-memory user logged in: {mem_user['username']}")
        
        return {
            **token,
            "user": mem_user
        }
    
    # Try database user
    try:
        user = db.query(User).filter(
            (User.email == form_data.username) | (User.username == form_data.username)
        ).first()
    except Exception as db_error:
        logger.warning(f"Database error during login: {db_error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Create audit log
    try:
        audit = AuditLog(
            id=str(uuid.uuid4()),
            action="login",
            entity_type="user",
            entity_id=user.id,
            user_id=user.id,
            user_email=user.email,
            description=f"User logged in: {user.email}"
        )
        db.add(audit)
        db.commit()
    except Exception as audit_error:
        logger.warning(f"Failed to create audit log: {audit_error}")
    
    # Generate token
    token = create_user_token(user.id, user.email)
    logger.info(f"✅ Database user logged in: {user.email}")
    
    return {
        **token,
        "user": user
    }

@router.post("/login/json", response_model=TokenResponse)
async def login_json(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Alternative login endpoint accepting JSON
    
    - **email**: Email address or username
    - **password**: User password
    
    Returns JWT token and user information
    """
    # Try to find user by email or username
    user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.email)
    ).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Create audit log
    audit = AuditLog(
        id=str(uuid.uuid4()),
        action="login",
        entity_type="user",
        entity_id=user.id,
        user_id=user.id,
        user_email=user.email,
        description=f"User logged in: {user.email}"
    )
    db.add(audit)
    db.commit()
    
    # Generate token
    token = create_user_token(user.id, user.email)
    
    return {
        **token,
        "user": user
    }

# ==================== Protected Endpoints ====================

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user's information
    
    Requires valid JWT token in Authorization header
    """
    # If current_user is a dict (token-only auth), check in-memory first, then DB
    if isinstance(current_user, dict):
        user_id = current_user["user_id"]
        
        # Check in-memory users first
        for username, user_data in IN_MEMORY_USERS.items():
            if user_data["id"] == user_id:
                logger.info(f"✅ Retrieved in-memory user: {username}")
                return user_data
        
        # Fall back to database
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                return user
        except Exception as db_error:
            logger.warning(f"Database error fetching user: {db_error}")
        
        raise HTTPException(status_code=404, detail="User not found")
    
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    full_name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile information
    
    Requires valid JWT token in Authorization header
    """
    # Fetch user from DB if needed
    if isinstance(current_user, dict):
        user_id = current_user["user_id"]
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    else:
        user = current_user
    
    # Update fields
    if full_name is not None:
        user.full_name = full_name
    
    # Create audit log
    audit = AuditLog(
        id=str(uuid.uuid4()),
        action="update",
        entity_type="user",
        entity_id=user.id,
        user_id=user.id,
        user_email=user.email,
        description=f"User updated profile: {user.email}"
    )
    db.add(audit)
    
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout current user
    
    Note: JWT tokens are stateless, so this is primarily for audit logging
    Client should delete the token from storage
    """
    return {
        "message": "Successfully logged out",
        "detail": "Please delete the token from client storage"
    }
