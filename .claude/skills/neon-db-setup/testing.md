# Neon Database Testing

## Test Connection Function
Add to `backend/db.py`:

```python
def test_connection():
    """Test database connectivity"""
    try:
        with Session(engine) as session:
            session.exec("SELECT 1")
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
```

## Manual Testing
Test the connection from command line:

```bash
python -c "from db import test_connection; test_connection()"
```

Should output: `✅ Database connection successful!`

## Health Check Endpoint

Access the health check endpoint:
```bash
curl http://localhost:8000/health/db
```

Expected response:
```json
{
  "status": "healthy",
  "database": "neon-postgresql"
}
```

## Validation Checklist
- [ ] DATABASE_URL is set in .env
- [ ] Connection string includes `?sslmode=require`
- [ ] `db.py` file created with engine configuration
- [ ] Health check endpoint returns success
- [ ] Can execute test query: `SELECT 1`
- [ ] No connection errors in logs

## Output Files
- `backend/.env` - Environment variables
- `backend/db.py` - Database configuration
- `backend/main.py` - FastAPI app with health check
