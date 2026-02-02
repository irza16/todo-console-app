"""
FastAPI application entry point for Todo Backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from config import settings
from db import create_db_and_tables
from routes import auth, tasks, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Create database tables
    create_db_and_tables()
    yield
    # Shutdown: Clean up if needed


# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="Full-Stack Todo Application Backend",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # ← Must include this for local dev
        "https://todo-console-app-orcin.vercel.app",
        *settings.cors_origin.split(",")  # Include any additional origins from settings
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "status": "ok",
        "message": "Todo API is running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
