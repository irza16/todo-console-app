# Implementation Plan: Full-Stack Todo Web Application with Authentication

**Branch**: `002-auth-todo-fullstack` | **Date**: 2026-01-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/sp.plan` command with full architecture specification

## Summary

Full-stack monorepo with Next.js 15+ frontend (Vercel), FastAPI backend (Railway/Render), and Neon PostgreSQL database. Features user authentication (Better Auth + JWT), task CRUD operations, and responsive UI. Implements multi-user architecture with strict user data isolation at the database layer.

## Technical Context

**Language/Version**:
- Frontend: TypeScript (Node.js 20+), Next.js 15+ App Router
- Backend: Python 3.13+, FastAPI 0.115+, SQLModel

**Primary Dependencies**:
- Frontend: React, Tailwind CSS, shadcn/ui, Axios, React Query, Better Auth
- Backend: FastAPI, SQLModel, Pydantic, python-jose (JWT), passlib (password hashing)

**Storage**: Neon Serverless PostgreSQL 14+ (cloud database, no local SQLite)

**Testing**: Manual API testing via /docs (Swagger UI), browser-based user flow testing

**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge), responsive design for mobile/tablet/desktop

**Project Type**: Full-stack web application (monorepo with frontend/ and backend/)

**Performance Goals**:
- Registration: <2 minutes (SC-001)
- Login: <30 seconds (SC-002)
- Loading indicators within 200ms (SC-007)
- 95% first-attempt success rate for primary task flow (SC-004)

**Constraints**:
- Neon PostgreSQL only (no local SQLite)
- Better Auth + JWT (no custom auth)
- All endpoints except /auth/* require JWT token
- User isolation enforced at data layer
- CORS configured for frontend domain only
- No hardcoded secrets, use .env templates

**Scale/Scope**: Single-user focus initially, hackathon demo scale

## Constitution Check

| Requirement | Status | Notes |
|------------|--------|-------|
| Spec-driven development with subagent orchestration | PASS | All code generated via Claude Code subagents from specs |
| Multi-user architecture with user data isolation | PASS | All queries filtered by user_id, JWT contains user_id claim |
| Type-safe full-stack (TS frontend, Python backend) | PASS | TypeScript strict mode, Pydantic validation on backend |
| JWT authentication with proper verification | PASS | Better Auth frontend, JWT Bearer token backend verification |
| User isolation enforced at data layer | PASS | Every task query includes WHERE user_id = :current_user_id |
| No hardcoded secrets, use .env | PASS | Environment variable templates specified |
| Responsive design (mobile to desktop) | PASS | Specified 375px to 1920px range |
| Loading states and error handling | PASS | Skeletons/spinners, toast notifications required |
| OpenAPI documentation at /docs | PASS | FastAPI auto-generates Swagger UI |
| Monorepo with frontend/ and backend/ | PASS | Specified folder structure |
| Frontend: camelCase, Backend: snake_case | PASS | Naming conventions specified |

## Project Structure

### Documentation (this feature)

```text
specs/002-auth-todo-fullstack/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (this plan)
├── data-model.md        # Phase 1 output (below)
├── quickstart.md        # Phase 1 output (below)
├── contracts/           # Phase 1 output (below)
│   └── openapi.yaml     # OpenAPI 3.0 specification
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (monorepo)

