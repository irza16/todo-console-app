---
id: 2
title: specify-conversational-ai-todo-assistant-with-mcp-architecture
stage: spec
dateIso: 2026-01-14
surface: agent
model: google/gemini-2.0-flash-exp:free
feature: ai-todo-chatbot
branch: 1-ai-todo-chatbot
user: irza
command: /sp.specify
labels:
  - ai
  - mcp
  - chatbot
  - specification
links:
  spec: specs/1-ai-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
filesYaml: |
  - specs/1-ai-todo-chatbot/spec.md
  - specs/1-ai-todo-chatbot/checklists/requirements.md
tasksYaml: |
  - Create specification for AI-powered todo chatbot
  - Define functional requirements for natural language processing
  - Specify MCP tool integration requirements
  - Define conversation persistence requirements
  - Create user scenarios and testing criteria
  - Validate specification quality
promptText: |
  /sp.specify

  Project: Conversational AI todo assistant with MCP tool architecture

  Target audience: Hackathon judges evaluating AI agent integration and MCP implementation

  Focus: Demonstrating AI-native interface evolution from traditional web forms (Phase II) to natural language chat (Phase III)

  Success criteria:
  - User can type "add task to buy groceries" → Agent calls add_task tool → Responds "Created task: Buy groceries"
  - User can say "show me all my tasks" → Agent calls list_tasks → Displays task list in chat
  - User can say "what's pending?" → Agent calls list_tasks with completed=false → Shows pending tasks
  - User can say "mark task 3 as done" → Agent calls complete_task(3) → Confirms completion
  - User can say "delete the grocery task" → Agent searches, asks confirmation, calls delete_task
  - User can say "change task 1 to 'Call mom tonight'" → Agent calls update_task → Confirms update
  - Conversation persists: Close browser, reopen → Previous chat history loads from database
  - Agent handles unclear requests: "Do something with my tasks" → Asks clarification
  - Agent provides context-aware responses using conversation history
  - Agent confirms all actions with friendly natural language
  - MCP server exposes 5 stateless tools, each stores state in Neon database
  - Chat endpoint returns: {conversation_id, response, tool_calls}
  - UI shows typing indicator while agent processes
  - UI displays agent responses with proper formatting (lists, confirmations, errors)
  - All Phase II functionality still works via REST API (backward compatible)

  Constraints:
  - Frontend: OpenAI ChatKit (not custom chat UI)
  - Backend: Must implement MCP server with Official MCP SDK
  - Agent: OpenAI Agents SDK with gpt-4 or gpt-4-turbo
  - Chat endpoint: POST /api/{user_id}/chat {conversation_id?, message}
  - Conversation storage: Database (conversations + messages tables)
  - MCP tools: Stateless functions that accept user_id parameter
  - No in-memory conversation state (server must be restartable)
  - OpenAI API key: From environment variable GROQ_API_KEY
  - Timeline: Complete by December 21, 2025

  Building:
  - Database models: Conversation, Message (add to existing User, Task)
  - MCP Server: 5 tools (add_task, list_tasks, complete_task, update_task, delete_task)
  - Agent: OpenAI Agents SDK runner with tool definitions
  - Chat API endpoint: POST /api/{user_id}/chat (stateless, DB-backed)
  - Frontend: ChatKit component integrated into existing app
  - Chat page: New route /chat with ChatKit interface
  - Navigation: Add "Chat Assistant" link to header
  - Agent system prompt: Defines personality, behavior, tool usage guidelines
  - Message storage: Save user messages and agent responses with tool_calls
  - Conversation resume: Load history from DB on chat page load
  - Error handling: Agent gracefully handles tool failures, invalid requests

  Not building:
  - Custom chat UI (use ChatKit)
  - Voice input (Phase V bonus)
  - Multi-language support (Phase V bonus)
  - Streaming responses (nice-to-have, not required)
  - Advanced features: priorities, tags, due dates, categories (still deferred)
  - Real-time notifications
  - File attachments
  - Task sharing via chat
  - Multiple concurrent conversations per user (one active conversation)
  - Chat analytics/metrics
  - Agent training/fine-tuning (use base GPT-4)

  MCP Tool Specifications:

  Tool: add_task
  - Parameters: {user_id: string, title: string, description?: string}
  - Behavior: Insert task into database, return task_id and title
  - Response: {task_id: int, status: "created", title: string}

  Tool: list_tasks
  - Parameters: {user_id: string, status?: "all"|"pending"|"completed"}
  - Behavior: Query tasks from database filtered by user_id and optional status
  - Response: [{id, title, description, completed}, ...]

  Tool: complete_task
  - Parameters: {user_id: string, task_id: int}
  - Behavior: Toggle task.completed in database
  - Response: {task_id: int, status: "completed"|"pending", title: string}

  Tool: update_task
  - Parameters: {user_id: string, task_id: int, title?: string, description?: string}
  - Behavior: Update task fields in database
  - Response: {task_id: int, status: "updated", title: string}

  Tool: delete_task
  - Parameters: {user_id: string, task_id: int}
  - Behavior: Delete task from database
  - Response: {task_id: int, status: "deleted", title: string}

  Natural Language Command Examples:
  - "Add buy Groceries" → add_task
  - "Show all tasks" → list_tasks(status="all")
  - "What's pending?" → list_tasks(status="pending")
  - "Mark 3 complete" → complete_task(3)
  - "Delete task 5" → delete_task(5)
  - "Change task 1 to call mom" → update_task(1, title="Call mom")
  - "I finished the grocery shopping" → Agent asks which task → complete_task

  Agent Personality:
  - Helpful and friendly
  - Confirms all actions clearly
  - Asks for clarification when ambiguous
  - Uses casual but professional tone
  - Provides context-aware suggestions
responseText: |
  Created comprehensive specification for the Conversational AI Todo Assistant feature with MCP architecture. The specification includes:

  - Detailed functional requirements for natural language processing
  - MCP tool integration requirements
  - Chat interface specifications
  - Conversation persistence requirements
  - User scenarios covering all major use cases
  - Non-functional requirements for performance, availability, security, and scalability
  - Key entities for the data model
  - Dependencies and assumptions
  - Constraints and success criteria

  The specification is complete and ready for the planning phase.
outcome: |
  Successfully created a comprehensive specification for the AI-powered todo chatbot feature with MCP architecture. The specification covers all required functionality including natural language processing, MCP tool integration, conversation persistence, and backward compatibility with existing functionality.
evaluation: |
  The specification is complete and addresses all requirements from the user input. It defines clear functional and non-functional requirements, user scenarios, and success criteria. The specification is ready for the planning phase.
---
