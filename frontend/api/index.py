"""
Vercel Serverless Function entry point for FastAPI backend.
This file serves as the bridge between Vercel's serverless runtime and FastAPI.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from config import settings
from db import create_db_and_tables
from routes import auth, tasks

# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="Full-Stack Todo Application Backend (Vercel Serverless)",
    version="0.1.0",
    lifespan=None,  # Disable lifespan for serverless (tables created manually)
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS - allow Vercel preview domains and production
cors_origins = [
    "http://localhost:3000",
    settings.cors_origin,
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Create database tables on startup."""
    try:
        create_db_and_tables()
    except Exception as e:
        print(f"Database initialization warning: {e}")

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "status": "ok",
        "message": "Todo API is running on Vercel Serverless",
        "docs": "/docs",
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Vercel serverless handler
from mangum import Mangum
handler = Mangum(app)
