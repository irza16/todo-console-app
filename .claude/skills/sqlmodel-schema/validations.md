# SQLModel Validations

## Pydantic Validators
For complex validations, use Pydantic validators:

```python
from sqlmodel import SQLModel, Field
from pydantic import field_validator
from datetime import datetime

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    due_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @field_validator('due_date')
    @classmethod
    def due_date_must_be_future(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v and v < datetime.utcnow():
            raise ValueError('Due date must be in the future')
        return v
```

## Pydantic Schemas
For API request/response:

```python
# Request Schemas (without ID, timestamps)
class TaskCreate(SQLModel):
    """Schema for creating a task"""
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=1000)

class TaskUpdate(SQLModel):
    """Schema for updating a task"""
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = Field(default=None)

# Response Schema (with all fields)
class TaskRead(SQLModel):
    """Schema for reading a task"""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: Optional[datetime]
```

## Common Patterns

### Auto-updating Timestamps
```python
from datetime import datetime
from sqlmodel import Field, SQLModel
from typing import Optional

class BaseModel(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
```

### Soft Delete Pattern
```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = Field(default=None)
```

## Validation Checklist
- [ ] All models inherit from `SQLModel` with `table=True`
- [ ] Primary keys defined correctly
- [ ] Required fields don't have `Optional` type
- [ ] Timestamps use `datetime.utcnow` default
- [ ] String fields have max_length constraints
- [ ] Create/Update/Read schemas defined

## Testing Models
```python
# Test model creation
from models import Task
from datetime import datetime

task = Task(
    user_id="user123",
    title="Test Task",
    description="Test Description"
)

print(task.model_dump())  # Validate model structure
```
