# Data Model: Todo Console App - Phase I

## Task Entity

Represents a single todo item stored in the in-memory task list.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | integer | > 0, unique, auto-increment | Unique identifier, never reused after deletion |
| `title` | string | 1-200 characters, required | Brief task description |
| `description` | string | 0-1000 characters, optional | Detailed task information |
| `completed` | boolean | default: `False` | Task completion status |

### Example Instance

```python
{
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread, butter",
    "completed": False
}
```

## Task List Entity

A collection of Task entities stored as a Python list.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `tasks` | `list[dict]` | Ordered list of task dictionaries |
| `next_id` | `int` | Counter for assigning new task IDs (starts at 1) |

### Example Instance

```python
tasks = [
    {
        "id": 1,
        "title": "Buy groceries",
        "description": "Milk, eggs, bread, butter",
        "completed": False
    },
    {
        "id": 2,
        "title": "Call mom",
        "description": "",
        "completed": True
    }
]
next_id = 3  # Next task will get ID 3
```

## Validation Rules

### Title Validation

- Minimum length: 1 character (after stripping whitespace)
- Maximum length: 200 characters
- Required: Yes (empty title rejected)
- Whitespace handling: Stripped from ends, internal spaces preserved

### Description Validation

- Minimum length: 0 characters (optional field)
- Maximum length: 1000 characters
- Required: No (empty string allowed)
- Whitespace handling: Stripped from ends

### ID Validation

- Must be a positive integer
- Must exist in the task list for operations (update, delete, toggle)
- Non-numeric input rejected
- Out-of-range IDs rejected with error message

## State Transitions

### Task Completion Status

```
[Pending] <-- toggle_complete() --> [Completed]
     |                              |
     | (new task starts here)       |
     --------------------------------
```

### Task Lifecycle

```
Created (id assigned, completed=False)
    |
    +-- view_tasks() --> Displayed in list
    |
    +-- update_task() --> Modified (title/description)
    |
    +-- toggle_complete() --> Completed=True
    |
    +-- toggle_complete() --> Completed=False
    |
    +-- delete_task() --> Removed from list
```

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `MAX_TITLE_LENGTH` | 200 | Maximum characters in task title |
| `MAX_DESCRIPTION_LENGTH` | 1000 | Maximum characters in task description |
| `MIN_ID` | 1 | Minimum valid task ID |
| `MENU_OPTIONS` | 6 | Number of menu options (1-6) |
