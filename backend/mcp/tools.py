"""
MCP Tools for AI-powered Todo Chatbot
Implements the 5 required MCP tools: add_task, list_tasks, complete_task, update_task, delete_task
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from models import Task, Conversation, Message, User
from db import engine


class AddTaskArguments(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "Medium"  # Options: Low, Medium, High, Urgent
    tags: Optional[str] = None  # Comma-separated string of tags
    is_recurring: Optional[bool] = False  # Whether the task repeats
    recurrence_pattern: Optional[str] = None  # Options: daily, weekly, monthly, weekdays (only if is_recurring is True)


class ListTasksArguments(BaseModel):
    status: Optional[str] = "all"  # "all", "pending", "completed"


class CompleteTaskArguments(BaseModel):
    task_id: int


class UpdateTaskArguments(BaseModel):
    task_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None  # Options: Low, Medium, High, Urgent
    tags: Optional[str] = None  # Comma-separated string of tags
    is_recurring: Optional[bool] = None  # Whether the task repeats
    recurrence_pattern: Optional[str] = None  # Options: daily, weekly, monthly, weekdays (only if is_recurring is True)


class DeleteTaskArguments(BaseModel):
    task_id: int


def add_task(args: AddTaskArguments, user_id: str) -> Dict[str, Any]:
    """
    Add a new task for a user
    """
    with Session(engine) as session:
        # Validate user exists and get user_id as integer
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise ValueError(f"Invalid user_id: {user_id}")

        # Verify the user exists
        user = session.get(User, user_id_int)
        if not user:
            raise PermissionError(f"User with id {user_id_int} does not exist")

        # Validate the title is meaningful (not random characters, placeholders, etc.)
        title = args.title.strip().lower()

        # Check for meaningless/random titles
        meaningless_patterns = [
            r'^[a-z]{8,}$',  # Long sequences of random letters
            r'^[a-zA-Z]{10,}$',  # Very long random letter combinations
            r'^\s*$',  # Empty or whitespace only
            r'^(ok|okay|yes|no|abc|xyz|test|task|item|thing|stuff|random|placeholder|sample|demo)\s*$',  # Common meaningless words
            r'^(add|create|new)\s+(task|item|todo)\s*$',  # Generic phrases
            r'^(ok ok|xyz xyz|abc abc)$',  # Repeated meaningless words
        ]

        import re
        for pattern in meaningless_patterns:
            if re.match(pattern, title):
                raise ValueError(f"Task title '{args.title}' is not meaningful. Please provide a specific task title.")

        # Validate recurrence_pattern if provided
        if args.recurrence_pattern and not args.is_recurring:
            raise ValueError("Recurrence pattern can only be set when is_recurring is true")

        # Validate recurrence pattern value if provided
        if args.recurrence_pattern and args.is_recurring:
            valid_recurrence_patterns = ["daily", "weekly", "monthly", "weekdays"]
            if args.recurrence_pattern not in valid_recurrence_patterns:
                raise ValueError(f"Invalid recurrence pattern: {args.recurrence_pattern}. Must be one of: {', '.join(valid_recurrence_patterns)}")

        # Validate priority value if provided
        if args.priority:
            valid_priorities = ["Low", "Medium", "High", "Urgent"]
            if args.priority not in valid_priorities:
                raise ValueError(f"Invalid priority: {args.priority}. Must be one of: {', '.join(valid_priorities)}")

        task = Task(
            user_id=user_id_int,
            title=args.title,
            description=args.description,
            priority=args.priority,
            tags=args.tags,
            is_recurring=args.is_recurring,
            recurrence_pattern=args.recurrence_pattern,
            completed=False
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title
        }


def list_tasks(args: ListTasksArguments, user_id: str) -> List[Dict[str, Any]]:
    """
    List tasks for a user with optional status filtering
    """
    with Session(engine) as session:
        # Validate user exists and get user_id as integer
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise ValueError(f"Invalid user_id: {user_id}")

        # Verify the user exists
        user = session.get(User, user_id_int)
        if not user:
            raise PermissionError(f"User with id {user_id_int} does not exist")

        query = select(Task).where(Task.user_id == user_id_int)

        if args.status == "pending":
            query = query.where(Task.completed == False)
        elif args.status == "completed":
            query = query.where(Task.completed == True)

        tasks = session.exec(query).all()

        return [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "tags": task.tags,
                "is_recurring": task.is_recurring,
                "recurrence_pattern": task.recurrence_pattern
            }
            for task in tasks
        ]


def complete_task(args: CompleteTaskArguments, user_id: str) -> Dict[str, Any]:
    """
    Mark a task as completed
    """
    with Session(engine) as session:
        # Validate user exists and get user_id as integer
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise ValueError(f"Invalid user_id: {user_id}")

        # Verify the user exists
        user = session.get(User, user_id_int)
        if not user:
            raise PermissionError(f"User with id {user_id_int} does not exist")

        task = session.get(Task, args.task_id)

        if not task:
            raise ValueError(f"Task with id {args.task_id} not found")

        if task.user_id != user_id_int:
            raise PermissionError("User does not have permission to modify this task")

        task.completed = True
        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title
        }


def update_task(args: UpdateTaskArguments, user_id: str) -> Dict[str, Any]:
    """
    Update task title or description
    """
    with Session(engine) as session:
        # Validate user exists and get user_id as integer
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise ValueError(f"Invalid user_id: {user_id}")

        # Verify the user exists
        user = session.get(User, user_id_int)
        if not user:
            raise PermissionError(f"User with id {user_id_int} does not exist")

        task = session.get(Task, args.task_id)

        if not task:
            raise ValueError(f"Task with id {args.task_id} not found")

        if task.user_id != user_id_int:
            raise PermissionError("User does not have permission to modify this task")

        if args.title is not None:
            task.title = args.title
        if args.description is not None:
            task.description = args.description
        if args.priority is not None:
            # Validate priority value
            valid_priorities = ["Low", "Medium", "High", "Urgent"]
            if args.priority not in valid_priorities:
                raise ValueError(f"Invalid priority: {args.priority}. Must be one of: {', '.join(valid_priorities)}")
            task.priority = args.priority
        if args.tags is not None:
            task.tags = args.tags
        if args.is_recurring is not None:
            task.is_recurring = args.is_recurring
        if args.recurrence_pattern is not None:
            # Validate recurrence_pattern if provided
            if not args.is_recurring:
                raise ValueError("Recurrence pattern can only be set when is_recurring is true")

            # Validate recurrence pattern value
            valid_recurrence_patterns = ["daily", "weekly", "monthly", "weekdays"]
            if args.recurrence_pattern not in valid_recurrence_patterns:
                raise ValueError(f"Invalid recurrence pattern: {args.recurrence_pattern}. Must be one of: {', '.join(valid_recurrence_patterns)}")

            task.recurrence_pattern = args.recurrence_pattern

        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "task_id": task.id,
            "status": "updated",
            "title": task.title,
            "priority": task.priority,
            "tags": task.tags,
            "is_recurring": task.is_recurring,
            "recurrence_pattern": task.recurrence_pattern
        }


def delete_task(args: DeleteTaskArguments, user_id: str) -> Dict[str, Any]:
    """
    Delete a task
    """
    with Session(engine) as session:
        # Validate user exists and get user_id as integer
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise ValueError(f"Invalid user_id: {user_id}")

        # Verify the user exists
        user = session.get(User, user_id_int)
        if not user:
            raise PermissionError(f"User with id {user_id_int} does not exist")

        task = session.get(Task, args.task_id)

        if not task:
            raise ValueError(f"Task with id {args.task_id} not found")

        if task.user_id != user_id_int:
            raise PermissionError("User does not have permission to delete this task")

        session.delete(task)
        session.commit()

        return {
            "task_id": args.task_id,
            "status": "deleted",
            "title": task.title
        }