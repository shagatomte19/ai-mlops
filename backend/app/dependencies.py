"""
FastAPI Dependencies for authentication and authorization.
Provides reusable dependency functions for route protection.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .core.database import get_db
from .core.security import decode_token
from .models.user import User


# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False  # Don't auto-error, let us handle it for optional auth
)

# Strict OAuth2 scheme (auto-errors if no token)
oauth2_scheme_required = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=True
)


async def get_current_user(
    token: str = Depends(oauth2_scheme_required),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    Raises 401 if token is invalid or user not found.
    
    Usage:
        @router.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            ...
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    token_data = decode_token(token)
    if token_data is None:
        raise credentials_exception
    
    # Verify it's an access token
    if token_data.type != "access":
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.email == token_data.sub).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get the current user if a valid token is provided, otherwise None.
    Useful for endpoints that work for both authenticated and anonymous users.
    
    Usage:
        @router.get("/public-or-private")
        async def route(user: Optional[User] = Depends(get_current_user_optional)):
            if user:
                # Authenticated user
            else:
                # Anonymous user
    """
    if token is None:
        return None
    
    token_data = decode_token(token)
    if token_data is None:
        return None
    
    if token_data.type != "access":
        return None
    
    user = db.query(User).filter(User.email == token_data.sub).first()
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current user and verify they are active.
    Raises 403 if user is inactive/disabled.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get the current user and verify they have admin privileges.
    Raises 403 if user is not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


def get_user_from_api_key(
    api_key: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get user from API key (alternative to JWT for programmatic access).
    
    Usage:
        @router.get("/api-access")
        async def api_route(
            api_key: str = Header(None, alias="X-API-Key"),
            db: Session = Depends(get_db)
        ):
            user = get_user_from_api_key(api_key, db)
            ...
    """
    if not api_key:
        return None
    
    user = db.query(User).filter(User.api_key == api_key).first()
    if user and user.is_active:
        return user
    
    return None