```text
todo-fullstack/
├── frontend/
│   ├── app/
│   │   ├── layout.tsx           # Root layout with providers
│   │   ├── page.tsx             # Landing page
│   │   ├── login/
│   │   │   └── page.tsx         # Login page
│   │   ├── signup/
│   │   │   └── page.tsx         # Signup page
│   │   └── tasks/
│   │       └── page.tsx         # Protected tasks page
│   ├── components/
│   │   ├── ui/                  # shadcn/ui components
│   │   ├── auth/
│   │   │   ├── login-form.tsx
│   │   │   ├── signup-form.tsx
│   │   │   └── protected-route.tsx
│   │   ├── tasks/
│   │   │   ├── task-list.tsx
│   │   │   ├── task-card.tsx
│   │   │   ├── task-form.tsx
│   │   │   └── task-dialog.tsx
│   │   └── layout/
│   │       └── header.tsx       # Header with logout button
│   ├── lib/
│   │   ├── api.ts               # Axios client with JWT interceptor
│   │   ├── auth.ts              # Better Auth configuration
│   │   └── utils.ts             # Utility functions
│   ├── hooks/
│   │   ├── use-tasks.ts         # React Query hooks for tasks
│   │   └── use-auth.ts          # React Query hooks for auth
│   ├── types/
│   │   └── index.ts             # TypeScript type definitions
│   ├── .env.local               # Frontend environment variables
│   └── package.json
├── backend/
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration management
│   ├── db.py                    # Database connection setup
│   ├── models.py                # SQLModel User and Task models
│   ├── routes/
│   │   ├── auth.py              # Authentication endpoints
│   │   └── tasks.py             # Task CRUD endpoints
│   ├── crud/
│   │   └── task.py              # Task CRUD operations
│   ├── middleware/
│   │   └── auth.py              # JWT verification middleware
│   ├── utils/
│   │   ├── jwt.py               # JWT encoding/decoding utilities
│   │   └── crud.py              # Base CRUD utilities
│   ├── .env                     # Backend environment variables
│   └── pyproject.toml
├── specs/                       # Feature specifications
├── .claude/                     # Claude Code configuration
└── README.md                    # Project documentation
```

**Structure Decision**: Monorepo with frontend/ and backend/ folders as specified in the plan input. This enables easy cloning for judges and coordinated deployments.

## Key Design Decisions

### 1. Monorepo vs Separate Repos

| Option | Decision | Rationale |
|--------|----------|-----------|
| Single repo with frontend/ + backend/ | SELECTED | Easier for hackathon judges to clone and review, shared .claude/ folder, coordinated deployments |
| Separate frontend and backend repos | REJECTED | More complex to manage, harder to demonstrate end-to-end flow |

### 2. Authentication Strategy

| Option | Decision | Rationale |
|--------|----------|-----------|
| Better Auth (frontend) + JWT verification (backend) | SELECTED | Matches hackathon spec, skills already created, stateless backend |
| NextAuth.js | CONSIDERED | Good alternative but Better Auth specified in requirements |
| Custom session cookies | REJECTED | Security risks, more maintenance |

### 3. API Structure: Nested Routes vs Flat

| Option | Decision | Rationale |
|--------|----------|-----------|
| /api/{user_id}/tasks | SELECTED | Explicit user context in URL, easier to secure, matches RESTful patterns |
| /api/tasks (with token) | REJECTED | Requires additional user_id extraction from token for every query |

### 4. State Management: React Query vs Redux

| Option | Decision | Rationale |
|--------|----------|-----------|
| React Query (TanStack Query) | SELECTED | Built for server state, caching, simpler than Redux, skills already created |
| Redux Toolkit | CONSIDERED | More boilerplate, overkill for this scope |
| Zustand | CONSIDERED | Good alternative but React Query better for API data |

### 5. Deployment: Vercel + Railway vs Other Combos

