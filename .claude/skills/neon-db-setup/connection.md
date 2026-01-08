# Neon Database Connection

## Get Connection String
1. Log in to Neon dashboard
2. Navigate to your database
3. Copy the connection string (it should look like):
   ```
   postgresql://username:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```

## Environment Configuration
Create `.env` in backend root:

```env
# Neon Database Configuration
DATABASE_URL=postgresql://username:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require

# Connection Pool Settings (optional)
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

## Database Configuration File
Create `backend/db.py`:

```python
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_size=int(os.getenv("DB_POOL_SIZE", 10)),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", 20)),
    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", 30)),
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", 3600)),
)

def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session for dependency injection"""
    with Session(engine) as session:
        yield session
```

## Health Check Endpoint
In `backend/main.py`:

```python
from fastapi import FastAPI
from db import test_connection, create_db_and_tables

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    create_db_and_tables()
    test_connection()

@app.get("/health/db")
async def db_health_check():
    """Check database health"""
    is_healthy = test_connection()
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "database": "neon-postgresql"
    }
```

## Common Issues & Solutions

### Issue: "SSL connection required"
**Solution:** Add `?sslmode=require` to connection string

### Issue: "Connection pool exhausted"
**Solution:** Increase `DB_POOL_SIZE` and `DB_MAX_OVERFLOW`

### Issue: "Connection timeout"
**Solution:** Check network connectivity, increase `DB_POOL_TIMEOUT`

### Issue: "Database does not exist"
**Solution:** Verify database name in Neon dashboard matches connection string
