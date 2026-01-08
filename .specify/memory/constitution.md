<!--
  Sync Impact Report
  Version change: 1.0.0 → 2.0.0 (Phase I → Phase II)
  Added sections:
    - Multi-user architecture principle
    - Type-safe full-stack principle
    - Secure by default principle
    - Production-ready patterns principle
    - Full-stack technology constraints (Next.js, FastAPI, Neon, Better Auth, etc.)
    - Monorepo structure (frontend/ and backend/ folders)
    - JWT authentication requirements
    - API security constraints
    - Deployment and hosting constraints
    - New success criteria for Phase II
  Removed sections:
    - Console/CLI specific constraints
    - In-memory storage constraints
    - Python-only naming conventions
  Templates requiring updates:
    - .specify/templates/spec-template.md ✅ (Phase II compatible)
    - .specify/templates/plan-template.md ✅ (Phase II compatible)
    - .specify/templates/tasks-template.md ✅ (Phase II compatible)
  Follow-up TODOs: None
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

## Technology Stack

### Required Stack
- **Frontend**:
  - Framework: Next.js 15+ (App Router)
  - Language: TypeScript
  - Styling: Tailwind CSS
  - UI Components: shadcn/ui
  - Authentication: Better Auth
- **Backend**:
  - Framework: FastAPI 0.115+
  - Language: Python 3.13+
  - ORM: SQLModel
  - Validation: Pydantic
- **Database**:
  - Provider: Neon Serverless PostgreSQL 14+
- **Infrastructure**:
  - Frontend hosting: Vercel (free tier)
  - Backend hosting: Railway/Render/Heroku (free tier acceptable)
- **API**:
  - Style: RESTful JSON
  - Auth: JWT Bearer tokens
  - Documentation: OpenAPI at /docs

### Code Organization
- Monorepo structure: `frontend/` and `backend/` folders
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
- Create, read, update, delete tasks via web UI
- Each user sees only their own tasks
- Optimistic UI updates for responsive feel
- Error states communicate clearly what went wrong

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

### User Isolation
- Every task query includes: `WHERE user_id = :current_user_id`
- JWT token contains `user_id` claim
- No cross-user data leakage possible

## API Security

### Authentication
- All endpoints except `/auth/*` require valid JWT Bearer token
- JWT verified on backend before processing requests
- Tokens expire (configurable, recommend 24 hours)
- Refresh token flow supported

### Input Validation
- Pydantic models validate all request bodies
- Frontend forms validate before submission
- SQL injection prevention via SQLModel parameterized queries
- XSS prevention via React's auto-escaping

### CORS Configuration
- Explicit allowed origins (frontend domain)
- Credentials: true only with specific origin
- Methods: REST standard (GET, POST, PUT, DELETE)
- Headers: Authorization, Content-Type

## Quality Gates

Before submission, ensure:
- [ ] Multi-user system: Signup, login, protected routes work
- [ ] CRUD operations: Create, read, update, delete via web UI
- [ ] User isolation: Users only see their own tasks
- [ ] Error handling: User-friendly messages for all error cases
- [ ] Loading states: Skeletons/spinners on all async operations
- [ ] Responsive design: Works on mobile, tablet, desktop
- [ ] API documentation: Swagger UI accessible at /docs
- [ ] Deployment: Frontend on Vercel, backend on cloud platform
- [ ] Type safety: No `any` types, proper TypeScript strict mode
- [ ] Code generation: All code via subagents from specs

## Development Workflow

1. **Specify**: Write feature specification in `specs/<feature>/spec.md`
2. **Plan**: Create architectural plan in `specs/<feature>/plan.md`
3. **Tasks**: Generate testable tasks in `specs/<feature>/tasks.md`
4. **Implement**: Execute tasks via subagents (`/sp.implement`)
5. **Test**: Validate against acceptance criteria
6. **Iterate**: If bugs → refine specs, regenerate code
7. **Never**: Manually fix code - fix the spec instead

## Success Definition

Phase II is complete when:
- Users can signup, login, and manage their own tasks via web UI
- All CRUD operations work through REST API with JWT auth
- Frontend deploys to Vercel, backend to cloud platform
- API documentation available at /docs
- Responsive design works on mobile, tablet, desktop
- User-friendly error messages and loading states throughout
- All code generated by subagents from specifications

## Governance

This constitution supersedes all other development practices for this project.

**Amendment Process**:
- Constitution changes require documented rationale
- Backward-incompatible changes require major version bump (3.0.0+)
- New principles or expanded guidance requires minor version bump (2.1.0+)
- Clarifications, wording fixes, typo corrections use patch bump (2.0.1+)

**Compliance**:
- All PRs/reviews must verify constitution compliance
- Complexity beyond constitution scope must be justified
- Refer to CLAUDE.md for runtime development guidance

**Version**: 2.0.0 | **Ratified**: 2025-12-31 | **Last Amended**: 2026-01-06
