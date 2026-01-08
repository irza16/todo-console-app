# SQLModel Models

## Create Models File
Create `backend/models.py`:

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    """User model for authentication"""
    __tablename__ = "users"

    # Primary Key
    id: str = Field(primary_key=True)

    # Required Fields
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    """Task model for todo items"""
    __tablename__ = "tasks"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Key
    user_id: str = Field(foreign_key="users.id", index=True)

    # Required Fields
    title: str = Field(max_length=200, min_length=1)

    # Optional Fields
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: User = Relationship(back_populates="tasks")
```

## Initialize Database
Update `backend/db.py`:

```python
from sqlmodel import SQLModel, create_engine
from models import User, Task  # Import all models

# Create tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

## Field Type Reference

| Spec Type | SQLModel Type | Example |
|-----------|---------------|---------|
| String | `str` | `Field(max_length=255)` |
| Integer | `int` | `Field(ge=0)` (greater than or equal) |
| Boolean | `bool` | `Field(default=False)` |
| DateTime | `datetime` | `Field(default_factory=datetime.utcnow)` |
| Optional String | `Optional[str]` | `Field(default=None)` |
| Email | `str` | `Field(regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')` |
| UUID | `str` | `Field(primary_key=True)` |

## Basic Model Template
```python
class ModelName(SQLModel, table=True):
    __tablename__ = "table_name"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Required Fields
    field_name: FieldType = Field(constraints...)

    # Optional Fields
    optional_field: Optional[FieldType] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
```

## Add Indexes
For frequently queried fields:

```python
from sqlmodel import Field, Index

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    __table_args__ = (
        Index('idx_user_completed', 'user_id', 'completed'),
        Index('idx_user_created', 'user_id', 'created_at'),
    )

    # ... fields ...
```
