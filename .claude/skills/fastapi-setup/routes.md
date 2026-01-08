# FastAPI Routes

## Route Template
`backend/routes/tasks.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from db import get_session
from models import Task, TaskCreate, TaskRead, TaskUpdate

router = APIRouter()

@router.get("/tasks", response_model=List[TaskRead])
async def list_tasks(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """List all tasks with pagination"""
    tasks = session.exec(
        select(Task).offset(skip).limit(limit)
    ).all()
    return tasks

@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    session: Session = Depends(get_session)
):
    """Create a new task"""
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific task by ID"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.put("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    """Update a task"""
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: Session = Depends(get_session)
):
    """Delete a task"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    session.delete(task)
    session.commit()
    return None
```

## Include Routers
In `backend/main.py`:

```python
from routes import tasks, auth

app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
```

## Route Best Practices
- Use descriptive endpoint names
- Include proper HTTP status codes
- Use response models for type safety
- Implement pagination for list endpoints
- Handle 404 errors appropriately
- Use dependency injection for database sessions
- Include docstrings for API documentation
