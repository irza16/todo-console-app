# REST API Generator Skill

## Purpose
Generate complete CRUD REST API endpoints for FastAPI from data model specifications with proper validation, error handling, and pagination.

## When to Use
- Creating CRUD endpoints for a new resource
- Need standardized API structure
- Want consistent error handling
- Building RESTful APIs quickly

## Prerequisites
- FastAPI project set up
- SQLModel models defined
- Database configured

## Instructions

### Step 1: Define Resource Pattern
For each resource (Task, User, etc.), create:
- **List** - GET /api/{user_id}/resources
- **Create** - POST /api/{user_id}/resources
- **Read** - GET /api/{user_id}/resources/{id}
- **Update** - PUT /api/{user_id}/resources/{id}
- **Delete** - DELETE /api/{user_id}/resources/{id}
- **Partial Update** - PATCH /api/{user_id}/resources/{id}

### Step 2: Create Base CRUD Template
`backend/utils/crud.py`:
```python
from typing import Generic, TypeVar, Type, Optional, List
from sqlmodel import SQLModel, Session, select
from fastapi import HTTPException, status

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(
        self,
        session: Session,
        id: int,
        user_id: Optional[str] = None
    ) -> Optional[ModelType]:
        """Get a single record by ID"""
        query = select(self.model).where(self.model.id == id)
        
        if user_id:
            query = query.where(self.model.user_id == user_id)
        
        return session.exec(query).first()
    
    def get_or_404(
        self,
        session: Session,
        id: int,
        user_id: Optional[str] = None
    ) -> ModelType:
        """Get record or raise 404"""
        obj = self.get(session, id, user_id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found"
            )
        return obj
    
    def get_multi(
        self,
        session: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination"""
        query = select(self.model).offset(skip).limit(limit)
        
        if user_id:
            query = query.where(self.model.user_id == user_id)
        
        return session.exec(query).all()
    
    def create(
        self,
        session: Session,
        obj_in: CreateSchemaType,
        user_id: Optional[str] = None
    ) -> ModelType:
        """Create a new record"""
        obj_data = obj_in.model_dump()
        
        if user_id:
            obj_data["user_id"] = user_id
        
        db_obj = self.model(**obj_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        session: Session,
        db_obj: ModelType,
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update an existing record"""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def delete(
        self,
        session: Session,
        id: int,
        user_id: Optional[str] = None
    ) -> None:
        """Delete a record"""
        obj = self.get_or_404(session, id, user_id)
        session.delete(obj)
        session.commit()
    
    def count(
        self,
        session: Session,
        user_id: Optional[str] = None
    ) -> int:
        """Count total records"""
        query = select(self.model)
        
        if user_id:
            query = query.where(self.model.user_id == user_id)
        
        return len(session.exec(query).all())
```

### Step 3: Create Resource-Specific CRUD
`backend/crud/task.py`:
```python
from utils.crud import CRUDBase
from models import Task, TaskCreate, TaskUpdate
from sqlmodel import Session, select
from typing import List

class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    def get_by_status(
        self,
        session: Session,
        user_id: str,
        completed: bool
    ) -> List[Task]:
        """Get tasks filtered by completion status"""
        query = select(Task).where(
            Task.user_id == user_id,
            Task.completed == completed
        )
        return session.exec(query).all()
    
    def toggle_complete(
        self,
        session: Session,
        task_id: int,
        user_id: str
    ) -> Task:
        """Toggle task completion status"""
        task = self.get_or_404(session, task_id, user_id)
        task.completed = not task.completed
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    
    def search(
        self,
        session: Session,
        user_id: str,
        query: str
    ) -> List[Task]:
        """Search tasks by title or description"""
        search_query = select(Task).where(
            Task.user_id == user_id,
            (Task.title.contains(query)) | (Task.description.contains(query))
        )
        return session.exec(search_query).all()

# Create instance
task_crud = CRUDTask(Task)
```

