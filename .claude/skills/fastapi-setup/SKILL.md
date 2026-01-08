# FastAPI Project Setup Skill

## Purpose
Scaffold a production-ready FastAPI project with proper structure, middleware, and configuration.

## When to Use
- Starting a new FastAPI backend project
- Setting up project structure
- Configuring CORS, middleware, error handling
- Adding health check endpoints

## Prerequisites
- Python 3.13+ installed
- UV or pip package manager
- Project root directory created

## Instructions

### Step 1: Create Project Structure
See [structure.md](structure.md)

### Step 2: Create Main Application
See [structure.md](structure.md)

### Step 3: Create Configuration
See [structure.md](structure.md)

### Step 4: Create Environment Files
See [structure.md](structure.md)

### Step 5: Create Route Template
See [routes.md](routes.md)

### Step 6: Install Dependencies
See [structure.md](structure.md)

### Step 7: Create Run Script
See [structure.md](structure.md)

## Middleware
See [middleware.md](middleware.md)

## Testing Setup
`backend/tests/test_main.py`:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
```

Run tests:
```bash
pytest
```

## Validation Checklist
- [ ] Project structure created with all folders
- [ ] `main.py` with FastAPI app and middleware configured
- [ ] `config.py` with Pydantic settings
- [ ] `.env` and `.env.example` files created
- [ ] CORS configured for frontend URLs
- [ ] Health check endpoints working
- [ ] Route template created
- [ ] Dependencies installed
- [ ] App starts without errors: `python run.py`
- [ ] API docs accessible at `/docs`

## Output Files
- `backend/main.py` - FastAPI app
- `backend/config.py` - Configuration
- `backend/routes/` - Route handlers
- `backend/.env` - Environment variables
- `backend/pyproject.toml` - Dependencies

## Next Steps
After setup:
1. Use **REST API Generator** skill to create endpoints
2. Use **JWT Auth Middleware** skill to add authentication
3. Deploy with **Vercel Deployment** or **Docker** skills