| Option | Decision | Rationale |
|--------|----------|-----------|
| Vercel (frontend) + Railway or Render (backend) | SELECTED | Vercel best for Next.js, Railway/Render have generous free tiers |
| Netlify + Heroku | CONSIDERED | Heroku no longer has free tier |
| Vercel + Railway | PREFERRED | Both have excellent Next.js/FastAPI support |

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER (Browser)                              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    NEXT.JS FRONTEND (Vercel)                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Pages: / → /login → /signup → /tasks (protected)            │  │
│  │ Better Auth: Session management, JWT storage                │  │
│  │ API Client: Axios + React Query + JWT interceptor           │  │
│  │ UI: shadcn/ui components, Tailwind CSS                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTPS + JWT Bearer Token
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              FASTAPI BACKEND (Railway/Render/Heroku)               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ /api/auth/* → signup, login, me (public)                    │  │
│  │ /api/{user_id}/tasks/* → CRUD operations (protected)        │  │
│  │ JWT Middleware: Verify token, extract user_id               │  │
│  │ CORS: Allow frontend origin                                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │ SQLModel queries
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 NEON POSTGRESQL (Cloud Database)                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ users: id, email(unique), name, hashed_password             │  │
│  │ tasks: id, user_id(FK), title, description, completed       │  │
│  │ Index: user_id, user_id+completed                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Database & Backend Foundation

**Owner**: Database Architect + Backend Developer

| Task | Description |
|------|-------------|
| Set up Neon database | Create PostgreSQL database, get connection string |
| Create SQLModel models | User model with email/password_hash, Task model with user_id FK |
| Implement DB connection | SQLModel engine setup with Neon connection string |
| Create database tables | Run migrations or auto-create on startup |

### Phase 2: Authentication

**Owner**: Auth Specialist + Backend Developer

| Task | Description |
|------|-------------|
| Signup endpoint | POST /api/auth/signup - hash password, create user, return JWT |
| Login endpoint | POST /api/auth/login - verify password, return JWT |
| JWT middleware | Verify Bearer token, extract user_id, reject invalid tokens |
| Password hashing | Use passlib with bcrypt or argon2 |

### Phase 3: Task API

**Owner**: Backend Developer

| Task | Description |
|------|-------------|
| GET /api/{user_id}/tasks | List all user's tasks (filtered by user_id) |
| POST /api/{user_id}/tasks | Create new task for user |
| GET /api/{user_id}/tasks/{id} | Get single task (verify ownership) |
| PUT /api/{user_id}/tasks/{id} | Update task title/description |
| PATCH /api/{user_id}/tasks/{id}/complete | Toggle completion status |
| DELETE /api/{user_id}/tasks/{id} | Delete task (with confirmation from frontend) |

### Phase 4: Frontend Setup

**Owner**: Frontend Developer

| Task | Description |
|------|-------------|
| Initialize Next.js | Create Next.js 15+ project with TypeScript and Tailwind |
| Set up Better Auth | Configure auth client, providers |
| Create layout | Root layout with auth providers and global styles |
| Landing page | Welcome page with navigation to login/signup |

### Phase 5: Auth UI

**Owner**: Frontend Developer + Auth Specialist

| Task | Description |
|------|-------------|
| Login form | Email/password form with validation |
| Signup form | Email/name/password form with validation |
| Protected route | Redirect unauthenticated users to /login |
| Logout | Clear session, redirect to /login |

### Phase 6: Task UI

**Owner**: Frontend Developer

| Task | Description |
|------|-------------|
| Task list | Display all tasks with completion status |
| Task card | Individual task with edit/delete actions |
| Task form/dialog | Create and edit task with validation |
| Task management page | Main tasks page with all components |

### Phase 7: Integration

**Owner**: Integration Specialist

| Task | Description |
|------|-------------|
| API client | Axios instance with JWT interceptor |
| React Query hooks | useTasks, useCreateTask, useUpdateTask, etc. |
| Connect components | Wire UI to API through hooks |

### Phase 8: Deployment

**Owner**: DevOps Specialist

| Task | Description |
|------|-------------|
| Backend deployment | Deploy to Railway/Render with environment variables |
| Frontend deployment | Deploy to Vercel, configure environment variables |
| CORS configuration | Allow frontend domain in backend CORS settings |
| Domain configuration | Set up environment variables for API URL |

### Phase 9: QA & Polish

**Owner**: QA Specialist + All

| Task | Description |
|------|-------------|
| User flow testing | Signup → login → CRUD → logout |
| Responsive design | Test mobile, tablet, desktop layouts |
| Loading states | Verify skeletons/spinners on async operations |
| Error handling | Test and improve error messages |
| API documentation | Verify /docs works with all endpoints |

## Quality Validation

| Check | Method |
|-------|--------|
| API endpoints | Test via /docs (Swagger UI) |
| User flows | Manual browser testing (signup → login → CRUD → logout) |
| Frontend errors | Browser console must be error-free |
| Status codes | 200, 201, 204, 400, 401, 403, 404, 500 |
| JWT handling | Token stored and sent correctly |
| User isolation | Users can only access their own tasks |
| Responsive design | Mobile/tablet/desktop viewport testing |
| Loading states | Visual feedback during async operations |
| Error toasts | User-friendly messages for failed operations |
| Deployment | Both apps accessible via public URLs |

## Complexity Tracking

No constitution violations requiring justification. All decisions align with the Phase II constitution requirements.

## Next Steps

After `/sp.plan` completion:
1. Run `/sp.tasks` to generate implementation tasks
2. Execute tasks via subagents (`/sp.implement`)
3. Each phase produces working code that can be tested
