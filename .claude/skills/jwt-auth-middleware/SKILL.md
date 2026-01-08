# JWT Auth Middleware Skill

## Purpose
Implement JWT token verification middleware in FastAPI to secure API endpoints and extract authenticated user information.

## When to Use
- Securing API endpoints
- Validating JWT tokens from frontend
- Extracting user ID from requests
- Implementing authorization logic

## Prerequisites
- FastAPI project set up
- Better Auth configured on frontend
- Secret key shared between frontend and backend

## Instructions

### Step 1: Install Dependencies
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

Or add to `pyproject.toml`:
```toml
[project]
dependencies = [
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
]
```

### Step 2: Create Auth Configuration
`backend/config.py` (add to existing):
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...
    
    # JWT Configuration
    SECRET_KEY: str  # Must match BETTER_AUTH_SECRET from frontend
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

settings = Settings()
```

### Step 3: Create JWT Utilities
`backend/utils/jwt.py`:
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status
from config import settings

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a new JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def decode_token(token: str) -> Optional[str]:
    """Decode token and extract user ID"""
    try:
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None
```

### Step 4: Create Auth Middleware
`backend/middleware/auth.py`:
```python
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from utils.jwt import decode_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Dependency to get current authenticated user ID from JWT token.
    Use this in route handlers that require authentication.
    """
    token = credentials.credentials
    
    user_id = decode_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id

async def get_current_user_optional(
    request: Request
) -> Optional[str]:
    """
    Optional authentication - returns user ID if token is valid,
    None if no token or invalid token.
    Use for endpoints that work with or without authentication.
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.replace("Bearer ", "")
    return decode_token(token)

def verify_user_access(requested_user_id: str, token_user_id: str):
    """
    Verify that the authenticated user is requesting their own data.
    Raises 403 if user tries to access another user's data.
    """
    if requested_user_id != token_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
```

### Step 5: Update Routes with Auth
`backend/routes/tasks.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from db import get_session
from models import Task, TaskCreate, TaskRead, TaskUpdate
from middleware.auth import get_current_user, verify_user_access

router = APIRouter()

@router.get("/{user_id}/tasks", response_model=List[TaskRead])
async def list_tasks(
    user_id: str,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List all tasks for authenticated user"""
    # Verify user is accessing their own data
    verify_user_access(user_id, current_user)
    
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()
    
    return tasks

@router.post("/{user_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task: TaskCreate,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new task for authenticated user"""
    verify_user_access(user_id, current_user)
    
    db_task = Task.model_validate(task, update={"user_id": user_id})
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    
    return db_task

@router.get("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a specific task by ID"""
    verify_user_access(user_id, current_user)
    
    task = session.get(Task, task_id)
    
    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task

@router.put("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    user_id: str,
    task_id: int,
    task_update: TaskUpdate,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a task"""
    verify_user_access(user_id, current_user)
    
    db_task = session.get(Task, task_id)
    
    if not db_task or db_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    
    return db_task

@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a task"""
    verify_user_access(user_id, current_user)
    
    task = session.get(Task, task_id)
    
    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    session.delete(task)
    session.commit()
```

### Step 6: Create Auth Routes (Login/Signup)
`backend/routes/auth.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from db import get_session
from models import User
from utils.jwt import create_access_token

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    user: dict
    token: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/signup", response_model=AuthResponse)
async def signup(
    data: SignupRequest,
    session: Session = Depends(get_session)
):
    """Create a new user account"""
    # Check if user exists
    existing_user = session.exec(
        select(User).where(User.email == data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=data.email,
        name=data.name,
        hashed_password=hash_password(data.password)
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Create JWT token
    token = create_access_token(data={"sub": user.id})
    
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        },
        "token": token
    }

@router.post("/login", response_model=AuthResponse)
async def login(
    data: LoginRequest,
    session: Session = Depends(get_session)
):
    """Login with email and password"""
    # Find user
    user = session.exec(
        select(User).where(User.email == data.email)
    ).first()
    
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create JWT token
    token = create_access_token(data={"sub": user.id})
    
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        },
        "token": token
    }

@router.get("/me")
async def get_current_user_info(
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get current authenticated user info"""
    user = session.get(User, current_user)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name
    }
```

### Step 7: Update User Model
`backend/models.py` (add password field):
```python
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    hashed_password: str = Field(max_length=255)  # Add this
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Step 8: Environment Variables
`.env`:
```env
# Must match BETTER_AUTH_SECRET from frontend
SECRET_KEY=your-super-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

## Testing Auth Flow

### Test 1: Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","name":"Test User"}'
```

Expected: `{"user":{...},"token":"eyJ..."}`

### Test 2: Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

Expected: `{"user":{...},"token":"eyJ..."}`

### Test 3: Protected Endpoint
```bash
curl http://localhost:8000/api/user123/tasks \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Expected: List of tasks or 401 if token invalid

### Test 4: Wrong User Access
```bash
curl http://localhost:8000/api/different_user/tasks \
  -H "Authorization: Bearer USER123_TOKEN"
```

Expected: 403 Forbidden

## Validation Checklist
- [ ] JWT dependencies installed
- [ ] SECRET_KEY matches frontend
- [ ] Signup creates user and returns token
- [ ] Login verifies password and returns token
- [ ] Protected routes require valid token
- [ ] Invalid token returns 401
- [ ] User can only access their own data (403 for others)
- [ ] Token expiration works
- [ ] Password hashing working

## Common Issues

### Issue: "401 Unauthorized" on valid token
**Solution:** Verify SECRET_KEY matches between frontend and backend

### Issue: "Token expired"
**Solution:** Increase ACCESS_TOKEN_EXPIRE_MINUTES or refresh token

### Issue: "User can access other users' data"
**Solution:** Ensure verify_user_access() is called in all routes

## Security Best Practices
- ✅ Never log or expose SECRET_KEY
- ✅ Use HTTPS in production
- ✅ Hash passwords with bcrypt
- ✅ Set appropriate token expiration
- ✅ Validate user_id matches token user_id
- ✅ Use rate limiting on auth endpoints

## Output Files
- `utils/jwt.py` - JWT utilities
- `middleware/auth.py` - Auth dependencies
- `routes/auth.py` - Auth endpoints
- Updated `routes/tasks.py` with auth
- Updated `models.py` with password field

## Next Steps
After JWT middleware:
1. Test full auth flow (signup → login → access data)
2. Add password reset functionality
3. Implement token refresh mechanism
4. Add rate limiting on auth endpoints