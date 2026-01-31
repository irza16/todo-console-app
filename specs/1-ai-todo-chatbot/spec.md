# Conversational AI Todo Assistant Specification

## Feature Overview

A conversational AI assistant that allows users to manage their todo tasks through natural language interactions. The feature integrates with the existing todo application to provide an alternative interface using OpenAI's ChatKit (with Groq API backend) and MCP (Model Context Protocol) architecture.

## Business Context

Modern users increasingly expect natural language interfaces for task management. This feature transforms the traditional form-based todo application into an AI-powered conversational interface while maintaining backward compatibility with existing functionality.

## User Personas

- **Primary**: Tech-savvy users who prefer natural language interactions over traditional UI controls
- **Secondary**: Users who want a more intuitive way to manage tasks without clicking through multiple screens
- **Tertiary**: Power users who want to manage tasks quickly through voice or text commands

## User Scenarios & Testing

### Scenario 1: Adding Tasks via Natural Language
- **Given**: User is on the chat interface
- **When**: User types "add task to buy groceries"
- **Then**: AI agent calls add_task tool and responds "Created task: Buy Groceries"

### Scenario 2: Listing Tasks
- **Given**: User has multiple tasks in their list
- **When**: User types "show me all my tasks"
- **Then**: AI agent calls list_tasks tool and displays all tasks in the chat

### Scenario 3: Filtering Tasks
- **Given**: User has both completed and pending tasks
- **When**: User types "what's pending?"
- **Then**: AI agent calls list_tasks with status filter and shows only pending tasks

### Scenario 4: Completing Tasks
- **Given**: User has tasks in their list
- **When**: User types "mark task 3 as done"
- **Then**: AI agent calls complete_task(3) and confirms completion

### Scenario 5: Updating Tasks
- **Given**: User wants to modify an existing task
- **When**: User types "change task 1 to 'Call mom tonight'"
- **Then**: AI agent calls update_task and confirms the update

### Scenario 6: Deleting Tasks
- **Given**: User wants to remove a task
- **When**: User types "delete the grocery task"
- **Then**: AI agent searches, asks for confirmation, and calls delete_task

### Scenario 7: Conversation Persistence
- **Given**: User had previous conversations with the AI
- **When**: User closes browser and reopens the app
- **Then**: Previous chat history loads from the database

### Scenario 8: Handling Ambiguous Requests
- **Given**: User enters a vague request
- **When**: User types "Do something with my tasks"
- **Then**: AI agent asks for clarification

## Functional Requirements

### FR-1: Natural Language Processing
- **Requirement**: The system must interpret natural language commands to manage tasks
- **Acceptance Criteria**:
  - "add buy groceries" → creates a new task with title "Buy Groceries"
  - "show me all my tasks" → retrieves and displays all user tasks
  - "what's pending?" → retrieves and displays only incomplete tasks
  - "mark 3 complete" → marks task with ID 3 as completed
  - "delete task 5" → deletes task with ID 5
  - "change task 1 to call mom" → updates task 1 title to "Call Mom"

### FR-2: MCP Tool Integration
- **Requirement**: The system must expose 5 stateless tools via MCP protocol
- **Acceptance Criteria**:
  - add_task tool accepts user_id, title, and optional description parameters
  - list_tasks tool accepts user_id and optional status filter
  - complete_task tool accepts user_id and task_id parameters
  - update_task tool accepts user_id, task_id, and optional title/description parameters
  - delete_task tool accepts user_id and task_id parameters
  - All tools store state in the Neon database

### FR-3: Chat Interface
- **Requirement**: The system must provide a conversational interface using OpenAI ChatKit
- **Acceptance Criteria**:
  - Chat interface is available at /chat route
  - "Chat Assistant" link is added to navigation header
  - Typing indicators show when agent is processing
  - Responses are properly formatted (lists, confirmations, errors)

### FR-4: Conversation Persistence
- **Requirement**: The system must persist conversation history in the database
- **Acceptance Criteria**:
  - Conversation model stores id, user_id, created_at, updated_at
  - Message model stores id, conversation_id, role, content, created_at, tool_calls
  - Previous conversation history loads when user returns to chat
  - User can resume conversations across browser sessions

