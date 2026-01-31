---
title: AI-Powered Todo Chatbot
emoji: 📝
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: mit
---

# AI-Powered Todo Chatbot - Hugging Face Space Version

This is an AI-powered Todo Chatbot that allows you to manage your tasks using natural language. Built with FastAPI, SQLModel, and integrated with Groq AI for natural language processing.

## Features

- Natural language task management (add, list, update, complete, delete tasks)
- AI-powered chat interface
- User authentication and task isolation
- Persistent storage with database

## How to Use

1. Use the chat interface to communicate with the AI assistant
2. Type commands in natural language like:
   - "Add buy groceries to my tasks"
   - "Show me all my tasks"
   - "Mark task 1 as completed"
   - "Update task 1 to 'buy organic groceries'"
   - "Delete task 2"

## Tech Stack

- FastAPI
- SQLModel
- Gradio (for Hugging Face Space interface)
- Groq AI API
- SQLite (for Hugging Face Space)

## Original Project Information

# Todo Full-Stack Web Application (Hackathon Phase II)

## Project Description

A multi-user todo application with authentication, built during Hackathon Phase II. Demonstrates spec-driven development with subagent orchestration, scaling from console app (Phase I) to production full-stack web application.

## Features

### Authentication
- **User Registration** - Create accounts with email, name, and password
- **User Login** - Secure authentication with JWT tokens
- **Protected Routes** - Session-based access control

### Task Management
- **View Tasks** - Clean, responsive task list with completion status
- **Create Task** - Add tasks with title and optional description
- **Update Task** - Edit task details
- **Mark Complete/Incomplete** - Toggle task completion status
- **Delete Task** - Remove tasks with confirmation dialog

## Tech Stack

### Frontend
- **Framework**: Next.js 15+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Authentication**: Better Auth
- **State Management**: React Query (TanStack Query)
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI 0.115+
- **Language**: Python 3.13+
- **ORM**: SQLModel
- **Validation**: Pydantic
- **Authentication**: JWT (python-jose)
- **Password Hashing**: passlib with bcrypt

### Database
- **Provider**: Neon Serverless PostgreSQL 14+

## Getting Started

### Prerequisites

- Node.js 20+
- Python 3.13+
- Neon PostgreSQL database (or local PostgreSQL 14+)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. Create `.env` file from template:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env` with your configuration:
   - Set `DATABASE_URL` to your Neon PostgreSQL connection string
   - Set `JWT_SECRET` to a secure random string
   - Set `CORS_ORIGIN` to your frontend URL (default: http://localhost:3000)

6. Run the backend server:
   ```bash
   python -m uvicorn main:app --reload
   ```

   The API will be available at http://localhost:8000
   API documentation at http://localhost:8000/docs

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create `.env.local` file from template:
   ```bash
   cp .env.local.example .env.local
   ```

4. Edit `.env.local` with your configuration:
   - Set `NEXT_PUBLIC_API_URL` to your backend URL (default: http://localhost:8000)

5. Run the frontend development server:
   ```bash
   npm run dev
   ```

   The application will be available at http://localhost:3000

## Project Structure

```
todo-console-app/
├── frontend/                 # Next.js frontend application
│   ├── app/                  # App Router pages
│   │   ├── login/           # Login page
│   │   ├── signup/          # Signup page
│   │   └── tasks/           # Protected tasks page
│   ├── components/           # React components
│   │   ├── auth/            # Authentication components
│   │   ├── tasks/           # Task management components
│   │   ├── layout/          # Layout components
│   │   └── ui/              # shadcn/ui components
│   ├── lib/                  # Utility functions and configurations
│   ├── hooks/                # Custom React hooks
│   └── types/                # TypeScript type definitions
│
├── backend/                  # FastAPI backend application
│   ├── routes/               # API route handlers
│   │   ├── auth.py          # Authentication endpoints
│   │   └── tasks.py         # Task CRUD endpoints
│   ├── crud/                 # Database operations
│   ├── middleware/           # Custom middleware (JWT auth)
│   ├── utils/                # Utility functions
│   ├── models.py             # SQLModel data models
│   ├── schemas.py            # Pydantic schemas
│   ├── db.py                 # Database connection
│   └── main.py               # FastAPI application entry point
│
├── specs/                    # Feature specifications
│   └── 002-auth-todo-fullstack/
│       ├── spec.md           # Feature specification
│       ├── plan.md           # Architectural plan
│       ├── tasks.md          # Implementation tasks
│       └── data-model.md     # Data model documentation
│
├── .claude/                  # Claude Code configuration
└── .gitignore               # Git ignore rules
```

## API Endpoints

### Authentication (Public)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register a new user |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/auth/me` | Get current user info |

### Tasks (Protected - require JWT token)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{user_id}/tasks` | List all user's tasks |
| POST | `/api/{user_id}/tasks` | Create a new task |
| GET | `/api/{user_id}/tasks/{task_id}` | Get a single task |
| PUT | `/api/{user_id}/tasks/{task_id}` | Update a task |
| PATCH | `/api/{user_id}/tasks/{task_id}/complete` | Toggle task completion |
| DELETE | `/api/{user_id}/tasks/{task_id}` | Delete a task |

## Development

This project uses spec-driven development with subagent orchestration:

1. **Specify** (`/sp.specify`) - Create feature specifications
2. **Plan** (`/sp.plan`) - Create architectural plans
3. **Tasks** (`/sp.tasks`) - Generate implementation tasks
4. **Implement** (`/sp.implement`) - Execute tasks via subagents

## Deployment

### Frontend (Vercel)
- Connect repository to Vercel
- Configure environment variables in Vercel dashboard
- Vercel will automatically detect Next.js and deploy

### Backend (Hugging Face Spaces)
- Fork this repository to your Hugging Face account
- The space will automatically deploy with Gradio interface
- Configure secrets for API keys in Space settings

### Alternative Backend (Railway/Render/Heroku)
- Deploy the backend directory
- Set environment variables in your platform's dashboard
- Ensure `DATABASE_URL` points to your Neon PostgreSQL database

## User Stories (by Priority)

| Priority | User Story | Status |
|----------|------------|--------|
| P1 | New User Registration | To Do |
| P1 | User Login | To Do |
| P1 | View Tasks | To Do |
| P1 | Create Task | To Do |
| P2 | Update Task | To Do |
| P2 | Mark Complete/Incomplete | To Do |
| P2 | Delete Task | To Do |
| P2 | User Logout | To Do |

## Legacy (Phase I)

The Phase I console application is preserved in `src/main.py`. To run it:
```bash
python src/main.py
```

---

Built with Spec-Driven Development using Claude Code and subagent orchestration.