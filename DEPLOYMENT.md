# Deployment Guide: Vercel Serverless

This guide covers deploying the entire Todo application (frontend + backend) to **Vercel** using serverless functions.

## Architecture

```
Frontend (Next.js)  →  Backend (FastAPI Serverless)  →  Database (Neon PostgreSQL)
      Vercel                     Vercel                        Neon
```

**Benefits:**
- ✅ **Single platform** - everything on Vercel
- ✅ **Completely free** - generous free tier
- ✅ **Auto HTTPS** - SSL included
- ✅ **Auto scaling** - handles traffic automatically
- ✅ **GitHub integration** - auto-deploy on push
- ✅ **No server management**

## Prerequisites

1. GitHub repository with your code
2. Neon PostgreSQL account (database)
3. Vercel account (sign up at [vercel.com](https://vercel.com))

---

## Step 1: Create Neon Database

### 1.1. Sign up for Neon
- Go to [neon.tech](https://neon.tech)
- Click "Sign up" with GitHub or email

### 1.2. Create a new project
1. Click "New Project"
2. Choose a name: `todo-db`
3. Select a region (choose closest to you)
4. Click "Create Project"

### 1.3. Get connection string
1. Your project dashboard will show a connection string
2. Copy the **Connection string** (looks like `postgresql://...`)
3. Keep this safe - you'll need it for Vercel

**Connection string format:**
```
postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
```

---

## Step 2: Deploy to Vercel

### 2.1. Create Vercel account
- Go to [vercel.com](https://vercel.com)
- Click "Sign up"
- Choose **Sign up with GitHub** (recommended)

### 2.2. Import your repository
1. Click "Add New..." → "Project"
2. Select your GitHub repository
3. Vercel will detect your Next.js project

### 2.3. Configure project settings

**Project Settings:**
- **Project Name**: `todo-app` (or your preferred name)
- **Framework Preset**: Next.js
- **Root Directory**: `.` (root of repo)

### 2.4. Add Environment Variables

Go to **Environment Variables** section and add:

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `your_neon_connection_string` | PostgreSQL connection from Step 1 |
| `JWT_SECRET` | `random_32_char_string` | Generate a secure random string |
| `JWT_ALGORITHM` | `HS256` | Keep as is |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token expiry (24 hours) |
| `CORS_ORIGIN` | `https://your-app-name.vercel.app` | Will update after first deploy |

**How to generate JWT_SECRET:**
```bash
# In terminal
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.5. Update CORS_ORIGIN after deployment

**Important**: After your first deploy, update `CORS_ORIGIN`:
1. Deploy once to get your Vercel URL
2. Go back to Environment Variables
3. Update `CORS_ORIGIN` to your actual URL: `https://your-app.vercel.app`
4. Click "Redeploy"

---

## Step 3: How It Works

### File Structure
```
your-repo/
├── frontend/                    # Next.js frontend
│   ├── app/                    # App directory
│   ├── components/             # React components
│   ├── api/                    # Serverless API functions
│   │   ├── index.py            # FastAPI + Mangum entry point
│   │   └── requirements.txt    # Python dependencies
│   ├── package.json
│   └── vercel.json             # Vercel configuration
├── backend/                    # FastAPI source code
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── routes/                 # API routes
│   ├── utils/
│   └── middleware/
├── .env.example                # Environment variables template
└── README.md
```

### How Serverless Works

1. **Frontend** runs as static pages + Next.js server
2. **Backend** runs as serverless functions under `/api/*`
3. When frontend calls `/api/auth/login`, Vercel runs `api/index.py`
4. Mangum adapts FastAPI to work with Vercel's serverless runtime
5. Database connection is made per-request (stateless)

---

## Step 4: First Deploy

1. Click **"Deploy"** in Vercel
2. Wait for build to complete (~2-3 minutes)
3. You'll get a URL like: `https://your-app.vercel.app`
4. Visit the URL and test:
   - You should see the login page
   - Sign up with a new account
   - Create a task
   - Mark task complete
   - Delete task
   - Logout

---

## Step 5: Verify Everything Works

### Check Backend Health
Visit: `https://your-app.vercel.app/api/health`

Expected response:
```json
{"status": "healthy"}
```

### Check API Docs
Visit: `https://your-app.vercel.app/api/docs`

You should see the FastAPI Swagger UI.

### Test Authentication
1. Open browser dev tools (F12)
2. Go to Network tab
3. Sign up for an account
4. Check that `/api/auth/signup` returns 200 with token

---

## Step 6: Update CORS (Critical)

After your first deploy, you **must** update CORS_ORIGIN:

1. Go to Vercel dashboard → your project
2. Settings → Environment Variables
3. Find `CORS_ORIGIN`
4. Update to your actual Vercel URL:
   ```
   CORS_ORIGIN=https://your-app-name.vercel.app
   ```
5. Click "Save"
6. Click "Redeploy" in the Deployments tab

**Why this matters:** The backend needs to know which domain is allowed to make API requests. Without this, you'll get CORS errors.

---

## Troubleshooting

### Issue: CORS errors in browser console

**Symptom:** Network requests show CORS error
**Fix:**
- Update `CORS_ORIGIN` environment variable
- Make sure it matches your exact Vercel URL
- Include `https://` and no trailing slash

### Issue: Database connection failed

**Symptom:** 500 error on API calls
**Fix:**
- Verify `DATABASE_URL` is correct
- Make sure it includes `?sslmode=require`
- Check Neon database is running

### Issue: Module not found

**Symptom:** Build error about missing modules
**Fix:**
- Check `frontend/api/requirements.txt` has all dependencies
- Vercel auto-installs from this file

### Issue: 404 on API calls

**Symptom:** `/api/auth/login` returns 404
**Fix:**
- Check `vercel.json` has correct routes
- Verify `frontend/api/index.py` exists
- Check Vercel function logs

### Issue: "Cold start" delay

**Symptom:** First API call takes 2-3 seconds
**Fix:**
- This is normal for serverless
- Subsequent calls are fast
- Vercel keeps functions warm for active apps

---

## Environment Variables Reference

| Variable | Value | Notes |
|----------|-------|-------|
| `DATABASE_URL` | `postgresql://...` | Get from Neon |
| `JWT_SECRET` | `random_string_32_chars` | Generate with Python secrets |
| `JWT_ALGORITHM` | `HS256` | Don't change |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | 24 hours in minutes |
| `CORS_ORIGIN` | `https://your-app.vercel.app` | Update after first deploy |

---

## Local Development

To run locally with the serverless setup:

```bash
# Terminal 1 - Frontend
cd frontend
npm install
npm run dev

# Terminal 2 - Backend (use backend directory)
cd backend
python3 -m uvicorn main:app --reload
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local` for local backend.

---

## GitHub Integration

Vercel automatically deploys when you push to GitHub:

1. Make changes to your code
2. Commit and push:
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```
3. Vercel auto-deploys
4. Visit the new URL in Deployments tab

---

## Free Tier Limits

**Vercel Free Tier:**
- 100GB bandwidth/month
- 6,000 minutes of execution time/month
- Unlimited deployments
- Auto HTTPS
- CDN included

**Your Todo App Usage:**
- Each API call: ~100ms execution time
- 10,000 API calls = ~17 minutes of execution time
- Well within free tier limits

---

## Post-Deployment Checklist

- [ ] Neon database created
- [ ] Connection string copied
- [ ] Vercel project created
- [ ] Environment variables added
- [ ] First deployment successful
- [ ] Frontend loads without errors
- [ ] `/api/health` returns `{"status":"healthy"}`
- [ ] `/api/docs` shows Swagger UI
- [ ] Signup works with valid credentials
- [ ] Login works with registered user
- [ ] Tasks can be created
- [ ] Tasks can be edited
- [ ] Tasks can be marked complete
- [ ] Tasks can be deleted
- [ ] Logout clears authentication
- [ ] No CORS errors in console
- [ ] `CORS_ORIGIN` updated to production URL
- [ ] GitHub auto-deploy works

---

## Files Explained

### `frontend/api/index.py`
- Entry point for serverless function
- Imports FastAPI app and wraps it with Mangum
- Mangum adapts FastAPI for AWS Lambda/Vercel runtime

### `frontend/api/requirements.txt`
- Python dependencies for serverless function
- Includes Mangum for FastAPI adaptation

### `frontend/vercel.json`
- Vercel configuration
- Defines routes, runtime, and function settings

### `backend/`
- All your FastAPI source code
- Imported by `api/index.py` via sys.path

---

## Alternative: Separate Backend Deployment

If you ever need a dedicated backend server, see `DEPLOYMENT_KOYEB.md` for Koyeb/Render deployment options.
