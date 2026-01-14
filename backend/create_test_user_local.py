#!/usr/bin/env python3
"""
Script to create a test user in the local database that the backend uses.
"""
import os
import sys
from pathlib import Path

# Add backend to path to import modules
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from sqlmodel import SQLModel, create_engine, Session
from backend.models import User
from backend.utils.password import hash_password
from backend.db import settings

def create_local_test_user():
    """Create a test user in the database using the same settings as the backend."""
    # Use the same database URL as configured in settings
    # Since we created .env.local, it should use the local SQLite
    from backend.db import engine

    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Create a test user
    password_hash = hash_password("testpassword123")

    with Session(engine) as session:
        # Check if user already exists
        existing_user = session.query(User).filter(User.email == "test@example.com").first()

        if existing_user:
            print(f"Test user already exists with ID: {existing_user.id}")
            return existing_user.id

        # Create new user
        user = User(
            email="test@example.com",
            name="Test User",
            password_hash=password_hash
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        print(f"Test user created successfully with ID: {user.id}")
        return user.id

if __name__ == "__main__":
    print("Creating test user in local database...")
    user_id = create_local_test_user()

    print(f"\nTest user created with ID: {user_id}")
    print("You can now use this user ID in the frontend.")
    print(f"API endpoints will be like: /api/{user_id}/tasks")