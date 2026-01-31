---
id: 1
title: amend-constitution-ai-powered-todo-chatbot
stage: constitution
dateIso: 2026-01-14
surface: agent
model: google/gemini-2.0-flash-exp:free
feature: ai-powered-todo-chatbot
branch: 001-todo-console-app
user: irza
command: /sp.constitution
labels:
  - constitution
  - ai
  - mcp
  - chatbot
links:
  spec: null
  ticket: null
  adr: null
  pr: null
filesYaml: |
  - .specify/memory/constitution.md
tasksYaml: |
  - Update constitution to version 3.0.0
  - Add AI-powered chatbot principles
  - Add MCP architecture principles
  - Update technology stack to include OpenAI components
  - Add new data models for conversations and messages
  - Update deployment constraints
promptText: |
  /sp.constitution

  Project: AI-Powered Todo Chatbot - Phase III (Hackathon II)

  Core principles:
  - Conversational AI-first interface (natural language over buttons/forms)
  - MCP (Model Context Protocol) architecture for tool-based AI interactions
  - Stateless backend design (all conversation state persisted to database)
  - Agent-driven task management (AI interprets intent, calls appropriate tools)
  - Backward compatible (existing REST API remains functional alongside chat)

  Key standards:
  - Frontend: OpenAI ChatKit for chat interface
  - AI Framework: OpenAI Agents SDK for agent orchestration
  - MCP Server: Official MCP SDK (Python) exposing task tools
  - Backend: FastAPI with both REST endpoints AND chat endpoint
  - Database: Neon PostgreSQL with new tables (conversations, messages)
  - Tools: MCP tools must be stateless, store all state in database
  - Agent behavior: Natural language understanding, context-aware responses
  - Conversation persistence: All messages stored, retrievable across sessions

  Constraints:
  - No hardcoded conversation memory in code (must use database)
  - MCP tools receive user_id and store state independently
  - Chat endpoint: POST /api/{user_id}/chat (stateless request/response)
  - Agent must use MCP tools for ALL task operations (no direct DB access)
  - Natural language only: "add buy groceries" not button clicks
  - OpenAI API key required (from environment variable)
  - Agent must handle ambiguous requests gracefully
  - Conversation history sent with each request for context

  Technology versions:
  - OpenAI Agents SDK: latest
  - Official MCP SDK: latest (Python)
  - OpenAI ChatKit: latest
  - OpenAI API: gpt-4 or gpt-4-turbo

  Data model additions:
  - Conversation: {id, user_id, created_at, updated_at}
  - Message: {id, conversation_id, role (user/assistant), content, created_at, tool_calls}
  - Existing Task model unchanged (reused via MCP tools)

  Success criteria:
  - User can chat with AI to manage tasks via natural language
  - Agent correctly interprets: add, list, update, delete, complete intents
  - Conversation persists across page refreshes (resume capability)
  - Agent provides helpful confirmations and error messages
  - All task operations work through chat (no REST API calls from chat UI)
  - MCP server exposes 5 tools: add_task, list_tasks, complete_task, update_task, delete_task
  - Agent chains tools when needed (e.g., "show pending" → list → filter)
  - Deployed: Frontend on Vercel, Backend on Koyeb, Database on Neon
  - Zero manual coding: All implemented by subagents from specs
responseText: |
  Updated the constitution to version 3.0.0 to incorporate the AI-powered Todo Chatbot features with MCP architecture. Added new principles for conversational AI-first interface, MCP architecture, and backward compatibility. Updated the technology stack to include OpenAI ChatKit, Agents SDK, and MCP SDK. Added new data models for conversations and messages. Updated deployment constraints to reflect Koyeb hosting for the backend. The constitution now supports both traditional REST API and new chat interface while maintaining backward compatibility.
outcome: |
  Successfully updated the project constitution to version 3.0.0 incorporating AI-powered chatbot features with MCP architecture. The new constitution includes principles for conversational AI, MCP tools, and maintains backward compatibility with existing REST API.
evaluation: |
  The constitution update is complete and reflects all the new features and constraints specified in the user input. The version has been incremented from 2.0.0 to 3.0.0 as required for the significant additions.
---
