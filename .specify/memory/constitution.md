<!--
  Sync Impact Report
  Version change: 2.0.0 → 3.0.0 (Phase II → Phase III)
  Added sections:
    - Conversational AI-first interface principle
    - MCP (Model Context Protocol) architecture principle
    - Statelessness principle
    - Agent-driven task management principle
    - Backward compatibility principle
    - New technology stack elements (OpenAI ChatKit, Agents SDK, MCP SDK)
    - New data model additions (conversations, messages)
    - New deployment constraints (MCP server)
  Removed sections:
    - None (backward compatible addition)
  Templates requiring updates:
    - .specify/templates/spec-template.md ⚠ pending
    - .specify/templates/plan-template.md ⚠ pending
    - .specify/templates/tasks-template.md ⚠ pending
  Follow-up TODOs:
    - Update templates to accommodate MCP and AI features
    - Add quality gates for AI interactions
-->

# Todo Full-Stack Web Application Constitution

## Core Principles

### 1. Spec-Driven Development with Subagent Orchestration
All code must be generated from specifications using Claude Code subagents.
Manual coding is NOT allowed. Iterate on specs, not code - bugs in code mean
specs need refinement. Every feature requires: specification → plan → tasks →
implementation via subagents.

### 2. Multi-User Architecture
Each user owns their data in isolation. All database queries MUST filter by
user_id. No cross-user data access. Authentication establishes identity before
any privileged operation. User isolation is non-negotiable and enforced at
the data layer.

### 3. Type-Safe Full-Stack
TypeScript frontend and Python backend share data contracts. API schemas are
defined once and validated at both ends. Frontend uses camelCase, backend uses
snake_case with automatic conversion. Shared types ensure end-to-end type safety.

### 4. Secure by Default
JWT authentication with proper verification on all protected endpoints.
Input validation on both client and server. No hardcoded secrets - use .env
variables only. CORS configured explicitly for frontend domain. SQL injection
prevention via SQLModel ORM.

### 5. Production-Ready Patterns
Error handling with user-friendly messages. Loading states (skeletons/spinners)
for all async operations. Responsive design for mobile, tablet, desktop.
Comprehensive API documentation via OpenAPI/Swagger UI.

### 6. Conversational AI-First Interface
Natural language interactions take precedence over traditional button/form interfaces.
Users interact with the system through conversational prompts rather than UI controls.
The AI agent interprets user intent and performs appropriate actions on their behalf.

### 7. MCP (Model Context Protocol) Architecture
Tool-based AI interactions using official MCP SDK for exposing backend functionality.
Stateless backend design with all conversation state persisted to database.
Agent-driven task management where AI interprets intent and calls appropriate tools.

### 8. Backward Compatibility
Existing REST API remains functional alongside new chat interface.
Legacy interfaces continue to work without disruption during AI feature rollout.

## Technology Stack

### Required Stack
- **Frontend**:
  - Framework: Next.js 15+ (App Router)
  - Language: TypeScript
  - Styling: Tailwind CSS
  - UI Components: shadcn/ui
  - Authentication: Better Auth
  - AI Interface: OpenAI ChatKit for chat interface (using Groq API backend)
- **AI Framework**:
  - Orchestration: OpenAI SDK configured for Groq API for agent orchestration
  - Tooling: Official MCP SDK (Python) exposing task tools
- **Backend**:
  - Framework: FastAPI 0.115+
  - Language: Python 3.13+
  - ORM: SQLModel
  - Validation: Pydantic
  - AI Integration: MCP server exposing task tools
- **AI Technology Versions**:
  - Groq API: Latest (FREE tier)
  - OpenAI SDK: 1.0.0+ (used as Groq client)
  - Model: llama-3.3-70b-versatile
  - Base URL: https://api.groq.com/openai/v1
- **Database**:
  - Provider: Neon Serverless PostgreSQL 14+
- **Infrastructure**:
  - Frontend hosting: Vercel (free tier)
  - Backend hosting: Koyeb (free tier acceptable)
- **API**:
  - Style: RESTful JSON and MCP tool-based
  - Auth: JWT Bearer tokens
  - Documentation: OpenAPI at /docs

### Code Organization
- Monorepo structure: `frontend/` and `backend/` folders
- MCP server: Python-based tools for AI agent interactions
- Shared types: Define contracts in frontend, mirror in backend
- Environment variables: `.env.example` templates, no secrets committed

### Naming Conventions
- TypeScript: camelCase (e.g., `taskList`, `userId`)
- Python: snake_case (e.g., `task_list`, `user_id`)
- Constants: UPPER_CASE in respective languages

## User Experience Rules

### Authentication Flow
- Signup creates user with encrypted password
- Login returns JWT for protected requests
- Protected routes redirect to login when unauthenticated
- Logout clears local session

### Task Management
- Create, read, update, delete tasks via web UI and natural language
- Each user sees only their own tasks
- Optimistic UI updates for responsive feel
- Error states communicate clearly what went wrong

### Conversational AI Interface
- Natural language interaction with AI agent for task management
- AI interprets user intent and performs appropriate task operations
- Context-aware responses that maintain conversation history
- Helpful confirmations and error messages for all AI interactions