### Step 4: Create Complete API Routes
`backend/routes/tasks.py`:
```python
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session
from typing import List, Optional

from db import get_session
from models import Task, TaskCreate, TaskUpdate, TaskRead
from crud.task import task_crud
from middleware.auth import get_current_user, verify_user_access

router = APIRouter()

@router.get("/{user_id}/tasks", response_model=List[TaskRead])
async def list_tasks(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    completed: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List tasks with optional filtering and pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 100)
    - **completed**: Filter by completion status (optional)
    - **search**: Search in title and description (optional)
    """
    verify_user_access(user_id, current_user)
    
    if search:
        tasks = task_crud.search(session, user_id, search)
    elif completed is not None:
        tasks = task_crud.get_by_status(session, user_id, completed)
    else:
        tasks = task_crud.get_multi(session, skip, limit, user_id)
    
    return tasks

@router.post("/{user_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task: TaskCreate,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task.
    
    - **title**: Task title (required, 1-200 characters)
    - **description**: Task description (optional, max 1000 characters)
    """
    verify_user_access(user_id, current_user)
    return task_crud.create(session, task, user_id)

@router.get("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a specific task by ID"""
    verify_user_access(user_id, current_user)
    return task_crud.get_or_404(session, task_id, user_id)

@router.put("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    user_id: str,
    task_id: int,
    task_update: TaskUpdate,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a task (full update).
    
    All fields in TaskUpdate will be updated, even if set to null.
    """
    verify_user_access(user_id, current_user)
    db_task = task_crud.get_or_404(session, task_id, user_id)
    return task_crud.update(session, db_task, task_update)

@router.patch("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def partial_update_task(
    user_id: str,
    task_id: int,
    task_update: TaskUpdate,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Partially update a task.
    
    Only provided fields will be updated, others remain unchanged.
    """
    verify_user_access(user_id, current_user)
    db_task = task_crud.get_or_404(session, task_id, user_id)
    return task_crud.update(session, db_task, task_update)

@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a task"""
    verify_user_access(user_id, current_user)
    task_crud.delete(session, task_id, user_id)

@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskRead)
async def toggle_task_complete(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Toggle task completion status"""
    verify_user_access(user_id, current_user)
    return task_crud.toggle_complete(session, task_id, user_id)

@router.get("/{user_id}/tasks/stats/summary")
async def get_task_stats(
    user_id: str,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get task statistics for user"""
    verify_user_access(user_id, current_user)
    
    total = task_crud.count(session, user_id)
    completed = len(task_crud.get_by_status(session, user_id, True))
    pending = len(task_crud.get_by_status(session, user_id, False))
    
    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "completion_rate": (completed / total * 100) if total > 0 else 0
    }
```

### Step 5: Add Pagination Response Model
`backend/models.py` (add pagination):
```python
from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic pagination response"""
    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        skip: int,
        limit: int
    ):
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(items)) < total
        )
```

Use in routes:
```python
@router.get("/{user_id}/tasks", response_model=PaginatedResponse[TaskRead])
async def list_tasks_paginated(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    verify_user_access(user_id, current_user)
    
    tasks = task_crud.get_multi(session, skip, limit, user_id)
    total = task_crud.count(session, user_id)
    
    return PaginatedResponse.create(tasks, total, skip, limit)
```

### Step 6: Add Bulk Operations
```python
@router.post("/{user_id}/tasks/bulk", response_model=List[TaskRead])
async def bulk_create_tasks(
    user_id: str,
    tasks: List[TaskCreate],
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create multiple tasks at once"""
    verify_user_access(user_id, current_user)
    
    created_tasks = []
    for task in tasks:
        created_task = task_crud.create(session, task, user_id)
        created_tasks.append(created_task)
    
    return created_tasks

@router.delete("/{user_id}/tasks/bulk")
async def bulk_delete_tasks(
    user_id: str,
    task_ids: List[int],
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete multiple tasks at once"""
    verify_user_access(user_id, current_user)
    
    for task_id in task_ids:
        task_crud.delete(session, task_id, user_id)
    
    return {"deleted": len(task_ids)}
```

## API Documentation
FastAPI auto-generates docs at `/docs`. Enhance with:

```python
@router.get(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskRead,
    summary="Get Task by ID",
    description="Retrieve a specific task by its ID. User must be authenticated and own the task.",
    responses={
        200: {"description": "Task found"},
        404: {"description": "Task not found"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"}
    }
)
async def get_task(...):
    ...
```

## Validation Checklist
- [ ] CRUD base class created
- [ ] Resource-specific CRUD created
- [ ] All 6 standard endpoints implemented
- [ ] Pagination working
- [ ] Filtering working
- [ ] Search working
- [ ] Bulk operations working
- [ ] Error responses correct (404, 401, 403)
- [ ] API docs generated at /docs

## Testing Endpoints

### Create Task
```bash
curl -X POST http://localhost:8000/api/user123/tasks \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"New Task","description":"Description"}'
```

### List Tasks
```bash
curl "http://localhost:8000/api/user123/tasks?skip=0&limit=10&completed=false" \
  -H "Authorization: Bearer TOKEN"
```

### Get Task
```bash
curl http://localhost:8000/api/user123/tasks/1 \
  -H "Authorization: Bearer TOKEN"
```

### Update Task
```bash
curl -X PATCH http://localhost:8000/api/user123/tasks/1 \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Title"}'
```

### Delete Task
```bash
curl -X DELETE http://localhost:8000/api/user123/tasks/1 \
  -H "Authorization: Bearer TOKEN"
```

## Output Files
- `utils/crud.py` - Base CRUD class
- `crud/task.py` - Task-specific CRUD
- `routes/tasks.py` - Complete API routes
- Updated `models.py` with pagination

## Next Steps
After REST API:
1. Test all endpoints with Postman/Thunder Client
2. Add rate limiting
3. Add request validation
4. Implement caching
5. Add API versioning