# Data Model: Full-Stack Todo Web Application

## Overview

This document defines the data model for the multi-user todo application. The model consists of two primary entities: User and Task, with a one-to-many relationship (one user has many tasks).

## Entities

### User

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | integer | Primary Key, Auto-increment | Unique user identifier |
| email | string | Unique, Not Null, Email format | User's email address (unique across all users) |
| name | string | Not Null, Max 100 chars | User's display name |
| password_hash | string | Not Null | Bcrypt/Argon2 hashed password (never store plain text) |
| created_at | datetime | Not Null, Default: now() | Account creation timestamp |
| updated_at | datetime | Not Null, Default: now() | Last update timestamp |

### Task

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | integer | Primary Key, Auto-increment | Unique task identifier |
| user_id | integer | Foreign Key (users.id), Not Null, Indexed | Owning user's ID |
| title | string | Not Null, Max 200 chars | Task title (required) |
| description | string | Max 1000 chars | Optional task description |
| completed | boolean | Not Null, Default: false | Completion status |
| created_at | datetime | Not Null, Default: now() | Task creation timestamp |
| updated_at | datetime | Not Null, Default: now() | Last update timestamp |

## Relationships

```
User (1) ──────> (N) Task
  id  ---------------->  user_id
```

- Each Task belongs to exactly one User
- Each User can have zero or more Tasks
- Deleting a User should cascade to delete all their Tasks

## Validation Rules

### User Validation (Pydantic)

```python
# Signup Request
{
    "email": "user@example.com",           # Valid email format required
    "password": "securepassword123",       # Min 8 characters
    "name": "John Doe"                     # Non-empty, max 100 chars
}

# Login Request
{
    "email": "user@example.com",           # Must match registered email
    "password": "securepassword123"        # Must match registered password
}
```

### Task Validation (Pydantic)

```python
# Create Task Request
{
    "title": "Buy groceries",              # Required, 1-200 chars
    "description": "Milk, bread, eggs"     # Optional, 0-1000 chars
}

# Update Task Request (all fields optional)
{
    "title": "Buy groceries and snacks",   # 1-200 chars if provided
    "description": "Milk, bread, eggs, chips",  # 0-1000 chars if provided
    "completed": true                      # Boolean if provided
}
```

## API Schemas

### Response Schemas

```python
# User Response (login/signup response)
{
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
}

# Auth Response (login/signup with token)
{
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "John Doe"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# Task Response
{
    "id": 1,
    "user_id": 1,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "completed": false,
    "created_at": "2025-12-14T10:30:00Z",
    "updated_at": "2025-12-14T10:30:00Z"
}

# Task List Response
{
    "tasks": [
        {
            "id": 1,
            "user_id": 1,
            "title": "Buy groceries",
            "description": "Milk, bread, eggs",
            "completed": false,
            "created_at": "2025-12-14T10:30:00Z",
            "updated_at": "2025-12-14T10:30:00Z"
        }
    ]
}
```

## User Isolation

All task queries MUST include a WHERE clause filtering by the authenticated user's ID:

```sql
-- List tasks for user
SELECT * FROM tasks WHERE user_id = :current_user_id

-- Get single task (with ownership check)
SELECT * FROM tasks WHERE id = :task_id AND user_id = :current_user_id

-- Update task (with ownership check)
UPDATE tasks SET title = :title WHERE id = :task_id AND user_id = :current_user_id

-- Delete task (with ownership check)
DELETE FROM tasks WHERE id = :task_id AND user_id = :current_user_id
```

## Database Indexes

| Index | Columns | Purpose |
|-------|---------|---------|
| idx_users_email | email | Fast email lookups for login/signup |
| idx_tasks_user_id | user_id | Fast task queries filtered by user |
| idx_tasks_user_completed | user_id, completed | Filter tasks by user and completion status |

## Error Schemas

```python
# Validation Error (400)
{
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "value is not a valid email address",
            "type": "value_error.email"
        }
    ]
}

# Authentication Error (401)
{
    "detail": "Invalid authentication credentials"
}

# Forbidden Error (403)
{
    "detail": "Not authorized to access this resource"
}

# Not Found Error (404)
{
    "detail": "Task not found"
}
```