### Responsive Design
- Mobile-first approach
- Touch-friendly controls
- Breakpoints for tablet and desktop
- Consistent experience across devices

### Loading States
- Skeleton loaders for data fetching
- Spinners for async operations
- Disabled states during submission
- No silent failures

## Data Model

### User Structure
```python
# Backend (SQLModel)
{
    "id": int,           # Primary key
    "email": str,        # Unique, validated
    "password_hash": str # Never store plain text
}
```

### Task Structure
```python
# Backend (SQLModel)
{
    "id": int,           # Primary key
    "user_id": int,      # Foreign key, indexed
    "title": str,        # Required, max 200 chars
    "description": str,  # Optional, max 1000 chars
    "completed": bool,   # Default: False
    "created_at": datetime,
    "updated_at": datetime
}
```

### Conversation Structure
```python
# Backend (SQLModel)
{
    "id": int,           # Primary key
    "user_id": int,      # Foreign key, indexed
    "created_at": datetime,
    "updated_at": datetime
}
```

### Message Structure
```python
# Backend (SQLModel)
{
    "id": int,           # Primary key
    "conversation_id": int,  # Foreign key, indexed
    "role": str,         # Role (user/assistant)
    "content": str,      # Message content
    "created_at": datetime,
    "tool_calls": dict   # Tool calls made during message
}
```

### User Isolation
- Every task query includes: `WHERE user_id = :current_user_id`
- Every conversation query includes: `WHERE user_id = :current_user_id`
- JWT token contains `user_id` claim
- No cross-user data leakage possible

## API Security

### Authentication
- All endpoints except `/auth/*` and `/chat/*` require valid JWT Bearer token
- JWT verified on backend before processing requests
- Tokens expire (configurable, recommend 24 hours)
- Refresh token flow supported

### Input Validation
- Pydantic models validate all request bodies
- Frontend forms validate before submission
- MCP tools validate inputs independently
- SQL injection prevention via SQLModel parameterized queries
- XSS prevention via React's auto-escaping

### MCP Security
- MCP tools receive user_id and validate permissions independently
- All MCP tools enforce user isolation
- Natural language input sanitized before processing

### CORS Configuration
- Explicit allowed origins (frontend domain)
- Credentials: true only with specific origin
- Methods: REST standard (GET, POST, PUT, DELETE) and MCP protocols
- Headers: Authorization, Content-Type, MCP-specific headers

## Quality Gates

Before submission, ensure:
- [ ] Multi-user system: Signup, login, protected routes work
- [ ] CRUD operations: Create, read, update, delete via web UI
- [ ] User isolation: Users only see their own tasks
- [ ] Error handling: User-friendly messages for all error cases
- [ ] Loading states: Skeletons/spinners on all async operations
- [ ] Responsive design: Works on mobile, tablet, desktop
- [ ] API documentation: Swagger UI accessible at /docs
- [ ] Deployment: Frontend on Vercel, backend on Koyeb, database on Neon
- [ ] Type safety: No `any` types, proper TypeScript strict mode
- [ ] Code generation: All code via subagents from specs
- [ ] AI Interface: Natural language task management works via chat
- [ ] MCP Integration: Tools properly exposed and secured
- [ ] Conversation Persistence: Messages stored and retrievable across sessions
- [ ] Agent Behavior: Natural language understanding works reliably
- [ ] Backward Compatibility: Legacy REST API still functional

## Development Workflow

1. **Specify**: Write feature specification in `specs/<feature>/spec.md`
2. **Plan**: Create architectural plan in `specs/<feature>/plan.md`
3. **Tasks**: Generate testable tasks in `specs/<feature>/tasks.md`
4. **Implement**: Execute tasks via subagents (`/sp.implement`)
5. **Test**: Validate against acceptance criteria
6. **Iterate**: If bugs → refine specs, regenerate code
7. **Never**: Manually fix code - fix the spec instead

## Success Definition

Phase III is complete when:
- Users can chat with AI to manage tasks via natural language
- Agent correctly interprets: add, list, update, delete, complete intents
- Conversation persists across page refreshes (resume capability)
- Agent provides helpful confirmations and error messages
- All task operations work through chat (no REST API calls from chat UI)
- MCP server exposes 5 tools: add_task, list_tasks, complete_task, update_task, delete_task
- Agent chains tools when needed (e.g., "show pending" → list → filter)
- Frontend deploys to Vercel, backend to Koyeb, database to Neon
- API documentation available at /docs
- Responsive design works on mobile, tablet, desktop
- User-friendly error messages and loading states throughout
- All code generated by subagents from specifications
- Backward compatibility maintained (REST API still functional)

## Governance

This constitution supersedes all other development practices for this project.

**Amendment Process**:
- Constitution changes require documented rationale
- Backward-incompatible changes require major version bump (4.0.0+)
- New principles or expanded guidance requires minor version bump (3.1.0+)
- Clarifications, wording fixes, typo corrections use patch bump (3.0.1+)

**Compliance**:
- All PRs/reviews must verify constitution compliance
- Complexity beyond constitution scope must be justified
- Refer to CLAUDE.md for runtime development guidance

**Version**: 3.0.0 | **Ratified**: 2025-12-31 | **Last Amended**: 2026-01-14