### FR-5: Agent Behavior
- **Requirement**: The AI agent must provide helpful, context-aware responses
- **Acceptance Criteria**:
  - Agent confirms all actions with friendly natural language
  - Agent asks for clarification when requests are ambiguous
  - Agent provides context-aware suggestions
  - Agent handles tool failures gracefully
  - Agent maintains conversation context for follow-up questions

### FR-6: API Endpoint
- **Requirement**: The system must expose a chat endpoint for processing requests
- **Acceptance Criteria**:
  - Endpoint available at POST /api/{user_id}/chat
  - Accepts parameters: conversation_id (optional) and message
  - Returns: conversation_id, response, tool_calls
  - Endpoint is stateless and backed by database

### FR-7: Backward Compatibility
- **Requirement**: Existing functionality must remain operational
- **Acceptance Criteria**:
  - Traditional REST API endpoints continue to work
  - Existing UI components remain functional
  - User authentication and authorization remain intact

## Non-Functional Requirements

### NFR-1: Performance
- AI responses should be delivered within 5 seconds under normal load
- Chat interface should update in real-time without noticeable delays
- Database operations should complete within 2 seconds

### NFR-2: Availability
- Chat functionality should be available 99.5% of the time
- System should recover gracefully from temporary API outages
- Conversation history should remain accessible during partial outages

### NFR-3: Security
- All conversation data must be encrypted in transit and at rest
- User isolation must be maintained (users can only access their own conversations)
- API keys must be stored securely in environment variables
- Natural language input must be sanitized to prevent injection attacks

### NFR-4: Scalability
- System should support up to 1000 concurrent users
- MCP tools should be stateless to allow horizontal scaling
- Database queries should be optimized with proper indexing

## Key Entities

### Conversation Entity
- **Attributes**: id (int), user_id (int), created_at (datetime), updated_at (datetime)
- **Relationships**: One-to-many with Message entity, belongs to User

### Message Entity
- **Attributes**: id (int), conversation_id (int), role (string), content (string), created_at (datetime), tool_calls (json)
- **Relationships**: Belongs to Conversation

### Task Entity (Existing)
- **Attributes**: id (int), user_id (int), title (string), description (string), completed (boolean), created_at (datetime), updated_at (datetime)
- **Relationships**: Belongs to User

### User Entity (Existing)
- **Attributes**: id (int), email (string), password_hash (string)
- **Relationships**: One-to-many with Conversation, One-to-many with Task

## Dependencies

- Groq API (llama-3.3-70b-versatile)
- OpenAI SDK configured for Groq
- Official MCP SDK
- OpenAI ChatKit
- Neon PostgreSQL database
- Existing authentication system

## Assumptions

- Groq API will remain available and responsive during normal operation
- Users have basic familiarity with chat interfaces
- Network connectivity is sufficient for real-time AI interactions
- Users will provide meaningful natural language input
- The existing authentication system is properly implemented

## Constraints

- Must use OpenAI ChatKit for the frontend interface
- MCP server must be implemented with the Official MCP SDK
- No in-memory conversation state (server must be restartable)
- GROQ_API_KEY must be retrieved from environment variable
- All MCP tools must be stateless and store state in the database
- Timeline: Complete by December 21, 2025
- LLM: Groq API with llama-3.3-70b-versatile model (FREE)
- OpenAI SDK: Used as client but pointing to Groq base_url
- Base URL: https://api.groq.com/openai/v1
- Zero API costs using Groq free tier

## Building

The agent integrates with Groq using the OpenAI SDK:

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=messages,
    tools=tools
)
```

## Success Criteria

- Users can successfully add, list, update, complete, and delete tasks using natural language commands
- AI agent correctly interprets 95% of common task management commands
- Average response time for AI interactions is under 3 seconds
- 90% of users find the chat interface more intuitive than traditional forms
- Conversation history persists across browser sessions
- All existing functionality remains operational during and after implementation
- AI agent handles ambiguous requests gracefully with appropriate clarification
- System maintains user data isolation with no cross-user data access
- 99% uptime for chat functionality in production environment