# Data Model: AI-Powered Todo Chatbot with MCP Architecture

## Entity: Conversation

### Attributes
- **id**: Integer (Primary Key, Auto-generated)
  - Purpose: Unique identifier for each conversation
  - Constraints: Non-null, Unique, Auto-incrementing
- **user_id**: String (Foreign Key to users.id)
  - Purpose: Links conversation to specific user
  - Constraints: Non-null, Indexed, References users table
- **created_at**: DateTime (Timestamp)
  - Purpose: When conversation was initiated
  - Constraints: Non-null, Default: Current timestamp
- **updated_at**: DateTime (Timestamp)
  - Purpose: Last time conversation was updated
  - Constraints: Nullable, Updates on conversation activity

### Relationships
- **One-to-Many**: With Message entity (conversation.messages)
  - Through: messages.conversation_id → conversations.id
  - Cascade: Delete messages when conversation is deleted

### Validation Rules
- user_id must correspond to an existing user in the users table
- created_at cannot be in the future
- updated_at must be equal to or later than created_at

## Entity: Message

### Attributes
- **id**: Integer (Primary Key, Auto-generated)
  - Purpose: Unique identifier for each message
  - Constraints: Non-null, Unique, Auto-incrementing
- **conversation_id**: Integer (Foreign Key to conversations.id)
  - Purpose: Links message to specific conversation
  - Constraints: Non-null, Indexed, References conversations table
- **role**: String (Enum: "user" | "assistant")
  - Purpose: Indicates if message is from user or AI assistant
  - Constraints: Non-null, Length: 20 characters max, Values: "user", "assistant"
- **content**: String
  - Purpose: The actual text content of the message
  - Constraints: Non-null, Length: 10000 characters max
- **tool_calls**: JSON String (Optional)
  - Purpose: Stores information about MCP tools called during message processing
  - Constraints: Nullable, JSON format validation
- **created_at**: DateTime (Timestamp)
  - Purpose: When message was created
  - Constraints: Non-null, Default: Current timestamp

### Relationships
- **Many-to-One**: With Conversation entity (message.conversation)
  - Through: messages.conversation_id → conversations.id
  - Behavior: Messages deleted when conversation is deleted

### Validation Rules
- conversation_id must correspond to an existing conversation
- role must be either "user" or "assistant"
- content length must not exceed 10,000 characters
- tool_calls must be valid JSON when present
- created_at cannot be in the future

## Entity: Task (Existing, Extended)

### Attributes (Existing)
- **id**: Integer (Primary Key, Auto-generated)
  - Purpose: Unique identifier for each task
- **user_id**: Integer (Foreign Key to users.id)
  - Purpose: Links task to specific user
- **title**: String
  - Purpose: Brief description of the task
- **description**: String (Optional)
  - Purpose: Detailed information about the task
- **completed**: Boolean
  - Purpose: Whether the task is completed
- **created_at**: DateTime
  - Purpose: When task was created
- **updated_at**: DateTime
  - Purpose: When task was last updated

### MCP Tool Integration Points
- **add_task**: Creates new Task record
- **list_tasks**: Queries Task records by user_id and status
- **complete_task**: Updates completed field on Task record
- **update_task**: Modifies title/description on Task record
- **delete_task**: Removes Task record

### Validation Rules (Extended)
- All existing validations remain
- MCP tools must verify user_id matches authenticated user

## Entity: User (Existing)

### Attributes (Existing)
- **id**: Integer (Primary Key, Auto-generated)
  - Purpose: Unique identifier for each user
- **email**: String
  - Purpose: User's email address
- **password_hash**: String
  - Purpose: Hashed password for authentication

### Relationships (Extended)
- **One-to-Many**: With Conversation entity (user.conversations)
  - Through: conversations.user_id → users.id
- **One-to-Many**: With Task entity (user.tasks)
  - Through: tasks.user_id → users.id

### MCP Tool Integration Points
- All MCP tools receive user_id parameter
- MCP tools must verify user_id matches authenticated user
- User isolation enforced at database and application levels

## Database Schema Implementation

### SQLModel Definitions

```python
from sqlmodel import SQLModel, Field, Relationship, create_engine
from typing import List, Optional
from datetime import datetime

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # References users table
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationship to messages
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str = Field(max_length=10000)
    tool_calls: Optional[str] = Field(default=None)  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to conversation
    conversation: Conversation = Relationship(back_populates="messages")

# Task and User models remain as defined in existing models.py
# with additional validation for MCP tool access
```

## Indexes and Performance Considerations

### Required Indexes
1. conversations.user_id (for user isolation queries)
2. conversations.created_at (for chronological ordering)
3. messages.conversation_id (for conversation history retrieval)
4. messages.created_at (for chronological ordering within conversations)
5. tasks.user_id (for user isolation in task operations)

### Query Patterns
1. Fetch conversation history: ORDER BY messages.created_at ASC
2. User's conversations: WHERE conversations.user_id = :user_id
3. Task operations: WHERE tasks.user_id = :user_id
4. Status filtering: WHERE tasks.completed = :status

## Data Integrity Constraints

### Referential Integrity
- conversations.user_id → users.id (foreign key constraint)
- messages.conversation_id → conversations.id (foreign key constraint)
- tasks.user_id → users.id (foreign key constraint)

### Data Validation
- All user access restricted by user_id matching
- Conversation history maintained in chronological order
- Message content sanitized before storage
- Tool calls validated as proper JSON format

## Migration Requirements

### New Tables
1. conversations table with specified schema
2. messages table with specified schema

### Index Creation
1. Index on conversations.user_id
2. Index on conversations.created_at
3. Index on messages.conversation_id
4. Index on messages.created_at

### Permissions
1. MCP tools can only access data for authenticated user_id
2. Conversation history access restricted by user_id
3. Message access restricted by conversation ownership