"""
JWT token encoding and decoding utilities using python-jose.
"""
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional

from config import settings


def create_access_token(user_id: int, email: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token for the user.

    Args:
        user_id: The user's ID to encode in the token
        email: The user's email to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT access token.

    Args:
        token: The JWT token string to decode

    Returns:
        Decoded token payload dict or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


def extract_user_id_from_token(token: str) -> Optional[int]:
    """
    Extract user_id from a JWT token.

    Args:
        token: The JWT token string

    Returns:
        User ID or None if token is invalid
    """
    payload = decode_access_token(token)
    if payload:
        user_id = payload.get("sub")
        if user_id:
            return int(user_id)
    return None


def verify_token(token: str) -> bool:
    """
    Verify if a JWT token is valid.

    Args:
        token: The JWT token string

    Returns:
        True if valid, False otherwise
    """
    payload = decode_access_token(token)
    return payload is not None
