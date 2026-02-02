"""
Hugging Face Space wrapper for the Todo Chatbot API
This file runs FastAPI with uvicorn to keep the process alive for Hugging Face Spaces.
"""
import uvicorn
import os
from contextlib import asynccontextmanager
import sys

# Add the current directory to the path so we can import from main.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the core functionality from the existing modules
from main import app as fastapi_app

# Use SQLite for Hugging Face Spaces
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "sqlite:///./todo_hf_space.db"

# Hugging Face expects the app to be named 'app' in app.py
app = fastapi_app

# Health check for Hugging Face
@app.get("/")
async def root():
    return {
        "status": "running",
        "message": "Todo Backend API",
        "docs": "/docs"
    }

# Run FastAPI with uvicorn to keep the process alive
if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=7860,
        reload=False
    )