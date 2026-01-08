"""
Task CRUD routes: list, create, update, complete, delete.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session
from typing import List, Optional
from pydantic import BaseModel

from models import Task
from middleware.auth import get_current_user, verify_user_access
from db import get_session
from utils.crud import TaskCRUD

router = APIRouter(prefix="", tags=["Tasks"])  # Prefix will be set by user_id


# Pydantic schemas for task operations
class TaskCreate(BaseModel):
    """Schema for creating a task."""
    title: str
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: int
    user_id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for task list response."""
    tasks: List[TaskResponse]


@router.get("/{user_id}/tasks", response_model=TaskListResponse)
async def list_tasks(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(verify_user_access),
    session: Session = Depends(get_session),
):
    """
    List all tasks for a user.

    Args:
        user_id: The user ID from the URL path
        skip: Number of tasks to skip (pagination)
        limit: Maximum number of tasks to return
        current_user: Authenticated user (verified by verify_user_access)
        session: Database session

    Returns:
        List of tasks
    """
    tasks = TaskCRUD.get_by_user(
        session=session,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )

    return TaskListResponse(
        tasks=[
            TaskResponse(
                id=task.id,
                user_id=task.user_id,
                title=task.title,
                description=task.description,
                completed=task.completed,
                created_at=task.created_at.isoformat(),
                updated_at=task.updated_at.isoformat(),
            )
            for task in tasks
        ]
    )


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: int,
    task_data: TaskCreate,
    current_user: dict = Depends(verify_user_access),
    session: Session = Depends(get_session),
):
    """
    Create a new task for a user.

    Args:
        user_id: The user ID from the URL path
        task_data: Task creation data
        current_user: Authenticated user
        session: Database session

    Returns:
        Created task
    """
    # Validate title
    if not task_data.title or len(task_data.title.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required",
        )

    if len(task_data.title) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must be 200 characters or less",
        )

    # Create task
    task = TaskCRUD.create(
        session=session,
        user_id=user_id,
        title=task_data.title.strip(),
        description=task_data.description.strip() if task_data.description else None,
    )

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
    )


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: int,
    task_id: int,
    current_user: dict = Depends(verify_user_access),
    session: Session = Depends(get_session),
):
    """
    Get a single task.

    Args:
        user_id: The user ID from the URL path
        task_id: The task ID from the URL path
        current_user: Authenticated user
        session: Database session

    Returns:
        Task details

    Raises:
        HTTPException: If task not found
    """
    task = TaskCRUD.get_by_id(session, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task",
        )

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
    )


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: int,
    task_id: int,
    task_data: TaskUpdate,
    current_user: dict = Depends(verify_user_access),
    session: Session = Depends(get_session),
):
    """
    Update a task.

    Args:
        user_id: The user ID from the URL path
        task_id: The task ID from the URL path
        task_data: Task update data
        current_user: Authenticated user
        session: Database session

    Returns:
        Updated task

    Raises:
        HTTPException: If task not found or validation fails
    """
    task = TaskCRUD.get_by_id(session, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this task",
        )

    # Update fields if provided
    if task_data.title is not None:
        if len(task_data.title.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title cannot be empty",
            )
        if len(task_data.title) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title must be 200 characters or less",
            )
        task.title = task_data.title.strip()

    if task_data.description is not None:
        task.description = task_data.description.strip() if task_data.description else None

    if task_data.completed is not None:
        task.completed = task_data.completed

    # Save task
    task = TaskCRUD.update(session, task)

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
    )


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_complete(
    user_id: int,
    task_id: int,
    current_user: dict = Depends(verify_user_access),
    session: Session = Depends(get_session),
):
    """
    Toggle task completion status.

    Args:
        user_id: The user ID from the URL path
        task_id: The task ID from the URL path
        current_user: Authenticated user
        session: Database session

    Returns:
        Updated task with toggled completion status

    Raises:
        HTTPException: If task not found
    """
    task = TaskCRUD.get_by_id(session, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this task",
        )

    # Toggle completion
    task = TaskCRUD.toggle_complete(session, task)

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
    )


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: int,
    task_id: int,
    current_user: dict = Depends(verify_user_access),
    session: Session = Depends(get_session),
):
    """
    Delete a task.

    Args:
        user_id: The user ID from the URL path
        task_id: The task ID from the URL path
        current_user: Authenticated user
        session: Database session

    Returns:
        No content (204)

    Raises:
        HTTPException: If task not found
    """
    task = TaskCRUD.get_by_id(session, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task",
        )

    TaskCRUD.delete(session, task_id)
    return None
