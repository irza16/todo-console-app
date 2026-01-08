"""
JWT authentication middleware for FastAPI.
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from typing import Optional

from utils.jwt import extract_user_id_from_token, verify_token
from utils.crud import UserCRUD
from db import get_session

security = HTTPBearer()


class AuthError(HTTPException):
    """Custom authentication error."""
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> dict:
    """
    Get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token credentials
        session: Database session

    Returns:
        User data dict with id, email, name

    Raises:
        AuthError: If token is invalid or user not found
    """
    token = credentials.credentials

    # Verify token is valid
    if not verify_token(token):
        raise AuthError("Invalid or expired token")

    # Extract user_id from token
    user_id = extract_user_id_from_token(token)
    if not user_id:
        raise AuthError("Could not extract user ID from token")

    # Get user from database
    user = UserCRUD.get_by_id(session, user_id)
    if not user:
        raise AuthError("User not found")

    # Return user data (excluding password)
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
    }


async def verify_user_access(
    user_id: int,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Verify that the current user has access to the specified user_id.

    This enforces user data isolation at the API level.

    Args:
        user_id: The user ID from the URL path
        current_user: The authenticated user from JWT

    Returns:
        The current user if access is verified

    Raises:
        AuthError: If user_id doesn't match authenticated user
    """
    if current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource",
        )
    return current_user


def get_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """
    Extract JWT token from Authorization header.

    Args:
        authorization: Authorization header value

    Returns:
        Token string or None
    """
    if not authorization:
        return None

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]
