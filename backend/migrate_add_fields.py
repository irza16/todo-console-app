#!/usr/bin/env python3
"""
Migration script to add new fields to existing task table
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_database():
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found in environment variables")
        return False

    print(f"Migrating database: {database_url}")

    # Create engine and connect
    engine = create_engine(database_url)

    # SQL statements to add missing columns
    alter_statements = [
        "ALTER TABLE task ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'Medium';",
        "ALTER TABLE task ADD COLUMN IF NOT EXISTS tags TEXT;",
        "ALTER TABLE task ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE task ADD COLUMN IF NOT EXISTS recurrence_pattern VARCHAR(20);"
    ]

    try:
        with engine.connect() as conn:
            transaction = conn.begin()

            for statement in alter_statements:
                print(f"Executing: {statement}")
                conn.execute(text(statement))

            transaction.commit()
            print("Migration completed successfully!")
            return True

    except Exception as e:
        print(f"Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    migrate_database()