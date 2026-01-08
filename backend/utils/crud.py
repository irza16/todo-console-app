"""
Base CRUD utility functions for database operations.
"""
from typing import TypeVar, Type, Optional, List, Generic
from sqlmodel import SQLModel, Session, select, delete
from models import User, Task

T = TypeVar("T", bound=SQLModel)


class CRUDError(Exception):
    """Custom exception for CRUD operations."""
    pass


class NotFoundError(CRUDError):
    """Raised when a resource is not found."""
    pass


class UserCRUD:
    """CRUD operations for User model."""

    @staticmethod
    def get_by_id(session: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return session.get(User, user_id)

    @staticmethod
    def get_by_email(session: Session, email: str) -> Optional[User]:
        """Get user by email."""
        statement = select(User).where(User.email == email)
        result = session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    def create(session: Session, email: str, name: str, password_hash: str) -> User:
        """Create a new user."""
        user = User(email=email, name=name, password_hash=password_hash)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    @staticmethod
    def update(session: Session, user: User) -> User:
        """Update a user."""
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


class TaskCRUD:
    """CRUD operations for Task model."""

    @staticmethod
    def get_by_id(session: Session, task_id: int) -> Optional[Task]:
        """Get task by ID."""
        return session.get(Task, task_id)

    @staticmethod
    def get_by_user(session: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks for a user."""
        statement = (
            select(Task)
            .where(Task.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        result = session.execute(statement)
        return result.scalars().all()

    @staticmethod
    def create(session: Session, user_id: int, title: str, description: Optional[str] = None) -> Task:
        """Create a new task for a user."""
        task = Task(user_id=user_id, title=title, description=description)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def update(session: Session, task: Task) -> Task:
        """Update a task."""
        from datetime import datetime
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def delete(session: Session, task_id: int) -> bool:
        """Delete a task by ID."""
        task = session.get(Task, task_id)
        if task:
            session.delete(task)
            session.commit()
            return True
        return False

    @staticmethod
    def toggle_complete(session: Session, task: Task) -> Task:
        """Toggle task completion status."""
        from datetime import datetime
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
