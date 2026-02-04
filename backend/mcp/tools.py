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


class ListTasksArguments(BaseModel):
    status: Optional[str] = "all"  # "all", "pending", "completed"


class CompleteTaskArguments(BaseModel):
    task_id: int


class UpdateTaskArguments(BaseModel):
    task_id: int
    title: Optional[str] = None
    description: Optional[str] = None


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

        task = Task(
            user_id=user_id_int,
            title=args.title,
            description=args.description,
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
                "completed": task.completed
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

        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "task_id": task.id,
            "status": "updated",
            "title": task.title
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