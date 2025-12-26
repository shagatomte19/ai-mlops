"""
Authentication Router - User registration, login, and token management.
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field, field_validator
import secrets

from ..core.database import get_db
from ..core.security import (
    verify_password,
    get_password_hash,
    create_tokens,
    decode_token,
    create_access_token,
    Token
)
from ..core.validators import validate_email, validate_password
from ..core.logging import logger
from ..models.user import User
from ..dependencies import get_current_user, get_current_active_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============ Request/Response Schemas ============

class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def validate_pass(cls, v: str) -> str:
        is_valid, error = validate_password(v)
        if not is_valid:
            raise ValueError(error)
        return v


class UserResponse(BaseModel):
    """Schema for user response (excludes sensitive data)."""
    id: int
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    is_verified: bool
    api_requests_count: int
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh."""
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    """Schema for password change."""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @field_validator('new_password')
    @classmethod
    def validate_new_pass(cls, v: str) -> str:
        is_valid, error = validate_password(v)
        if not is_valid:
            raise ValueError(error)
        return v


# ============ Endpoints ============

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    - Validates email format and password strength
    - Creates user with hashed password
    - Returns JWT tokens for immediate login
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        api_key=secrets.token_urlsafe(32)  # Generate API key
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New user registered: {new_user.email}")
    
    # Generate tokens
    tokens = create_tokens(new_user.email)
    
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and get JWT tokens.
    
    Uses OAuth2 password flow (form data with username/password).
    The 'username' field should contain the email address.
    """
    # Find user by email (username field in OAuth2)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    logger.info(f"User logged in: {user.email}")
    
    # Generate tokens
    tokens = create_tokens(user.email)
    
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using a valid refresh token.
    """
    # Decode refresh token
    token_data = decode_token(request.refresh_token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    if token_data.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    # Verify user still exists and is active
    user = db.query(User).filter(User.email == token_data.sub).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new access token
    new_access_token = create_access_token(user.email)
    
    return Token(
        access_token=new_access_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user's information.
    """
    return UserResponse.model_validate(current_user)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password.
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    logger.info(f"Password changed for user: {current_user.email}")
    
    return {"message": "Password updated successfully"}


@router.post("/regenerate-api-key")
async def regenerate_api_key(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new API key for the current user.
    """
    new_api_key = secrets.token_urlsafe(32)
    current_user.api_key = new_api_key
    db.commit()
    
    logger.info(f"API key regenerated for user: {current_user.email}")
    
    return {
        "message": "API key regenerated",
        "api_key": new_api_key
    }


@router.get("/api-key")
async def get_api_key(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's API key.
    """
    return {
        "api_key": current_user.api_key
    }
