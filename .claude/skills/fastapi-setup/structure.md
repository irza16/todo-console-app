# FastAPI Project Structure

## Create Project Structure
```bash
backend/
├── main.py              # FastAPI application entry point
├── db.py               # Database configuration
├── models.py           # SQLModel database models
├── config.py           # Application configuration
├── routes/             # API route handlers
│   ├── __init__.py
│   ├── tasks.py
│   └── auth.py
├── services/           # Business logic
│   ├── __init__.py
│   └── task_service.py
├── middleware/         # Custom middleware
│   ├── __init__.py
│   └── auth.py
├── utils/              # Utility functions
│   ├── __init__.py
│   └── helpers.py
├── tests/              # Test files
│   ├── __init__.py
│   └── test_tasks.py
├── .env                # Environment variables
├── .env.example        # Environment template
├── pyproject.toml      # Dependencies
└── README.md           # Documentation
```

## Main Application
`backend/main.py`:

```python
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from db import create_db_and_tables, test_connection
from routes import tasks, auth
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    print("🚀 Starting FastAPI application...")
    create_db_and_tables()
    test_connection()
    yield
    # Shutdown
    print("👋 Shutting down FastAPI application...")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        },
    )

# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "version": settings.APP_VERSION}

@app.get("/health/ready")
async def readiness_check():
    """Check if app is ready to serve traffic"""
    db_healthy = test_connection()
    return {
        "status": "ready" if db_healthy else "not_ready",
        "database": "connected" if db_healthy else "disconnected"
    }

# Include routers
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }
```

## Configuration
`backend/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    """Application settings"""

    # App Info
    APP_NAME: str = "Todo API"
    APP_DESCRIPTION: str = "Todo application REST API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings()
```

## Environment Files
`.env.example`:

```env
# Application
APP_NAME="Todo API"
APP_VERSION="2.0.0"
DEBUG=true

# Database
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=true

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

`.env` (copy from .env.example and fill in actual values)

## Dependencies
`pyproject.toml`:

```toml
[project]
name = "todo-backend"
version = "2.0.0"
description = "Todo application backend API"
requires-python = ">=3.13"

dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlmodel>=0.0.22",
    "psycopg2-binary>=2.9.9",
    "python-dotenv>=1.0.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.6.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    
    "python-multipart>=0.0.9",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "httpx>=0.27.0",
    "pytest-asyncio>=0.24.0",
]
```

Install:
```bash
uv pip install -e .
# Or for development
uv pip install -e ".[dev]"
```

## Run Script
`backend/run.py`:

```python
import uvicorn
from config import settings

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info"
    )
```

Run with:
```bash
python run.py
```
