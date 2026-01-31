"""
SQLModel database models for User, Task, Conversation, and Message entities.
"""
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import pydantic


class User(SQLModel, table=True):
    """User model for authentication and task ownership."""
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=100)
    password_hash: str

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="user")

    class Config:
        from_attributes = True


class Task(SQLModel, table=True):
    """Task model for todo items."""
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to user
    user: Optional[User] = Relationship(back_populates="tasks")

    class Config:
        from_attributes = True


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    """Conversation model for chat history."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)  # For user isolation queries
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)  # For chronological ordering
    updated_at: Optional[datetime] = Field(default=None)

    # Relationship to messages
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    """Message model for storing chat messages."""
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)  # For conversation history retrieval
    role: str = Field(max_length=20, index=True)  # "user" or "assistant" - for filtering by role
    content: str = Field(max_length=10000)
    tool_calls: Optional[str] = Field(default=None)  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)  # For chronological ordering

    # Relationship to conversation
    conversation: Conversation = Relationship(back_populates="messages")


# Pydantic schemas for request/response
class UserCreate(SQLModel):
    """Schema for user registration."""
    email: str
    name: str
    password: str  # Plain password, will be hashed


class LoginRequest(SQLModel):
    """Schema for user login."""
    email: str
    password: str


class UserResponse(SQLModel):
    """Schema for user response (without password)."""
    id: int
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(SQLModel):
    """Schema for authentication response with token."""
    user: UserResponse
    token: str


class TokenData(SQLModel):
    """JWT token payload data."""
    user_id: int
    email: Optional[str] = None
    exp: Optional[datetime] = None
