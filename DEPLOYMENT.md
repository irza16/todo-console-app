# Deployment Guide

This guide covers deploying the Todo App to production with Vercel (frontend) and Koyeb (backend).

## Architecture

```
Frontend (Next.js)  →  Backend (FastAPI)  →  Database (Neon PostgreSQL)
    Vercel                  Koyeb                  Neon
```

## Prerequisites

1. GitHub repository with your code
2. Neon PostgreSQL account (database)
3. Vercel account (frontend deployment)
4. Koyeb account (backend deployment)

---

## Step 1: Deploy Backend to Koyeb

### 1.1. Create Koyeb Account
- Go to [koyeb.com](https://koyeb.com)
- Sign up with GitHub

### 1.2. Create a New Service

1. Click "Create Service" in the Koyeb dashboard
2. Select your GitHub repository
3. Configure the service:

**Service Details**:
- **Name**: todo-backend
- **Region**: Choose nearest region
- **App Type**: Docker

**Docker Configuration**:

Create `backend/Dockerfile` if not exists:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Root Directory**: Set to `backend`

**Environment Variables**:

Go to the Environment tab and add:

```bash
# Database
DATABASE_URL=your_neon_database_url

# JWT
JWT_SECRET=your_secure_random_secret_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS (will be updated after frontend deployment)
CORS_ORIGIN=https://your-frontend-domain.vercel.app
```

4. Click "Deploy"

### 1.3. Get Backend URL

After deployment, Koyeb will provide a public URL like:
```
https://your-app-name.koyeb.app
```

Note this down - you'll need it for the frontend.

---

## Step 2: Deploy Frontend to Vercel

### 2.1. Create Vercel Account
- Go to [vercel.com](https://vercel.com)
- Sign up with GitHub

### 2.2. Deploy from GitHub
- Click "Add New..." → "Project"
- Select your GitHub repository
- Vercel will detect the Next.js project

### 2.3. Configure Project Settings

**Root Directory**: Set to `frontend`

**Framework Preset**: Next.js (auto-detected)

**Environment Variables**:
- Go to Settings → Environment Variables
- Add:
  ```
  NEXT_PUBLIC_API_URL=https://your-backend-domain.koyeb.app
  ```

### 2.4. Deploy

Click "Deploy" and wait for the build to complete.

You'll get a URL like:
```
https://your-app-name.vercel.app
```

---

## Step 3: Update CORS and Environment Variables

### 3.1. Update Backend CORS

Go back to Koyeb → your service → Environment tab:
```bash
CORS_ORIGIN=https://your-frontend-domain.vercel.app
```

### 3.2. Redeploy Backend

Click "Redeploy" on your Koyeb service.

### 3.3. Test

Visit your Vercel URL and test:
- Signup
- Login
- Create task
- Delete task
- Mark complete

---

## Quick Deployment Checklist

### Backend (Koyeb)
- [ ] Create service from GitHub repo
- [ ] Set root directory to `backend`
- [ ] Add `DATABASE_URL` (Neon)
- [ ] Add `JWT_SECRET` (generate a secure string)
- [ ] Add `CORS_ORIGIN` (Vercel URL)
- [ ] Deploy and get public URL

### Frontend (Vercel)
- [ ] Connect GitHub repo
- [ ] Set root directory to `frontend`
- [ ] Add `NEXT_PUBLIC_API_URL` (Koyeb URL)
- [ ] Deploy and get public URL
- [ ] Test the full app

---

## Troubleshooting

### CORS Errors

1. Make sure `CORS_ORIGIN` in backend matches your Vercel URL exactly
2. Include protocol (`https://`) and no trailing slash
3. For local testing, use: `CORS_ORIGIN=http://localhost:3000`

### Database Connection Issues

1. Verify `DATABASE_URL` is correct
2. Make sure Neon database is running
3. Check Koyeb logs for connection errors

### 404 Errors

1. Verify frontend `NEXT_PUBLIC_API_URL` points to the correct backend URL
2. Check Network tab in browser dev tools for actual request URLs

### Koyeb Build Issues

1. Make sure `backend/requirements.txt` exists
2. Ensure `backend/Dockerfile` exists
3. Check logs for specific error messages

---

## Environment Variable Reference

### Backend (Koyeb)
```bash
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
JWT_SECRET=random_string_min_32_chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGIN=https://your-frontend.vercel.app
```

### Frontend (Vercel)
```bash
NEXT_PUBLIC_API_URL=https://your-backend.koyeb.app
```

---

## Files Created

- `backend/Dockerfile` - Docker configuration for Koyeb
- `backend/requirements.txt` - Python dependencies
- `backend/.env.example` - Environment variables template

---

## Post-Deployment Checklist

- [ ] Backend URL is accessible and returns 200 at `/`
- [ ] Frontend URL loads without errors
- [ ] Signup works with valid credentials
- [ ] Login works with registered user
- [ ] Tasks can be created
- [ ] Tasks can be edited
- [ ] Tasks can be marked complete
- [ ] Tasks can be deleted
- [ ] Logout clears authentication
- [ ] No CORS errors in browser console
- [ ] No API errors in Koyeb logs
