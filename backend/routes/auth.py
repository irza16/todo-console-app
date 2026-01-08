"""
Authentication routes: signup, login, and user info.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session
from pydantic import EmailStr, constr

from models import User, UserCreate, LoginRequest, UserResponse, AuthResponse
from utils.password import hash_password, verify_password
from utils.jwt import create_access_token
from utils.crud import UserCRUD
from db import get_session
from middleware.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    session: Session = Depends(get_session),
):
    """
    Register a new user.

    Args:
        user_data: User registration data (email, name, password)
        session: Database session

    Returns:
        AuthResponse with user info and JWT token

    Raises:
        HTTPException: If email already exists or validation fails
    """
    # Check if email already exists
    existing_user = UserCRUD.get_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Validate password length
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )

    # Email validation is handled by Pydantic in UserCreate model

    # Hash password and create user
    password_hash = hash_password(user_data.password)
    user = UserCRUD.create(
        session=session,
        email=user_data.email,
        name=user_data.name,
        password_hash=password_hash,
    )

    # Generate JWT token
    token = create_access_token(user_id=user.id, email=user.email)

    # Return response
    return AuthResponse(
        user=UserResponse.model_validate(user),
        token=token,
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: LoginRequest,
    session: Session = Depends(get_session),
):
    """
    Login with email and password.

    Args:
        credentials: Login credentials (email, password)
        session: Database session

    Returns:
        AuthResponse with user info and JWT token

    Raises:
        HTTPException: If credentials are invalid
    """
    # Get user by email
    user = UserCRUD.get_by_email(session, credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate JWT token
    token = create_access_token(user_id=user.id, email=user.email)

    # Return response
    return AuthResponse(
        user=UserResponse.model_validate(user),
        token=token,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
):
    """
    Get current authenticated user info.

    Args:
        current_user: Current user from JWT token

    Returns:
        User info
    """
    return UserResponse(**current_user)
