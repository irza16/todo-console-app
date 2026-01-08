# Neon DB Setup Skill

## Purpose
Configure Neon Serverless PostgreSQL database connection for the project.

## When to Use
- Setting up a new project with Neon database
- Configuring database connection in backend
- Testing database connectivity
- Setting up connection pooling

## Prerequisites
- Neon account created at neon.tech
- Database created in Neon dashboard
- Connection string available

## Instructions

### Step 1: Get Connection String
See [connection.md](connection.md)

### Step 2: Create Environment File
See [connection.md](connection.md)

### Step 3: Create Database Configuration File
See [connection.md](connection.md)

### Step 4: Add Connection Test Endpoint
See [connection.md](connection.md)

### Step 5: Install Dependencies
```bash
pip install sqlmodel psycopg2-binary python-dotenv
```

Or add to `pyproject.toml`:
```toml
[project]
dependencies = [
    "sqlmodel>=0.0.14",
    "psycopg2-binary>=2.9.9",
    "python-dotenv>=1.0.0",
]
```

## Testing
See [testing.md](testing.md)

## Next Steps
After setting up Neon DB:
1. Use **SQLModel Schema Generator** skill to create models
2. Use **Database Migration Manager** skill for schema changes
3. Implement CRUD operations with the database session
