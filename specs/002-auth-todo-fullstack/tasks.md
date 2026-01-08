# Implementation Tasks: Full-Stack Todo Web Application with Authentication

**Feature Branch**: `002-auth-todo-fullstack`
**Created**: 2026-01-06
**Spec**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)
**Data Model**: [data-model.md](./data-model.md)

## Summary

This document contains all implementation tasks organized by user story for the full-stack todo application with authentication. The tasks follow the spec-driven development approach with subagent orchestration.

## Task Format Legend

- **- [ ] T###**: Task checkbox with sequential ID
- **[P]**: Task can be executed in parallel (different files, no dependencies)
- **[US#]**: Task belongs to User Story # (P1-P2 priority from spec)
- **No story label**: Setup or foundational tasks (required before user stories)

## Phase 1: Setup

**Goal**: Initialize project structure for both frontend and backend

### Independent Test Criteria
- Frontend: `npm run dev` starts without errors
- Backend: `python -m uvicorn main:app --reload` starts without errors
- Both services can be accessed on their respective ports

### Implementation Tasks

- [X] T001 Initialize Next.js 15+ frontend project with TypeScript and Tailwind CSS in frontend/ directory
- [ ] T002 Create frontend/package.json with dependencies: next, react, react-dom, tailwindcss, axios, @tanstack/react-query, better-auth, shadcn-ui
- [X] T003 Set up TypeScript configuration in frontend/tsconfig.json with strict mode enabled
- [X] T004 Configure Tailwind CSS in frontend/tailwind.config.ts with custom theme colors
- [X] T005 Initialize Python backend project in backend/ directory with pyproject.toml
- [X] T006 Create backend/pyproject.toml with dependencies: fastapi, uvicorn, sqlmodel, pydantic, python-jose, passlib, alembic
- [X] T007 Create environment template: backend/.env.example with DATABASE_URL, JWT_SECRET, CORS_ORIGIN placeholders
- [X] T008 Create environment template: frontend/.env.local.example with NEXT_PUBLIC_API_URL placeholders
- [X] T009 Initialize git repository and create .gitignore for both frontend and backend
- [X] T010 [P] Set up project README.md with setup instructions for both frontend and backend

## Phase 2: Foundational

**Goal**: Create database models, connection, and JWT utilities (blocking for all user stories)

### Independent Test Criteria
- Backend: Database connection successful, models created without errors
- JWT tokens can be encoded/decoded successfully
- Password hashing and verification working

### Implementation Tasks

- [X] T011 Create backend/config.py with Pydantic settings for environment variables
- [X] T012 Create backend/db.py with SQLModel engine setup for Neon PostgreSQL connection
- [X] T013 Create backend/models.py with SQLModel User and Task models per data-model.md
- [X] T014 Create backend/utils/jwt.py with JWT encode/decode functions using python-jose
- [X] T015 Create backend/utils/crud.py with base CRUD utility functions
- [X] T016 Create backend/utils/password.py with passlib bcrypt password hashing and verification
- [X] T017 Create backend/middleware/auth.py with JWT verification middleware for protected routes
- [X] T018 [P] Create backend/main.py with FastAPI app initialization, CORS configuration, and OpenAPI docs
- [X] T019 [P] Create .env file from .env.example with Neon database connection string

## Phase 3: User Story 1 - New User Registration (P1)

**Goal**: Allow new users to create accounts with email, name, and password

**Independent Test**: User can complete signup flow with valid credentials and account exists in database

### User Story Tasks

- [ ] T020 [US1] Create backend/schemas/user.py with Pydantic SignupRequest, LoginRequest, UserResponse schemas
- [ ] T021 [US1] Create backend/routes/auth.py with POST /api/auth/signup endpoint
- [ ] T022 [US1] Implement password hashing and user creation logic in auth.py signup endpoint
- [ ] T023 [US1] Implement JWT token generation on successful signup returning user + token
- [ ] T024 [US1] Add email uniqueness validation returning 400 if email exists
- [ ] T025 [US1] Add email format and password length validation in Pydantic schemas
- [ ] T026 [US1] Create frontend/types/index.ts with TypeScript interfaces for User, AuthResponse, SignupRequest
- [ ] T027 [US1] Create frontend/lib/api.ts with Axios instance and signup API function
- [ ] T028 [US1] Create frontend/components/auth/signup-form.tsx with email/name/password form and validation
- [ ] T029 [US1] Create frontend/app/signup/page.tsx with signup page rendering signup-form component
- [ ] T030 [US1] Integrate Better Auth for session management in frontend/lib/auth.ts
- [ ] T031 [US1] Add redirect to /tasks on successful signup in signup-form.tsx

## Phase 4: User Story 2 - User Login (P1)

**Goal**: Allow registered users to authenticate with email and password

**Independent Test**: User can log in with valid credentials and access protected tasks page

### User Story Tasks

- [ ] T032 [US2] Implement POST /api/auth/login endpoint in backend/routes/auth.py
- [ ] T033 [US2] Implement password verification against stored hash in auth.py login endpoint
- [ ] T034 [US2] Implement JWT token generation on successful login returning user + token
- [ ] T035 [US2] Return 401 error for invalid credentials (wrong email or password)
- [ ] T036 [US2] Create frontend/components/auth/login-form.tsx with email/password form and validation
- [ ] T037 [US2] Create frontend/app/login/page.tsx with login page rendering login-form component
- [ ] T038 [US2] Store JWT token in localStorage via Better Auth on successful login
- [ ] T039 [US2] Add redirect to /tasks on successful login in login-form.tsx
- [ ] T040 [US2] Redirect already authenticated users from /login to /tasks

## Phase 5: User Story 3 - View Tasks (P1)

**Goal**: Display all authenticated user's tasks in a responsive web interface

**Independent Test**: User sees their tasks displayed correctly with completion status

### User Story Tasks

- [ ] T041 [US3] Create backend/schemas/task.py with Pydantic TaskCreate, TaskUpdate, TaskResponse schemas
- [ ] T042 [US3] Create backend/crud/task.py with get_tasks, get_task functions filtering by user_id
- [ ] T043 [US3] Implement GET /api/{user_id}/tasks endpoint in backend/routes/tasks.py
- [ ] T044 [US3] Add JWT authentication requirement and user_id ownership verification
- [ ] T045 [US3] Create frontend/types/index.ts Task interfaces matching backend schemas
- [ ] T046 [US3] Update frontend/lib/api.ts with getTasks, getTask API functions
- [ ] T047 [US3] Create frontend/hooks/use-tasks.ts with React Query hooks for fetching tasks
- [ ] T048 [US3] Create frontend/components/tasks/task-card.tsx for individual task display
- [ ] T049 [US3] Create frontend/components/tasks/task-list.tsx for task collection display
- [ ] T050 [US3] Create frontend/components/layout/header.tsx with app header and logout button
- [ ] T051 [US3] Create frontend/app/tasks/page.tsx protected route rendering task list
- [ ] T052 [US3] Show empty state prompt when user has no tasks
- [ ] T053 [US3] Display completed and incomplete tasks with visual distinction

## Phase 6: User Story 4 - Create Task (P1)

**Goal**: Allow authenticated users to create new tasks with title and optional description

**Independent Test**: User can create a task and it appears in the task list

### User Story Tasks

- [ ] T054 [US4] Implement POST /api/{user_id}/tasks endpoint in backend/routes/tasks.py
- [ ] T055 [US4] Add Pydantic validation requiring title (1-200 chars), optional description (0-1000 chars)
- [ ] T056 [US4] Create new task with user_id from authenticated user context
- [ ] T057 [US4] Return 201 with created task object
- [ ] T058 [US4] Update frontend/lib/api.ts with createTask API function
- [ ] T059 [US4] Update frontend/hooks/use-tasks.ts with useCreateTask mutation hook
- [ ] T060 [US4] Create frontend/components/tasks/task-form.tsx with title/description form
- [ ] T061 [US4] Create frontend/components/tasks/task-dialog.tsx for task creation dialog
- [ ] T062 [US4] Add task form to task-list page with "Add Task" button
- [ ] T063 [US4] Show validation error when title is empty on task creation
- [ ] T064 [US4] New tasks appear in list as incomplete by default
- [ ] T065 [US4] Add optimistic update to task list when task is created

## Phase 7: User Story 5 - Update Task (P2)

**Goal**: Allow authenticated users to edit task title and description

**Independent Test**: User can edit a task and changes are saved correctly

### User Story Tasks

- [ ] T066 [US5] Implement GET /api/{user_id}/tasks/{task_id} endpoint in backend/routes/tasks.py
- [ ] T067 [US5] Implement PUT /api/{user_id}/tasks/{task_id} endpoint in backend/routes/tasks.py
- [ ] T068 [US5] Add ownership verification - return 404 if task not found or belongs to different user
- [ ] T069 [US5] Add title validation (1-200 chars) when updating
- [ ] T070 [US5] Update frontend/lib/api.ts with getTask, updateTask API functions
- [ ] T071 [US5] Update frontend/hooks/use-tasks.ts with useGetTask, useUpdateTask hooks
- [ ] T072 [US5] Add edit functionality to task-card.tsx with inline editing or dialog
- [ ] T073 [US5] Reuse task-form.tsx for editing existing task
- [ ] T074 [US5] Show validation error when title becomes empty on update
- [ ] T075 [US5] Add optimistic update to task list when task is modified

## Phase 8: User Story 6 - Mark Complete/Incomplete (P2)

**Goal**: Allow authenticated users to toggle task completion status

**Independent Test**: User can mark task complete/incomplete and status persists

### User Story Tasks

- [ ] T076 [US6] Implement PATCH /api/{user_id}/tasks/{task_id}/complete endpoint in backend/routes/tasks.py
- [ ] T077 [US6] Toggle completed status and return updated task object
- [ ] T078 [US6] Update frontend/lib/api.ts with toggleComplete API function
- [ ] T079 [US6] Update frontend/hooks/use-tasks.ts with useToggleComplete hook
- [ ] T080 [US6] Add completion toggle checkbox to task-card.tsx
- [ ] T081 [US6] Show visual distinction for completed tasks (strikethrough, color change)
- [ ] T082 [US6] Add optimistic update when toggling completion status
- [ ] T083 [US6] Persist completion status across page refreshes

## Phase 9: User Story 7 - Delete Task (P2)

**Goal**: Allow authenticated users to delete tasks with confirmation

**Independent Test**: User can delete a task and it is removed from the list

### User Story Tasks

- [ ] T084 [US7] Implement DELETE /api/{user_id}/tasks/{task_id} endpoint in backend/routes/tasks.py
- [ ] T085 [US7] Return 204 No Content on successful deletion
- [ ] T086 [US7] Update frontend/lib/api.ts with deleteTask API function
- [ ] T087 [US7] Update frontend/hooks/use-tasks.ts with useDeleteTask hook
- [ ] T088 [US7] Add delete button to task-card.tsx
- [ ] T089 [US7] Implement confirmation dialog before deletion in task-card.tsx
- [ ] T090 [US7] Cancel deletion keeps task in list, confirm deletion removes it
- [ ] T091 [US7] Add optimistic removal from task list when task is deleted

## Phase 10: User Story 8 - User Logout (P2)

**Goal**: Allow authenticated users to end their session securely

**Independent Test**: User can log out and is redirected to login page

### User Story Tasks

- [ ] T092 [US8] Implement logout functionality in Better Auth frontend
- [ ] T093 [US8] Clear JWT token from localStorage on logout
- [ ] T094 [US8] Redirect to /login page after logout
- [ ] T095 [US8] Add logout button to header component
- [ ] T096 [US8] Redirect to /login when accessing /tasks without authentication
- [ ] T097 [US8] Create frontend/middleware/auth.ts with protected route wrapper component

## Phase 11: Polish & Cross-Cutting Concerns

**Goal**: Ensure production-ready quality with loading states, error handling, responsive design

### Independent Test
- All user flows work end-to-end without errors
- UI works on mobile (375px), tablet, and desktop (1920px)
- Loading indicators show during API calls
- Error messages are user-friendly

### Implementation Tasks

- [ ] T098 Add skeleton loaders to task-list.tsx while tasks are loading
- [ ] T099 Add loading spinner to login-form.tsx and signup-form.tsx during submission
- [ ] T100 Add loading state to task-card.tsx during update/delete operations
- [ ] T101 Implement global error boundary in frontend/app/layout.tsx
- [ ] T102 Add toast notifications for success/error feedback (using shadcn/ui toast)
- [ ] T103 Handle 401 errors by redirecting to login
- [ ] T104 Handle 404 errors with user-friendly "Task not found" message
- [ ] T105 Handle network errors with "Connection failed, please try again" message
- [ ] T106 Ensure responsive layout for task list on mobile devices
- [ ] T107 Ensure responsive layout for login/signup forms on mobile devices
- [ ] T108 Add touch-friendly controls for task completion toggle on mobile
- [ ] T109 Create frontend/.env.local with actual API URL configuration
- [ ] T110 Verify API documentation at backend /docs shows all endpoints
- [ ] T111 Test all API endpoints via Swagger UI at /docs
- [ ] T112 Test complete user flow: signup → login → create task → view task → update → complete → delete → logout

## Dependency Graph

```
Phase 1 (Setup) ──────► Phase 2 (Foundational)
        │                        │
        │                        ▼
        │              Phase 3 (US1: Signup) ──► Phase 4 (US2: Login)
        │                        │
        │                        ▼
        │              Phase 5 (US3: View Tasks)
        │                        │
        │                        ▼
        │              Phase 6 (US4: Create Task)
        │                        │
        │                        ▼
        │              Phase 7 (US5: Update Task)
        │                        │
        │                        ▼
        │              Phase 8 (US6: Complete Toggle)
        │                        │
        │                        ▼
        │              Phase 9 (US7: Delete Task)
        │                        │
        │                        ▼
        │              Phase 10 (US8: Logout)
        │                        │
        └────────────────────────┘
                              │
                              ▼
                   Phase 11 (Polish & Cross-Cutting)
```

## Parallel Execution Opportunities

### Within Phase 1 (Setup)
- T010 (README) can run in parallel with T001-T009

### Within Phase 2 (Foundational)
- T018 (main.py) can run in parallel with T011-T017
- T019 (.env file) can run in parallel once T007 is complete

### Within Phase 3 (US1: Signup)
- T026 (types) and T027 (api) can run in parallel
- T028 (signup-form) and T029 (signup page) can run in parallel
- T030 (Better Auth) and T031 (redirect) can run in parallel

### Within Phase 4 (US2: Login)
- T036 (login-form) and T037 (login page) can run in parallel
- T038 (token storage) and T039 (redirect) and T040 (auth redirect) can run in parallel

### Within Phase 5 (US3: View Tasks)
- T046 (api) and T045 (types) can run in parallel
- T048 (task-card) and T049 (task-list) can run in parallel
- T050 (header) and T051 (tasks page) can run in parallel

### Within Phase 6 (US4: Create Task)
- T058 (api) and T059 (hooks) can run in parallel
- T060 (task-form) and T061 (task-dialog) can run in parallel

### Within Phase 7 (US5: Update Task)
- T070 (api) and T071 (hooks) can run in parallel
- T072 (edit functionality) and T073 (reuse form) can run in parallel

### Within Phase 8 (US6: Complete Toggle)
- T078 (api) and T079 (hooks) can run in parallel
- T080 (toggle checkbox) and T081 (visual distinction) can run in parallel

### Within Phase 9 (US7: Delete Task)
- T086 (api) and T087 (hooks) can run in parallel
- T088 (delete button) and T089 (confirmation dialog) can run in parallel

## MVP Scope (User Story 1 Only)

For a minimal viable product demonstrating the core value, implement:
- Phase 1: T001-T010
- Phase 2: T011-T019
- Phase 3: T020-T031 (Signup flow)
- Phase 4: T032-T040 (Login flow)
- Phase 11: T098-T112 (Polish)

This MVP demonstrates: User registration, login, and protected route redirect - the foundation for the full application.

## Implementation Strategy

### MVP First (Phases 1-4 + 11)
Start with user registration and login flow to establish authentication foundation. This creates the JWT mechanism needed for all subsequent user story implementation.

### Incremental Delivery
1. **Auth Foundation** (Phases 1-4): Complete signup and login before task operations
2. **Task CRUD** (Phases 5-9): Add task operations one story at a time
3. **Polish** (Phase 11): Add loading states, error handling, responsive design

### Testing Approach
- Test each phase independently using the "Independent Test Criteria"
- Use /docs (Swagger UI) for backend API testing
- Use browser for frontend user flow testing
- No automated tests required per spec (manual testing specified)

## Task Summary

| Category | Count |
|----------|-------|
| Phase 1: Setup | 10 tasks |
| Phase 2: Foundational | 9 tasks |
| Phase 3: US1 (Signup) | 12 tasks |
| Phase 4: US2 (Login) | 9 tasks |
| Phase 5: US3 (View Tasks) | 13 tasks |
| Phase 6: US4 (Create Task) | 12 tasks |
| Phase 7: US5 (Update Task) | 10 tasks |
| Phase 8: US6 (Complete Toggle) | 8 tasks |
| Phase 9: US7 (Delete Task) | 8 tasks |
| Phase 10: US8 (Logout) | 6 tasks |
| Phase 11: Polish | 15 tasks |
| **Total** | **112 tasks** |

## Parallel Execution Summary

| Phase | Parallel Tasks |
|-------|---------------|
| Phase 1 | T010 can parallelize with T001-T009 |
| Phase 2 | T018-T019 can parallelize with T011-T017 |
| Phase 3 | T026-T027, T028-T029, T030-T031 each parallelize |
| Phase 4 | T036-T037, T038-T040 each parallelize |
| Phase 5 | T045-T046, T048-T049, T050-T051 each parallelize |
| Phase 6 | T058-T059, T060-T061 each parallelize |
| Phase 7 | T070-T071, T072-T073 each parallelize |
| Phase 8 | T078-T079, T080-T081 each parallelize |
| Phase 9 | T086-T087, T088-T089 each parallelize |

**Total Parallelizable Tasks**: ~30 tasks can be executed concurrently with proper agent orchestration
