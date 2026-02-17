---
id: 001
title: Phase 4 Tasks
stage: tasks
date: 2026-02-06
surface: agent
model: google/gemini-2.0-flash-exp:free
feature: kubernetes-deployment
branch: 005-kubernetes-deployment
user: irza
command: sp.tasks
labels: [kubernetes, deployment, docker, helm, minikube]
links:
  spec: specs/005-kubernetes-deployment/spec.md
  plan: specs/005-kubernetes-deployment/plan.md
  tasks: specs/005-kubernetes-deployment/tasks.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-kubernetes-deployment/tasks.md
tests:
  - task generation validation
  - dependency mapping
  - parallel execution identification
---

## Prompt

```text
# Phase 4 Tasks: Kubernetes Deployment Implementation

## Task Organization

Tasks are organized into logical groups and numbered sequentially. Each task is atomic, testable, and maps back to the specification and plan.

**Priority Levels:**
- **P0**: Critical path - must complete
- **P1**: High priority - should complete
- **P2**: Medium priority - nice to have
- **P3**: Low priority - optional

**Status:**
- ⬜ Not Started
- 🟡 In Progress
- ✅ Complete
- ❌ Blocked

---

## Group 1: Environment Setup (P0)

### T-001: Install Required Tools
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** None

**Description:**
Install all required tools for Kubernetes development and deployment.

**Acceptance Criteria:**
- Docker Desktop 4.53+ is installed and running
- Minikube is installed (latest stable version)
- kubectl is installed and working
- Helm 3.x is installed
- All tools return version when run with `--version`

**Implementation Steps:**
1. Download and install Docker Desktop from https://www.docker.com/products/docker-desktop
2. Start Docker Desktop and verify it's running
3. Install Minikube: `brew install minikube` (macOS) or follow OS-specific guide
4. Install kubectl: `brew install kubectl` or download from kubernetes.io
5. Install Helm: `brew install helm` or download from helm.sh
6. Verify installations:
   ```bash
   docker --version
   minikube version
   kubectl version --client
   helm version
   ```

**Testing:**
```bash
# All commands should return version info
docker --version
minikube version
kubectl version --client
helm version
```

**References:**
- Spec: Technical Requirements > Tool Dependencies
- Plan: Build and Deployment Workflow

---

### T-002: Start Minikube Cluster
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** T-001

**Description:**
Start a local Minikube Kubernetes cluster with appropriate resources.

**Acceptance Criteria:**
- Minikube cluster starts successfully
- Cluster has at least 4GB RAM and 2 CPUs allocated
- kubectl can connect to cluster
- Cluster info displays correctly

**Implementation Steps:**
1. Start Minikube with resource allocation:
   ```bash
   minikube start --cpus=4 --memory=4096 --driver=docker
   ```
2. Wait for cluster to be ready
3. Verify cluster status:
   ```bash
   minikube status
   kubectl cluster-info
   kubectl get nodes
   ```

**Testing:**
```bash
# Should show running cluster
minikube status

# Should show cluster endpoints
kubectl cluster-info

# Should show node in Ready state
kubectl get nodes
```

**References:**
- Spec: US-4.7 Developer Deploys to Minikube
- Plan: Phase 3: Deployment to Minikube

---

### T-003: Configure Docker for Minikube
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 10 minutes
**Dependencies:** T-002

**Description:**
Configure Docker to use Minikube's Docker daemon so images built locally are available to Kubernetes.

**Acceptance Criteria:**
- Docker commands point to Minikube's daemon
- Can build and see images in Minikube
- Environment variable DOCKER_HOST is set correctly

**Implementation Steps:**
1. Run: `eval $(minikube docker-env)`
2. Verify Docker is using Minikube:
   ```bash
   docker ps
   # Should show Minikube system containers
   ```
3. Add to shell profile for persistence (optional):
   ```bash
   echo 'eval $(minikube docker-env)' >> ~/.zshrc
   ```

**Testing:**
```bash
# Should show Minikube containers
docker ps | grep k8s

# Build test image
docker build -t test:latest - <<EOF
FROM alpine
CMD echo "Hello from Minikube Docker"
EOF

# Verify image exists
docker images | grep test
```

**References:**
- Plan: Build and Deployment Workflow > Step 3: Load Images into Minikube

---

## Group 2: Frontend Containerization (P0)

### T-004: Create Frontend Dockerfile
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 1 hour
**Dependencies:** None

**Description:**
Create a multi-stage Dockerfile for the Next.js frontend application.

**Acceptance Criteria:**
- File exists at `frontend/Dockerfile`
- Uses node:20-alpine base image
- Implements multi-stage build (builder + runner)
- Runs as non-root user
- Exposes port 3000
- Image builds successfully without errors

**Implementation Steps:**
1. Create `frontend/Dockerfile` with multi-stage build:
   - Stage 1 (builder): Install deps, build Next.js
   - Stage 2 (runner): Copy built files, configure production
2. Configure non-root user (node)
3. Set working directory to /app
4. Copy package files and install dependencies
5. Build Next.js app
6. Expose port 3000
7. Set CMD to start production server

**File Location:** `frontend/Dockerfile`

**Template Structure:**
```dockerfile
# Stage 1: Dependencies and build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production runtime
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
# Copy necessary files
# Configure user
# Expose port
# Start server
```

**Testing:**
```bash
cd frontend
docker build -t todo-frontend:test .
# Should complete without errors
```

**References:**
- Spec: US-4.1 Developer Containerizes Frontend
- Plan: Component Design > 1.1 Frontend Image

---

### T-005: Create Frontend .dockerignore
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 10 minutes
**Dependencies:** T-004

**Description:**
Create .dockerignore file to exclude unnecessary files from Docker build context.

**Acceptance Criteria:**
- File exists at `frontend/.dockerignore`
- Excludes node_modules, .git, .next, build artifacts
- Reduces build context size significantly
- Docker build is faster

**Implementation Steps:**
1. Create `frontend/.dockerignore`
2. Add exclusions:
   - node_modules
   - .next
   - .git
   - .env*.local
   - *.md (except README if needed)
   - coverage
   - .vscode

**File Location:** `frontend/.dockerignore`

**Content:**
```
node_modules
.next
.git
.gitignore
.env*.local
*.md
coverage
.vscode
.idea
*.log
dist
build
```

**Testing:**
```bash
# Build should be faster (less context)
cd frontend
time docker build -t todo-frontend:test .
```

**References:**
- Plan: Performance Optimization > Docker Image Optimization

---

### T-006: Add Frontend Health Check Endpoint
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** None

**Description:**
Create a health check API route in Next.js that returns 200 OK.

**Acceptance Criteria:**
- Route exists at `app/api/health/route.ts`
- Returns 200 status code
- Returns JSON with status and timestamp
- Works in both dev and production modes

**Implementation Steps:**
1. Create directory: `frontend/app/api/health/`
2. Create file: `route.ts`
3. Implement GET handler:
   ```typescript
   export async function GET() {
     return Response.json({
       status: 'healthy',
       timestamp: new Date().toISOString()
     });
   }
   ```

**File Location:** `frontend/app/api/health/route.ts`

**Testing:**
```bash
# Start dev server
npm run dev

# Test endpoint
curl http://localhost:3000/api/health
# Should return: {"status":"healthy","timestamp":"..."}
```

**References:**
- Spec: US-4.1 Acceptance Criteria > Health check endpoint
- Plan: Health Checks > Frontend Health Endpoint

---

### T-007: Build Frontend Docker Image
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** T-004, T-005, T-006

**Description:**
Build the frontend Docker image and verify it works correctly.

**Acceptance Criteria:**
- Image builds successfully
- Image size is under 500MB
- Image is tagged as `todo-frontend:latest`
- Image is available in Minikube

**Implementation Steps:**
1. Ensure Docker is using Minikube daemon: `eval $(minikube docker-env)`
2. Build image:
   ```bash
   cd frontend
   docker build -t todo-frontend:latest .
   ```
3. Verify image exists:
   ```bash
   docker images | grep todo-frontend
   ```

**Testing:**
```bash
# Check image size
docker images todo-frontend:latest
# Size column should show < 500MB

# Verify image is in Minikube
minikube ssh -- docker images | grep todo-frontend
```

**References:**
- Spec: US-4.1 > Image size is under 500MB
- Plan: Phase 1: Containerization > Step 1: Build Docker Images

---

### T-008: Test Frontend Container Locally
**Priority:** P1
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-007

**Description:**
Run the frontend container locally and verify it works correctly.

**Acceptance Criteria:**
- Container starts without errors
- Application is accessible at http://localhost:3000
- Health check endpoint returns 200
- Pages load correctly
- No console errors

**Implementation Steps:**
1. Run container:
   ```bash
   docker run -p 3000:3000 \
     -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
     todo-frontend:latest
   ```
2. Open browser to http://localhost:3000
3. Verify pages load
4. Check health endpoint: `curl http://localhost:3000/api/health`
5. Stop container: Ctrl+C

**Testing:**
```bash
# Start container
docker run -d -p 3000:3000 --name test-frontend todo-frontend:latest

# Check health
curl http://localhost:3000/api/health

# Check logs
docker logs test-frontend

# Cleanup
docker stop test-frontend
docker rm test-frontend
```

**References:**
- Spec: US-4.3 Developer Tests Containers Locally
- Plan: Phase 1 > Step 2: Test Containers Locally

---

## Group 3: Backend Containerization (P0)

### T-009: Create Backend Dockerfile
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 1 hour
**Dependencies:** None

**Description:**
Create a multi-stage Dockerfile for the FastAPI backend application.

**Acceptance Criteria:**
- File exists at `backend/Dockerfile`
- Uses python:3.13-slim base image
- Implements multi-stage build (builder + runner)
- Runs as non-root user
- Exposes port 8000
- Image builds successfully without errors

**Implementation Steps:**
1. Create `backend/Dockerfile` with multi-stage build:
   - Stage 1 (builder): Create venv, install dependencies
   - Stage 2 (runner): Copy venv, copy code, run app
2. Create non-root user (appuser)
3. Set working directory to /app
4. Install Python dependencies from requirements.txt
5. Copy application code
6. Expose port 8000
7. Set CMD to run uvicorn

**File Location:** `backend/Dockerfile`

**Template Structure:**
```dockerfile
# Stage 1: Build dependencies
FROM python:3.13-slim AS builder
WORKDIR /app
RUN python -m venv /app/.venv
COPY requirements.txt .
RUN /app/.venv/bin/pip install -r requirements.txt

# Stage 2: Runtime
FROM python:3.13-slim AS runner
WORKDIR /app
# Copy venv from builder
# Create user
# Copy app code
# Configure
# Run app
```

**Testing:**
```bash
cd backend
docker build -t todo-backend:test .
# Should complete without errors
```

**References:**
- Spec: US-4.2 Developer Containerizes Backend
- Plan: Component Design > 1.2 Backend Image

---

### T-010: Create Backend .dockerignore
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 10 minutes
**Dependencies:** T-009

**Description:**
Create .dockerignore file to exclude unnecessary files from Docker build context.

**Acceptance Criteria:**
- File exists at `backend/.dockerignore`
- Excludes __pycache__, .venv, .git, etc.
- Reduces build context size
- Docker build is faster

**Implementation Steps:**
1. Create `backend/.dockerignore`
2. Add exclusions:
   - __pycache__
   - .venv
   - .git
   - .env
   - *.pyc
   - .pytest_cache

**File Location:** `backend/.dockerignore`

**Content:**
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
.venv
.env
.env.local
.git
.gitignore
*.md
.pytest_cache
.coverage
htmlcov
dist
build
*.egg-info
.vscode
.idea
*.log
```

**Testing:**
```bash
cd backend
time docker build -t todo-backend:test .
```

**References:**
- Plan: Performance Optimization > Docker Image Optimization

---

### T-011: Add Backend Health Check Endpoint
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** None

**Description:**
Create a health check endpoint in FastAPI that returns 200 OK.

**Acceptance Criteria:**
- Endpoint exists at `/health`
- Returns 200 status code
- Returns JSON with status and timestamp
- Does not require authentication

**Implementation Steps:**
1. Open `backend/main.py`
2. Add health check route:
   ```python
   from datetime import datetime

   @app.get("/health")
   async def health_check():
       return {
           "status": "healthy",
           "timestamp": datetime.utcnow().isoformat()
       }
   ```

**File Location:** `backend/main.py`

**Testing:**
```bash
# Start dev server
uvicorn main:app --reload

# Test endpoint
curl http://localhost:8000/health
# Should return: {"status":"healthy","timestamp":"..."}
```

**References:**
- Spec: US-4.2 Acceptance Criteria > Health check endpoint
- Plan: Health Checks > Backend Health Endpoint

---

### T-012: Build Backend Docker Image
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** T-009, T-010, T-011

**Description:**
Build the backend Docker image and verify it works correctly.

**Acceptance Criteria:**
- Image builds successfully
- Image size is under 300MB
- Image is tagged as `todo-backend:latest`
- Image is available in Minikube

**Implementation Steps:**
1. Ensure Docker is using Minikube daemon: `eval $(minikube docker-env)`
2. Build image:
   ```bash
   cd backend
   docker build -t todo-backend:latest .
   ```
3. Verify image exists:
   ```bash
   docker images | grep todo-backend
   ```

**Testing:**
```bash
# Check image size
docker images todo-backend:latest
# Size should be < 300MB

# Verify in Minikube
minikube ssh -- docker images | grep todo-backend
```

**References:**
- Spec: US-4.2 > Image size is under 300MB
- Plan: Phase 1: Containerization > Step 1: Build Docker Images

---

### T-013: Test Backend Container Locally
**Priority:** P1
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-012

**Description:**
Run the backend container locally and verify it works correctly.

**Acceptance Criteria:**
- Container starts without errors
- API is accessible at http://localhost:8000
- Health check endpoint returns 200
- API docs are accessible at http://localhost:8000/docs
- Can connect to Neon database

**Implementation Steps:**
1. Get DATABASE_URL from .env
2. Run container:
   ```bash
   docker run -p 8000:8000 \
     -e DATABASE_URL="postgresql://..." \
     -e JWT_SECRET="test-secret" \
     todo-backend:latest
   ```
3. Test health endpoint: `curl http://localhost:8000/health`
4. Check API docs: http://localhost:8000/docs
5. Stop container: Ctrl+C

**Testing:**
```bash
# Start container
docker run -d -p 8000:8000 \
  -e DATABASE_URL="$DATABASE_URL" \
  -e JWT_SECRET="test" \
  --name test-backend \
  todo-backend:latest

# Check health
curl http://localhost:8000/health

# Check logs
docker logs test-backend

# Cleanup
docker stop test-backend
docker rm test-backend
```

**References:**
- Spec: US-4.3 Developer Tests Containers Locally
- Plan: Phase 1 > Step 2: Test Containers Locally

---

## Group 4: Helm Chart Creation (P0)

### T-014: Initialize Helm Chart Structure
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** None

**Description:**
Create the Helm chart directory structure and base files.

**Acceptance Criteria:**
- Directory exists at `k8s/helm/todo-app/`
- Chart.yaml contains proper metadata
- values.yaml exists with default values
- templates/ directory exists
- _helpers.tpl exists

**Implementation Steps:**
1. Create directory structure:
   ```bash
   mkdir -p k8s/helm/todo-app/templates
   ```
2. Create Chart.yaml
3. Create values.yaml with default configuration
4. Create templates/_helpers.tpl with template functions
5. Create .helmignore

**File Locations:**
- `k8s/helm/todo-app/Chart.yaml`
- `k8s/helm/todo-app/values.yaml`
- `k8s/helm/todo-app/templates/_helpers.tpl`
- `k8s/helm/todo-app/.helmignore`

**Testing:**
```bash
# Lint chart
helm lint k8s/helm/todo-app

# Should pass with no errors
```

**References:**
- Spec: US-4.4 Developer Creates Helm Chart Structure
- Plan: Helm Chart Structure

---

### T-015: Create Chart.yaml
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 10 minutes
**Dependencies:** T-014

**Description:**
Create Chart.yaml with proper metadata for the Helm chart.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/Chart.yaml`
- Contains required fields: apiVersion, name, version, description
- Version is 1.0.0
- appVersion matches application version

**Implementation Steps:**
1. Create `k8s/helm/todo-app/Chart.yaml`
2. Add metadata:
   - apiVersion: v2
   - name: todo-app
   - description: Todo AI Chatbot Full Stack Application
   - type: application
   - version: 1.0.0
   - appVersion: "1.0.0"

**File Location:** `k8s/helm/todo-app/Chart.yaml`

**Content:**
```yaml
apiVersion: v2
name: todo-app
description: Todo AI Chatbot - Full Stack Application
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - todo
  - chatbot
  - nextjs
  - fastapi
maintainers:
  - name: irza16
```

**Testing:**
```bash
helm lint k8s/helm/todo-app
```

**References:**
- Plan: Helm Chart Structure > Chart.yaml

---

### T-016: Create values.yaml
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-014

**Description:**
Create values.yaml with all configurable parameters for the application.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/values.yaml`
- Contains frontend configuration
- Contains backend configuration
- All values have sensible defaults
- Well-documented with comments

**Implementation Steps:**
1. Create `k8s/helm/todo-app/values.yaml`
2. Add frontend section (image, replicas, service, resources)
3. Add backend section (image, replicas, service, resources, secrets)
4. Add configuration for ConfigMaps and Secrets
5. Add comments explaining each value

**File Location:** `k8s/helm/todo-app/values.yaml`

**Key Sections:**
- frontend.image
- frontend.replicaCount
- frontend.service
- frontend.resources
- backend.image
- backend.replicaCount
- backend.service
- backend.resources
- backend.secrets

**Testing:**
```bash
helm lint k8s/helm/todo-app
helm template todo-app k8s/helm/todo-app
```

**References:**
- Plan: Helm Chart Structure > values.yaml

---

### T-017: Create Frontend Deployment Template
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 45 minutes
**Dependencies:** T-016

**Description:**
Create Kubernetes Deployment template for the frontend service.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/frontend-deployment.yaml`
- Uses values from values.yaml
- Includes resource requests and limits
- Includes readiness and liveness probes
- Includes environment variables from ConfigMap
- Template renders correctly

**Implementation Steps:**
1. Create file: `templates/frontend-deployment.yaml`
2. Define Deployment resource
3. Reference values with `{{ .Values.frontend.* }}`
4. Add container spec with:
   - Image from values
   - Resource limits
   - Environment variables
   - Health probes
5. Add labels for organization

**File Location:** `k8s/helm/todo-app/templates/frontend-deployment.yaml`

**Testing:**
```bash
helm template todo-app k8s/helm/todo-app | grep -A 50 "kind: Deployment" | grep -A 50 "frontend"
```

**References:**
- Spec: US-4.5 Developer Defines Frontend Kubernetes Resources
- Plan: Component Design > 2.1 Deployments > Frontend Deployment

---

### T-018: Create Frontend Service Template
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-017

**Description:**
Create Kubernetes Service template for the frontend.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/frontend-service.yaml`
- Type is ClusterIP (configurable)
- Exposes port 3000
- Selector matches deployment labels
- Template renders correctly

**Implementation Steps:**
1. Create file: `templates/frontend-service.yaml`
2. Define Service resource
3. Reference values for type and port
4. Set selector to match deployment labels
5. Add annotations if needed

**File Location:** `k8s/helm/todo-app/templates/frontend-service.yaml`

**Testing:**
```bash
helm template todo-app k8s/helm/todo-app | grep -A 20 "kind: Service" | grep -A 20 "frontend"
```

**References:**
- Spec: US-4.5 > Service template exists for frontend
- Plan: Component Design > 2.2 Services > Frontend Service

---

### T-019: Create Frontend ConfigMap Template
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** T-017

**Description:**
Create Kubernetes ConfigMap template for frontend configuration.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/frontend-configmap.yaml`
- Contains NEXT_PUBLIC_API_URL
- Value references backend service name
- Template renders correctly

**Implementation Steps:**
1. Create file: `templates/frontend-configmap.yaml`
2. Define ConfigMap resource
3. Add data:
   - NEXT_PUBLIC_API_URL: http://todo-backend:8000
   - NODE_ENV: production

**File Location:** `k8s/helm/todo-app/templates/frontend-configmap.yaml`

**Testing:**
```bash
helm template todo-app k8s/helm/todo-app | grep -A 10 "kind: ConfigMap" | grep -A 10 "frontend"
```

**References:**
- Plan: Component Design > 2.3 ConfigMaps > Frontend ConfigMap

---

### T-020: Create Backend Deployment Template
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 45 minutes
**Dependencies:** T-016

**Description:**
Create Kubernetes Deployment template for the backend service.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/backend-deployment.yaml`
- Uses values from values.yaml
- Includes resource requests and limits
- Includes readiness and liveness probes
- Includes environment variables from ConfigMap and Secret
- Template renders correctly

**Implementation Steps:**
1. Create file: `templates/backend-deployment.yaml`
2. Define Deployment resource
3. Reference values with `{{ .Values.backend.* }}`
4. Add container spec with:
   - Image from values
   - Resource limits
   - Environment variables from ConfigMap
   - Secret references for DATABASE_URL and JWT_SECRET
   - Health probes
5. Add labels

**File Location:** `k8s/helm/todo-app/templates/backend-deployment.yaml`

**Testing:**
```bash
helm template todo-app k8s/helm/todo-app | grep -A 50 "kind: Deployment" | grep -A 50 "backend"
```

**References:**
- Spec: US-4.6 Developer Defines Backend Kubernetes Resources
- Plan: Component Design > 2.1 Deployments > Backend Deployment

---

### T-021: Create Backend Service Template
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-020

**Description:**
Create Kubernetes Service template for the backend.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/backend-service.yaml`
- Type is ClusterIP
- Exposes port 8000
- Selector matches deployment labels
- Template renders correctly

**Implementation Steps:**
1. Create file: `templates/backend-service.yaml`
2. Define Service resource
3. Reference values for port
4. Set selector to match deployment labels
5. Name must be "todo-backend" for DNS resolution

**File Location:** `k8s/helm/todo-app/templates/backend-service.yaml`

**Testing:**
```bash
helm template todo-app k8s/helm/todo-app | grep -A 20 "kind: Service" | grep -A 20 "backend"
```

**References:**
- Spec: US-4.6 > Service template exists for backend
- Plan: Component Design > 2.2 Services > Backend Service

---

### T-022: Create Backend ConfigMap Template
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** T-020

**Description:**
Create Kubernetes ConfigMap template for backend configuration.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/backend-configmap.yaml`
- Contains non-sensitive configuration
- Values come from values.yaml
- Template renders correctly

**Implementation Steps:**
1. Create file: `templates/backend-configmap.yaml`
2. Define ConfigMap resource
3. Add data:
   - CORS_ORIGIN
   - LOG_LEVEL
   - PYTHONUNBUFFERED

**File Location:** `k8s/helm/todo-app/templates/backend-configmap.yaml`

**Testing:**
```bash
helm template todo-app k8s/helm/todo-app | grep -A 10 "kind: ConfigMap" | grep -A 10 "backend"
```

**References:**
- Plan: Component Design > 2.3 ConfigMaps > Backend ConfigMap

---

### T-023: Create Backend Secret Template
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-020

**Description:**
Create Kubernetes Secret template for backend sensitive configuration.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/backend-secret.yaml`
- Contains DATABASE_URL and JWT_SECRET
- Values come from values.yaml (or helm install --set)
- Uses base64 encoding if needed
- Template renders correctly

**Implementation Steps:**
1. Create file: `templates/backend-secret.yaml`
2. Define Secret resource
3. Add stringData (Kubernetes handles base64):
   - database-url
   - jwt-secret
4. Reference values from .Values.backend.secrets

**File Location:** `k8s/helm/todo-app/templates/backend-secret.yaml`

**Testing:**
```bash
helm template todo-app k8s/helm/todo-app \
  --set backend.secrets.databaseUrl="test" \
  --set backend.secrets.jwtSecret="test" \
  | grep -A 10 "kind: Secret"
```

**References:**
- Spec: US-4.6 > Secret template exists for sensitive config
- Plan: Component Design > 2.4 Secrets

---

### T-024: Create Template Helpers
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-014

**Description:**
Create helper template functions for consistent naming and labels.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/_helpers.tpl`
- Contains name helper function
- Contains fullname helper function
- Contains label helpers
- Helpers are used in all templates

**Implementation Steps:**
1. Create file: `templates/_helpers.tpl`
2. Add `todo-app.name` helper
3. Add `todo-app.fullname` helper
4. Add `todo-app.labels` helper
5. Add `todo-app.selectorLabels` helper
6. Update all templates to use helpers

**File Location:** `k8s/helm/todo-app/templates/_helpers.tpl`

**Testing:**
```bash
helm template todo-app k8s/helm/todo-app | grep "app.kubernetes.io"
# Should show consistent labels across all resources
```

**References:**
- Plan: Helm Chart Structure > templates/_helpers.tpl

---

### T-025: Create NOTES.txt
**Priority:** P1
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-014

**Description:**
Create NOTES.txt with post-install instructions for users.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/NOTES.txt`
- Shows how to check pod status
- Shows how to access the application
- Shows helpful troubleshooting commands
- Displays after helm install

**Implementation Steps:**
1. Create file: `templates/NOTES.txt`
2. Add instructions for:
   - Checking deployment status
   - Port-forwarding to access app
   - Viewing logs
   - Getting service info
3. Use template syntax to show actual release name

**File Location:** `k8s/helm/todo-app/templates/NOTES.txt`

**Testing:**
```bash
helm install test-release k8s/helm/todo-app --dry-run
# Should display NOTES at the end
```

**References:**
- Plan: Helm Chart Structure > NOTES.txt

---

### T-026: Validate Helm Chart
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-014 through T-025

**Description:**
Validate the Helm chart for errors and best practices.

**Acceptance Criteria:**
- `helm lint` passes without errors
- `helm template` generates valid YAML
- Dry-run install succeeds
- All templates use values correctly
- No hardcoded values (except defaults)

**Implementation Steps:**
1. Run helm lint:
   ```bash
   helm lint k8s/helm/todo-app
   ```
2. Run helm template:
   ```bash
   helm template todo-app k8s/helm/todo-app > /tmp/output.yaml
   ```
3. Validate YAML:
   ```bash
   kubectl apply --dry-run=client -f /tmp/output.yaml
   ```
4. Dry-run install:
   ```bash
   helm install test-release k8s/helm/todo-app --dry-run --debug
   ```
5. Fix any errors found

**Testing:**
```bash
# All should pass without errors
helm lint k8s/helm/todo-app
helm template todo-app k8s/helm/todo-app > /tmp/output.yaml
kubectl apply --dry-run=client -f /tmp/output.yaml
```

**References:**
- Spec: US-4.4 > Chart passes helm lint validation
- Plan: Phase 2: Helm Chart Development > Step 2: Validate Chart

---

## Group 5: Deployment to Minikube (P0)

### T-027: Deploy Application to Minikube
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-007, T-012, T-026

**Description:**
Install the Helm chart to deploy the application to Minikube.

**Acceptance Criteria:**
- Helm install command succeeds
- All pods reach Running state within 60 seconds
- No pod restarts (0 in RESTARTS column)
- Services are created
- ConfigMaps and Secrets are created

**Implementation Steps:**
1. Get DATABASE_URL and JWT_SECRET values
2. Install chart:
   ```bash
   helm install todo-app k8s/helm/todo-app \
     --set backend.secrets.databaseUrl="$DATABASE_URL" \
     --set backend.secrets.jwtSecret="$JWT_SECRET"
   ```
3. Watch pods start:
   ```bash
   kubectl get pods -w
   ```
4. Wait for all pods to be Running
5. Verify deployment:
   ```bash
   kubectl get all
   ```

**Testing:**
```bash
# Check pod status
kubectl get pods
# All should show Running with 0 restarts

# Check services
kubectl get svc

# Check events for errors
kubectl get events --sort-by='.lastTimestamp'
```

**References:**
- Spec: US-4.7 Developer Deploys to Minikube
- Plan: Phase 3: Deployment to Minikube > Step 2: Install Helm Chart

---

### T-028: Verify Pod Health
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-027

**Description:**
Verify that all pods are healthy and ready to serve traffic.

**Acceptance Criteria:**
- All pods show 1/1 READY
- Liveness probes are passing
- Readiness probes are passing
- No errors in pod logs
- Health check endpoints return 200

**Implementation Steps:**
1. Check pod status:
   ```bash
   kubectl get pods
   ```
2. Describe pods:
   ```bash
   kubectl describe pod <frontend-pod>
   kubectl describe pod <backend-pod>
   ```
3. Check logs:
   ```bash
   kubectl logs -f <frontend-pod>
   kubectl logs -f <backend-pod>
   ```
4. Test health endpoints from within pods:
   ```bash
   kubectl exec <frontend-pod> -- curl http://localhost:3000/api/health
   kubectl exec <backend-pod> -- curl http://localhost:8000/health
   ```

**Testing:**
```bash
# All should show Running and 1/1 READY
kubectl get pods

# Should show no errors in events
kubectl describe pod <pod-name> | grep -A 10 Events
```

**References:**
- Spec: US-4.7 > All pods reach Running state
- Plan: Phase 4: Testing and Validation > Health Checks

---

### T-029: Verify Service Communication
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-028

**Description:**
Verify that frontend can communicate with backend via Kubernetes service.

**Acceptance Criteria:**
- Frontend pod can reach backend service
- Backend service resolves via DNS
- API requests succeed
- No network errors

**Implementation Steps:**
1. Get frontend pod name
2. Exec into frontend pod:
   ```bash
   kubectl exec -it <frontend-pod> -- /bin/sh
   ```
3. Test backend connectivity:
   ```bash
   curl http://todo-backend:8000/health
   ```
4. Should return: `{"status":"healthy",...}`
5. Exit pod: `exit`

**Testing:**
```bash
# From frontend pod
kubectl exec <frontend-pod> -- curl -s http://todo-backend:8000/health

# Should return healthy status
```

**References:**
- Spec: US-4.7 > Frontend pod is accessible via service
- Plan: Networking > Internal Communication

---

### T-030: Verify Database Connectivity
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** T-028

**Description:**
Verify that backend pod can connect to external Neon database.

**Acceptance Criteria:**
- Backend pod has DATABASE_URL from secret
- Connection to Neon database succeeds
- No database connection errors in logs
- Can execute test query

**Implementation Steps:**
1. Check backend logs for database connection:
   ```bash
   kubectl logs <backend-pod> | grep -i database
   ```
2. Exec into backend pod:
   ```bash
   kubectl exec -it <backend-pod> -- /bin/bash
   ```
3. Test database connection (if psql available):
   ```bash
   echo $DATABASE_URL
   ```
4. Check for connection errors in application logs

**Testing:**
```bash
# Check logs for successful database connection
kubectl logs <backend-pod> | grep -i "database\|connection"

# Should show successful connection, no errors
```

**References:**
- Spec: US-4.7 > Backend pod can connect to Neon database
- Plan: Networking > Database Access

---

### T-031: Access Application via Port-Forward
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** T-029

**Description:**
Access the deployed application from local browser using port-forwarding.

**Acceptance Criteria:**
- Port-forward command succeeds
- Application loads at http://localhost:3000
- Can navigate through pages
- No console errors
- Backend API is accessible

**Implementation Steps:**
1. Port-forward frontend service:
   ```bash
   kubectl port-forward service/todo-frontend 3000:3000
   ```
2. Open browser to http://localhost:3000
3. Verify application loads
4. Test navigation
5. Keep port-forward running for testing

**Testing:**
```bash
# In terminal 1: Port-forward
kubectl port-forward service/todo-frontend 3000:3000

# In terminal 2: Test access
curl http://localhost:3000
# Should return HTML

# Open in browser
open http://localhost:3000
```

**References:**
- Spec: US-4.8 Developer Accesses Application Locally
- Plan: Networking > External Access

---

### T-032: Test Application Functionality
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-031

**Description:**
Test all application features to ensure they work correctly in Kubernetes.

**Acceptance Criteria:**
- User can sign up
- User can log in
- User can create tasks
- User can view tasks
- User can update tasks
- User can mark tasks complete
- User can delete tasks
- All functionality from Phase 3 works

**Implementation Steps:**
1. With port-forward running, open http://localhost:3000
2. Test signup flow
3. Test login flow
4. Test task creation
5. Test task listing
6. Test task update
7. Test task completion
8. Test task deletion
9. Document any issues

**Testing:**
```
Manual test checklist:
[ ] Sign up with new account
[ ] Log in with credentials
[ ] Create a task
[ ] View task in list
[ ] Update task title
[ ] Mark task as complete
[ ] Mark task as incomplete
[ ] Delete task
[ ] Verify all operations persist
```

**References:**
- Spec: US-4.8 > All functionality from Phase 3 works identically
- Plan: Phase 4: Testing and Validation > Integration Testing

---

## Group 6: Documentation (P1)

### T-033: Create Kubernetes README
**Priority:** P1
**Status:** ⬜
**Estimated Time:** 1 hour
**Dependencies:** T-032

**Description:**
Create comprehensive documentation for deploying the application to Kubernetes.

**Acceptance Criteria:**
- File exists at `k8s/README.md`
- Includes prerequisites
- Includes step-by-step deployment instructions
- Includes verification steps
- Includes access instructions
- Includes troubleshooting section
- Includes cleanup instructions
- All commands are tested and work

**Implementation Steps:**
1. Create `k8s/README.md`
2. Add sections:
   - Prerequisites
   - Setup Minikube
   - Build Docker Images
   - Deploy with Helm
   - Verify Deployment
   - Access Application
   - Troubleshooting
   - Cleanup
3. Add actual commands (not placeholders)
4. Test all commands
5. Add screenshots (optional)

**File Location:** `k8s/README.md`

**Sections:**
- Prerequisites
- Minikube Setup
- Docker Image Build
- Helm Chart Deployment
- Verification Steps
- Accessing the App
- Troubleshooting
- Cleanup

**Testing:**
```bash
# Follow your own README from scratch
# Ensure all commands work
```

**References:**
- Spec: US-4.11 Developer Documents Deployment Process
- Plan: Documentation Validation

---

### T-034: Update Root README
**Priority:** P1
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-033

**Description:**
Update the root README.md to include Phase 4 information.

**Acceptance Criteria:**
- Root README.md is updated
- Includes Phase 4 section
- Links to k8s/README.md
- Mentions Kubernetes deployment
- Updated tech stack section

**Implementation Steps:**
1. Open root `README.md`
2. Add Phase 4 section
3. Update tech stack to include:
   - Docker
   - Kubernetes
   - Helm
   - Minikube
4. Add link to k8s/README.md
5. Update deployment section

**File Location:** `README.md`

**Testing:**
```bash
# Read through README
# Verify all links work
```

**References:**
- Spec: Deliverables > Documentation

---

### T-035: Add Deployment Diagram
**Priority:** P2
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-033

**Description:**
Create an architecture diagram showing the Kubernetes deployment.

**Acceptance Criteria:**
- Diagram shows pods, services, configmaps, secrets
- Diagram shows networking between components
- Diagram shows external database connection
- Saved as image in k8s/docs/
- Referenced in README

**Implementation Steps:**
1. Create diagram using draw.io, Excalidraw, or ASCII art
2. Show:
   - Minikube cluster boundary
   - Frontend pod + service
   - Backend pod + service
   - ConfigMaps
   - Secrets
   - External database
   - Network connections
3. Save as PNG or SVG
4. Add to k8s/docs/architecture.png
5. Reference in README

**File Location:** `k8s/docs/architecture.png`

**Testing:**
```bash
# Verify image displays in README
```

**References:**
- Plan: System Architecture diagrams

---

## Group 7: AI DevOps Tools (P2 - Optional)

### T-036: Install kubectl-ai
**Priority:** P2
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-002

**Description:**
Install and configure kubectl-ai for AI-assisted Kubernetes operations.

**Acceptance Criteria:**
- kubectl-ai is installed
- OpenAI API key is configured
- Can run simple kubectl-ai commands
- Commands execute successfully

**Implementation Steps:**
1. Install kubectl-ai:
   ```bash
   # macOS
   brew install kubectl-ai

   # Or download binary
   ```
2. Configure OpenAI API key:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```
3. Test:
   ```bash
   kubectl-ai "list all pods"
   ```

**Testing:**
```bash
kubectl-ai "show me the status of all pods"
kubectl-ai "describe the todo-frontend service"
```

**References:**
- Spec: US-4.9 Developer Uses kubectl-ai for Operations
- Plan: kubectl-ai and kagent Integration

---

### T-037: Install kagent
**Priority:** P2
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-002

**Description:**
Install and configure kagent for advanced cluster management.

**Acceptance Criteria:**
- kagent is installed
- Can run kagent commands
- Provides useful insights

**Implementation Steps:**
1. Install kagent:
   ```bash
   pip install kagent
   # Or follow official guide
   ```
2. Test:
   ```bash
   kagent "analyze cluster health"
   ```

**Testing:**
```bash
kagent "analyze the cluster health"
kagent "optimize resource allocation"
```

**References:**
- Spec: US-4.10 Developer Uses kagent for Cluster Management
- Plan: kubectl-ai and kagent Integration

---

### T-038: Document AI DevOps Usage
**Priority:** P2
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-036, T-037

**Description:**
Document examples of using kubectl-ai and kagent for this project.

**Acceptance Criteria:**
- Examples added to k8s/README.md
- Shows practical use cases
- Includes sample outputs
- Explains benefits

**Implementation Steps:**
1. Add section to k8s/README.md: "AI-Assisted Operations"
2. Add kubectl-ai examples
3. Add kagent examples
4. Show actual outputs
5. Explain when to use each tool

**File Location:** `k8s/README.md` (new section)

**Testing:**
```bash
# Follow examples in README
# Verify they work
```

**References:**
- Spec: US-4.9, US-4.10
- Plan: kubectl-ai and kagent Integration

---

## Group 8: Demo and Submission (P0)

### T-039: Record Demo Video
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 1 hour
**Dependencies:** T-032

**Description:**
Record a demo video showing the Kubernetes deployment and application functionality.

**Acceptance Criteria:**
- Video is under 90 seconds
- Shows helm install command
- Shows pods starting
- Shows kubectl commands
- Shows application running
- Shows at least one task operation
- Video quality is clear
- Audio is clear (if included)

**Implementation Steps:**
1. Plan video structure (30 seconds intro, 45 seconds demo, 15 seconds outro)
2. Practice walkthrough
3. Record screen:
   - Show helm install
   - Show kubectl get pods -w
   - Show port-forward command
   - Show browser with application
   - Create/complete a task
4. Edit video if needed
5. Export as MP4
6. Upload to YouTube/Vimeo/Google Drive
7. Get shareable link

**Content Outline:**
```
0:00-0:15  Introduction
0:15-0:30  Show helm install command
0:30-0:45  Show pods starting (kubectl get pods -w)
0:45-1:00  Show port-forward and browser
1:00-1:20  Demonstrate task operations
1:20-1:30  Conclusion
```

**Testing:**
```bash
# Watch video
# Verify under 90 seconds
# Verify all requirements shown
```

**References:**
- Spec: US-4.12 Developer Creates Demo Video
- Hackathon Requirements > Demo video link

---

### T-040: Prepare Submission Package
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-039

**Description:**
Prepare all materials for hackathon submission.

**Acceptance Criteria:**
- GitHub repository is public
- All code is committed and pushed
- README is up to date
- Demo video link is ready
- Vercel deployment link (Phase 3) is ready
- Submission form is filled out

**Implementation Steps:**
1. Commit all changes:
   ```bash
   git add .
   git commit -m "Phase 4 complete: Kubernetes deployment"
   git push origin phase-4-kubernetes
   ```
2. Merge to main (optional):
   ```bash
   git checkout main
   git merge phase-4-kubernetes
   git push origin main
   ```
3. Tag release:
   ```bash
   git tag phase-4-submission
   git push origin phase-4-submission
   ```
4. Verify GitHub repo is public
5. Get repository URL
6. Get demo video URL
7. Prepare Phase 3 Vercel URL

**Checklist:**
```
[ ] GitHub repo is public
[ ] All code is pushed
[ ] README is complete
[ ] Demo video is uploaded
[ ] Video link is accessible
[ ] Vercel link works
[ ] All links tested
```

**Testing:**
```bash
# Open repo in private/incognito window
# Verify it's accessible
# Click all links
```

**References:**
- Hackathon Requirements > Submit and Present Your Project

---

### T-041: Submit to Hackathon
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** T-040

**Description:**
Submit Phase 4 via the hackathon submission form.

**Acceptance Criteria:**
- Form is submitted successfully
- Received confirmation (if applicable)
- All required fields are filled
- Links are correct and working

**Implementation Steps:**
1. Go to: https://forms.gle/KMKEKaFUD6ZX4UtY8
2. Fill in:
   - Public GitHub Repo Link
   - Published App Link (Vercel from Phase 3)
   - Demo video link
   - WhatsApp number
3. Double-check all links work
4. Submit form
5. Screenshot confirmation page

**Form Fields:**
- GitHub Repository: https://github.com/irza16/todo-console-app
- Vercel Link: https://todo-console-app-orcin.vercel.app
- Demo Video: [Your YouTube/Drive link]
- WhatsApp: [Your number]

**Testing:**
```bash
# Test all links in private browser
# Verify they work for someone else
```

**References:**
- Hackathon Requirements > Submission Deadline: January 4, 2026

---

## Task Summary

**Total Tasks:** 41

**By Priority:**
- P0 (Critical): 33 tasks
- P1 (High): 5 tasks
- P2 (Medium): 3 tasks

**By Group:**
- Environment Setup: 3 tasks
- Frontend Containerization: 5 tasks
- Backend Containerization: 5 tasks
- Helm Chart Creation: 13 tasks
- Deployment to Minikube: 6 tasks
- Documentation: 3 tasks
- AI DevOps Tools: 3 tasks (optional)
- Demo and Submission: 3 tasks

**Estimated Total Time:** 16-20 hours

**Critical Path:**
T-001 → T-002 → T-003 → T-004 → T-007 → T-009 → T-012 → T-014 → T-026 → T-027 → T-032 → T-039 → T-041

---

## Notes for Implementation

### Using Spec-Driven Development
Each task should be implemented by:
1. Reading the task description
2. Understanding acceptance criteria
3. Writing code (via Claude Code if following hackathon rules)
4. Testing against acceptance criteria
5. Marking task as complete

### Testing Strategy
- Test each task immediately after completion
- Don't proceed to dependent tasks until current task passes
- Keep notes of any deviations from plan
- Update specs if requirements change

### Time Management
- Focus on P0 tasks first (critical path)
- P1 tasks are important but can be simplified if time-constrained
- P2 tasks are optional enhancements
- Save P3 for after submission if time permits

### Troubleshooting
- Reference the Troubleshooting Guide in the Plan
- Check pod logs: `kubectl logs <pod-name>`
- Describe resources: `kubectl describe <resource-type> <name>`
- Check events: `kubectl get events --sort-by='.lastTimestamp'`

### Getting Help
- Consult Docker documentation
- Consult Kubernetes documentation
- Consult Helm documentation
- Use kubectl-ai/kagent for AI assistance
- Ask Claude Code for spec-driven solutions

---

## Completion Checklist

Before marking Phase 4 complete, verify:

- [ ] All P0 tasks are complete
- [ ] Docker images build successfully
- [ ] Helm chart installs without errors
- [ ] All pods are Running
- [ ] Application is accessible
- [ ] All Phase 3 features work
- [ ] Documentation is complete
- [ ] Demo video is recorded
- [ ] Submission is completed

**Phase 4 is complete when all P0 tasks are ✅ and the application is deployed and working in Minikube.**
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Run `.specify/scripts/bash/check-prerequisites.sh --json` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load design documents**: Read from FEATURE_DIR:
   - **Required**: plan.md (tech stack, libraries, structure), spec.md (user stories with priorities)
   - **Optional**: data-model.md (entities), contracts/ (API endpoints), research.md (decisions), quickstart.md (test scenarios)
   - Note: Not all projects have all documents. Generate tasks based on what's available.

3. **Execute task generation workflow**:
   - Load plan.md and extract tech stack, libraries, project structure
   - Load spec.md and extract user stories with their priorities (P1, P2, P3, etc.)
   - If data-model.md exists: Extract entities and map to user stories
   - If contracts/ exists: Map endpoints to user stories
   - If research.md exists: Extract decisions for setup tasks
   - Generate tasks organized by user story (see Task Generation Rules below)
   - Generate dependency graph showing user story completion order
   - Create parallel execution examples per user story
   - Validate task completeness (each user story has all needed tasks, independently testable)

4. **Generate tasks.md**: Use `.specify/templates/tasks-template.md` as structure, fill with:
   - Correct feature name from plan.md
   - Phase 1: Setup tasks (project initialization)
   - Phase 2: Foundational tasks (blocking prerequisites for all user stories)
   - Phase 3+: One phase per user story (in priority order from spec.md)
   - Each phase includes: story goal, independent test criteria, tests (if requested), implementation tasks
   - Final Phase: Polish & cross-cutting concerns
   - All tasks must follow the strict checklist format (see Task Generation Rules below)
   - Clear file paths for each task
   - Dependencies section showing story completion order
   - Parallel execution examples per story
   - Implementation strategy section (MVP first, incremental delivery)

5. **Report**: Output path to generated tasks.md and summary:
   - Total task count
   - Task count per user story
   - Parallel opportunities identified
   - Independent test criteria for each story
   - Suggested MVP scope (typically just User Story 1)
   - Format validation: Confirm ALL tasks follow the checklist format (checkbox, ID, labels, file paths)

Context for task generation: # Phase 4 Tasks: Kubernetes Deployment Implementation

## Task Organization

Tasks are organized into logical groups and numbered sequentially. Each task is atomic, testable, and maps back to the specification and plan.

**Priority Levels:**
- **P0**: Critical path - must complete
- **P1**: High priority - should complete
- **P2**: Medium priority - nice to have
- **P3**: Low priority - optional

**Status:**
- ⬜ Not Started
- 🟡 In Progress
- ✅ Complete
- ❌ Blocked

---

## Group 1: Environment Setup (P0)

### T-001: Install Required Tools
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** None

**Description:**
Install all required tools for Kubernetes development and deployment.

**Acceptance Criteria:**
- Docker Desktop 4.53+ is installed and running
- Minikube is installed (latest stable version)
- kubectl is installed and working
- Helm 3.x is installed
- All tools return version when run with `--version`

**Implementation Steps:**
1. Download and install Docker Desktop from https://www.docker.com/products/docker-desktop
2. Start Docker Desktop and verify it's running
3. Install Minikube: `brew install minikube` (macOS) or follow OS-specific guide
4. Install kubectl: `brew install kubectl` or download from kubernetes.io
5. Install Helm: `brew install helm` or download from helm.sh
6. Verify installations:
   ```bash
   docker --version
   minikube version
   kubectl version --client
   helm version
   ```

**Testing:**
```bash
# All commands should return version info
docker --version
minikube version
kubectl version --client
helm version
```

**References:**
- Spec: Technical Requirements > Tool Dependencies
- Plan: Build and Deployment Workflow

---

### T-002: Start Minikube Cluster
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** T-001

**Description:**
Start a local Minikube Kubernetes cluster with appropriate resources.

**Acceptance Criteria:**
- Minikube cluster starts successfully
- Cluster has at least 4GB RAM and 2 CPUs allocated
- kubectl can connect to cluster
- Cluster info displays correctly

**Implementation Steps:**
1. Start Minikube with resource allocation:
   ```bash
   minikube start --cpus=4 --memory=4096 --driver=docker
   ```
2. Wait for cluster to be ready
3. Verify cluster status:
   ```bash
   minikube status
   kubectl cluster-info
   kubectl get nodes
   ```

**Testing:**
```bash
# Should show running cluster
minikube status

# Should show cluster endpoints
kubectl cluster-info

# Should show node in Ready state
kubectl get nodes
```

**References:**
- Spec: US-4.7 Developer Deploys to Minikube
- Plan: Phase 3: Deployment to Minikube

---

### T-003: Configure Docker for Minikube
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 10 minutes
**Dependencies:** T-002

**Description:**
Configure Docker to use Minikube's Docker daemon so images built locally are available to Kubernetes.

**Acceptance Criteria:**
- Docker commands point to Minikube's daemon
- Can build and see images in Minikube
- Environment variable DOCKER_HOST is set correctly

**Implementation Steps:**
1. Run: `eval $(minikube docker-env)`
2. Verify Docker is using Minikube:
   ```bash
   docker ps
   # Should show Minikube system containers
   ```
3. Add to shell profile for persistence (optional):
   ```bash
   echo 'eval $(minikube docker-env)' >> ~/.zshrc
   ```

**Testing:**
```bash
# Should show Minikube containers
docker ps | grep k8s

# Build test image
docker build -t test:latest - <<EOF
FROM alpine
CMD echo "Hello from Minikube Docker"
EOF

# Verify image exists
docker images | grep test
```

**References:**
- Plan: Build and Deployment Workflow > Step 3: Load Images into Minikube

---

## Group 2: Frontend Containerization (P0)

### T-004: Create Frontend Dockerfile
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 1 hour
**Dependencies:** None

**Description:**
Create a multi-stage Dockerfile for the Next.js frontend application.

**Acceptance Criteria:**
- File exists at `frontend/Dockerfile`
- Uses node:20-alpine base image
- Implements multi-stage build (builder + runner)
- Runs as non-root user
- Exposes port 3000
- Image builds successfully without errors

**Implementation Steps:**
1. Create `frontend/Dockerfile` with multi-stage build:
   - Stage 1 (builder): Install deps, build Next.js
   - Stage 2 (runner): Copy built files, configure production
2. Configure non-root user (node)
3. Set working directory to /app
4. Copy package files and install dependencies
5. Build Next.js app
6. Expose port 3000
7. Set CMD to start production server

**File Location:** `frontend/Dockerfile`

**Template Structure:**
```dockerfile
# Stage 1: Dependencies and build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production runtime
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
# Copy necessary files
# Configure user
# Expose port
# Start server
```

**Testing:**
```bash
cd frontend
docker build -t todo-frontend:test .
# Should complete without errors
```

**References:**
- Spec: US-4.1 Developer Containerizes Frontend
- Plan: Component Design > 1.1 Frontend Image

---

### T-005: Create Frontend .dockerignore
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 10 minutes
**Dependencies:** T-004

**Description:**
Create .dockerignore file to exclude unnecessary files from Docker build context.

**Acceptance Criteria:**
- File exists at `frontend/.dockerignore`
- Excludes node_modules, .git, .next, build artifacts
- Reduces build context size significantly
- Docker build is faster

**Implementation Steps:**
1. Create `frontend/.dockerignore`
2. Add exclusions:
   - node_modules
   - .next
   - .git
   - .env*.local
   - *.md (except README if needed)
   - coverage
   - .vscode

**File Location:** `frontend/.dockerignore`

**Content:**
```
node_modules
.next
.git
.gitignore
.env*.local
*.md
coverage
.vscode
.idea
*.log
dist
build
```

**Testing:**
```bash
# Build should be faster (less context)
cd frontend
time docker build -t todo-frontend:test .
```

**References:**
- Plan: Performance Optimization > Docker Image Optimization

---

### T-006: Add Frontend Health Check Endpoint
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** None

**Description:**
Create a health check API route in Next.js that returns 200 OK.

**Acceptance Criteria:**
- Route exists at `app/api/health/route.ts`
- Returns 200 status code
- Returns JSON with status and timestamp
- Works in both dev and production modes

**Implementation Steps:**
1. Create directory: `frontend/app/api/health/`
2. Create file: `route.ts`
3. Implement GET handler:
   ```typescript
   export async function GET() {
     return Response.json({
       status: 'healthy',
       timestamp: new Date().toISOString()
     });
   }
   ```

**File Location:** `frontend/app/api/health/route.ts`

**Testing:**
```bash
# Start dev server
npm run dev

# Test endpoint
curl http://localhost:3000/api/health
# Should return: {"status":"healthy","timestamp":"..."}
```

**References:**
- Spec: US-4.1 Acceptance Criteria > Health check endpoint
- Plan: Health Checks > Frontend Health Endpoint

---

### T-007: Build Frontend Docker Image
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** T-004, T-005, T-006

**Description:**
Build the frontend Docker image and verify it works correctly.

**Acceptance Criteria:**
- Image builds successfully
- Image size is under 500MB
- Image is tagged as `todo-frontend:latest`
- Image is available in Minikube

**Implementation Steps:**
1. Ensure Docker is using Minikube daemon: `eval $(minikube docker-env)`
2. Build image:
   ```bash
   cd frontend
   docker build -t todo-frontend:latest .
   ```
3. Verify image exists:
   ```bash
   docker images | grep todo-frontend
   ```

**Testing:**
```bash
# Check image size
docker images todo-frontend:latest
# Size column should show < 500MB

# Verify image is in Minikube
minikube ssh -- docker images | grep todo-frontend
```

**References:**
- Spec: US-4.1 > Image size is under 500MB
- Plan: Phase 1: Containerization > Step 1: Build Docker Images

---

### T-008: Test Frontend Container Locally
**Priority:** P1
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-007

**Description:**
Run the frontend container locally and verify it works correctly.

**Acceptance Criteria:**
- Container starts without errors
- Application is accessible at http://localhost:3000
- Health check endpoint returns 200
- Pages load correctly
- No console errors

**Implementation Steps:**
1. Run container:
   ```bash
   docker run -p 3000:3000 \
     -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
     todo-frontend:latest
   ```
2. Open browser to http://localhost:3000
3. Verify pages load
4. Check health endpoint: `curl http://localhost:3000/api/health`
5. Stop container: Ctrl+C

**Testing:**
```bash
# Start container
docker run -d -p 3000:3000 --name test-frontend todo-frontend:latest

# Check health
curl http://localhost:3000/api/health

# Check logs
docker logs test-frontend

# Cleanup
docker stop test-frontend
docker rm test-frontend
```

**References:**
- Spec: US-4.3 Developer Tests Containers Locally
- Plan: Phase 1 > Step 2: Test Containers Locally

---

## Group 3: Backend Containerization (P0)

### T-009: Create Backend Dockerfile
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 1 hour
**Dependencies:** None

**Description:**
Create a multi-stage Dockerfile for the FastAPI backend application.

**Acceptance Criteria:**
- File exists at `backend/Dockerfile`
- Uses python:3.13-slim base image
- Implements multi-stage build (builder + runner)
- Runs as non-root user
- Exposes port 8000
- Image builds successfully without errors

**Implementation Steps:**
1. Create `backend/Dockerfile` with multi-stage build:
   - Stage 1 (builder): Create venv, install dependencies
   - Stage 2 (runner): Copy venv, copy code, run app
2. Create non-root user (appuser)
3. Set working directory to /app
4. Install Python dependencies from requirements.txt
5. Copy application code
6. Expose port 8000
7. Set CMD to run uvicorn

**File Location:** `backend/Dockerfile`

**Template Structure:**
```dockerfile
# Stage 1: Build dependencies
FROM python:3.13-slim AS builder
WORKDIR /app
RUN python -m venv /app/.venv
COPY requirements.txt .
RUN /app/.venv/bin/pip install -r requirements.txt

# Stage 2: Runtime
FROM python:3.13-slim AS runner
WORKDIR /app
# Copy venv from builder
# Create user
# Copy app code
# Configure
# Run app
```

**Testing:**
```bash
cd backend
docker build -t todo-backend:test .
# Should complete without errors
```

**References:**
- Spec: US-4.2 Developer Containerizes Backend
- Plan: Component Design > 1.2 Backend Image

---

### T-010: Create Backend .dockerignore
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 10 minutes
**Dependencies:** T-009

**Description:**
Create .dockerignore file to exclude unnecessary files from Docker build context.

**Acceptance Criteria:**
- File exists at `backend/.dockerignore`
- Excludes __pycache__, .venv, .git, etc.
- Reduces build context size
- Docker build is faster

**Implementation Steps:**
1. Create `backend/.dockerignore`
2. Add exclusions:
   - __pycache__
   - .venv
   - .git
   - .env
   - *.pyc
   - .pytest_cache

**File Location:** `backend/.dockerignore`

**Content:**
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
.venv
.env
.env.local
.git
.gitignore
*.md
.pytest_cache
.coverage
htmlcov
dist
build
*.egg-info
.vscode
.idea
*.log
```

**Testing:**
```bash
cd backend
time docker build -t todo-backend:test .
```

**References:**
- Plan: Performance Optimization > Docker Image Optimization

---

### T-011: Add Backend Health Check Endpoint
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** None

**Description:**
Create a health check endpoint in FastAPI that returns 200 OK.

**Acceptance Criteria:**
- Endpoint exists at `/health`
- Returns 200 status code
- Returns JSON with status and timestamp
- Does not require authentication

**Implementation Steps:**
1. Open `backend/main.py`
2. Add health check route:
   ```python
   from datetime import datetime

   @app.get("/health")
   async def health_check():
       return {
           "status": "healthy",
           "timestamp": datetime.utcnow().isoformat()
       }
   ```

**File Location:** `backend/main.py`

**Testing:**
```bash
# Start dev server
uvicorn main:app --reload

# Test endpoint
curl http://localhost:8000/health
# Should return: {"status":"healthy","timestamp":"..."}
```

**References:**
- Spec: US-4.2 Acceptance Criteria > Health check endpoint
- Plan: Health Checks > Backend Health Endpoint

---

### T-012: Build Backend Docker Image
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** T-009, T-010, T-011

**Description:**
Build the backend Docker image and verify it works correctly.

**Acceptance Criteria:**
- Image builds successfully
- Image size is under 300MB
- Image is tagged as `todo-backend:latest`
- Image is available in Minikube

**Implementation Steps:**
1. Ensure Docker is using Minikube daemon: `eval $(minikube docker-env)`
2. Build image:
   ```bash
   cd backend
   docker build -t todo-backend:latest .
   ```
3. Verify image exists:
   ```bash
   docker images | grep todo-backend
   ```

**Testing:**
```bash
# Check image size
docker images todo-backend:latest
# Size should be < 300MB

# Verify in Minikube
minikube ssh -- docker images | grep todo-backend
```

**References:**
- Spec: US-4.2 > Image size is under 300MB
- Plan: Phase 1: Containerization > Step 1: Build Docker Images

---

### T-013: Test Backend Container Locally
**Priority:** P1
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-012

**Description:**
Run the backend container locally and verify it works correctly.

**Acceptance Criteria:**
- Container starts without errors
- API is accessible at http://localhost:8000
- Health check endpoint returns 200
- API docs are accessible at http://localhost:8000/docs
- Can connect to Neon database

**Implementation Steps:**
1. Get DATABASE_URL from .env
2. Run container:
   ```bash
   docker run -p 8000:8000 \
     -e DATABASE_URL="postgresql://..." \
     -e JWT_SECRET="test-secret" \
     todo-backend:latest
   ```
3. Test health endpoint: `curl http://localhost:8000/health`
4. Check API docs: http://localhost:8000/docs
5. Stop container: Ctrl+C

**Testing:**
```bash
# Start container
docker run -d -p 8000:8000 \
  -e DATABASE_URL="$DATABASE_URL" \
  -e JWT_SECRET="test" \
  --name test-backend \
  todo-backend:latest

# Check health
curl http://localhost:8000/health

# Check logs
docker logs test-backend

# Cleanup
docker stop test-backend
docker rm test-backend
```

**References:**
- Spec: US-4.3 Developer Tests Containers Locally
- Plan: Phase 1 > Step 2: Test Containers Locally

---

## Group 4: Helm Chart Creation (P0)

### T-014: Initialize Helm Chart Structure
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** None

**Description:**
Create the Helm chart directory structure and base files.

**Acceptance Criteria:**
- Directory exists at `k8s/helm/todo-app/`
- Chart.yaml contains proper metadata
- values.yaml exists with default values
- templates/ directory exists
- _helpers.tpl exists

**Implementation Steps:**
1. Create directory structure:
   ```bash
   mkdir -p k8s/helm/todo-app/templates
   ```
2. Create Chart.yaml
3. Create values.yaml with default configuration
4. Create templates/_helpers.tpl with template functions
5. Create .helmignore

**File Locations:**
- `k8s/helm/todo-app/Chart.yaml`
- `k8s/helm/todo-app/values.yaml`
- `k8s/helm/todo-app/templates/_helpers.tpl`
- `k8s/helm/todo-app/.helmignore`

**Testing:**
```bash
# Lint chart
helm lint k8s/helm/todo-app

# Should pass with no errors
```

**References:**
- Spec: US-4.4 Developer Creates Helm Chart Structure
- Plan: Helm Chart Structure

---

### T-015: Create Chart.yaml
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 10 minutes
**Dependencies:** T-014

**Description:**
Create Chart.yaml with proper metadata for the Helm chart.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/Chart.yaml`
- Contains required fields: apiVersion, name, version, description
- Version is 1.0.0
- appVersion matches application version

**Implementation Steps:**
1. Create `k8s/helm/todo-app/Chart.yaml`
2. Add metadata:
   - apiVersion: v2
   - name: todo-app
   - description: Todo AI Chatbot Full Stack Application
   - type: application
   - version: 1.0.0
   - appVersion: "1.0.0"

**File Location:** `k8s/helm/todo-app/Chart.yaml`

**Content:**
```yaml
apiVersion: v2
name: todo-app
description: Todo AI Chatbot - Full Stack Application
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - todo
  - chatbot
  - nextjs
  - fastapi
maintainers:
  - name: irza16
```

**Testing:**
```bash
helm lint k8s/helm/todo-app
```

**References:**
- Plan: Helm Chart Structure > Chart.yaml

---

### T-016: Create values.yaml
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-014

**Description:**
Create values.yaml with all configurable parameters for the application.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/values.yaml`
- Contains frontend configuration
- Contains backend configuration
- All values have sensible defaults
- Well-documented with comments

**Implementation Steps:**
1. Create `k8s/helm/todo-app/values.yaml`
2. Add frontend section (image, replicas, service, resources)
3. Add backend section (image, replicas, service, resources, secrets)
4. Add configuration for ConfigMaps and Secrets
5. Add comments explaining each value

**File Location:** `k8s/helm/todo-app/values.yaml`

**Key Sections:**
- frontend.image
- frontend.replicaCount
- frontend.service
- frontend.resources
- backend.image
- backend.replicaCount
- backend.service
- backend.resources
- backend.secrets

**Testing:**
```bash
helm lint k8s/helm/todo-app
helm template todo-app k8s/helm/todo-app
```

**References:**
- Plan: Helm Chart Structure > values.yaml

---

### T-017: Create Frontend Deployment Template
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 45 minutes
**Dependencies:** T-016

**Description:**
Create Kubernetes Deployment template for the frontend service.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/frontend-deployment.yaml`
- Uses values from values.yaml
- Includes resource requests and limits
- Includes readiness and liveness probes
- Includes environment variables from ConfigMap
- Template renders correctly

**Implementation Steps:**
1. Create file: `templates/frontend-deployment.yaml`
2. Define Deployment resource
3. Reference values with `{{ .Values.frontend.* }}`
4. Add container spec with:
   - Image from values
   - Resource limits
   - Environment variables
   - Health probes
5. Add labels for organization

**File Location:** `k8s/helm/todo-app/templates/frontend-deployment.yaml`

**Testing:**
```bash
helm template todo-app k8s/helm/todo-app | grep -A 50 "kind: Deployment" | grep -A 50 "frontend"
```

**References:**
- Spec: US-4.5 Developer Defines Frontend Kubernetes Resources
- Plan: Component Design > 2.1 Deployments > Frontend Deployment

---

### T-018: Create Frontend Service Template
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-017

**Description:**
Create Kubernetes Service template for the frontend.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/frontend-service.yaml`
- Type is ClusterIP (configurable)
- Exposes port 3000
- Selector matches deployment labels
- Template renders correctly

**Implementation Steps:**
1. Create file: `templates/frontend-service.yaml`
2. Define Service resource
3. Reference values for type and port
4. Set selector to match deployment labels
5. Add annotations if needed

**File Location:** `k8s/helm/todo-app/templates/frontend-service.yaml`

**Testing:**
```bash
helm template todo-app k8s/helm/todo-app | grep -A 20 "kind: Service" | grep -A 20 "frontend"
```

**References:**
- Spec: US-4.5 > Service template exists for frontend
- Plan: Component Design > 2.2 Services > Frontend Service

---

### T-019: Create Frontend ConfigMap Template
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** T-017

**Description:**
Create Kubernetes ConfigMap template for frontend configuration.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/frontend-configmap.yaml`
- Contains NEXT_PUBLIC_API_URL
- Value references backend service name
- Template renders correctly

**Implementation Steps:**
1. Create file: `templates/frontend-configmap.yaml`
2. Define ConfigMap resource
3. Add data:
   - NEXT_PUBLIC_API_URL: http://todo-backend:8000
   - NODE_ENV: production

**File Location:** `k8s/helm/todo-app/templates/frontend-configmap.yaml`

**Testing:**
```bash
helm template todo-app k8s/helm/todo-app | grep -A 10 "kind: ConfigMap" | grep -A 10 "frontend"
```

**References:**
- Plan: Component Design > 2.3 ConfigMaps > Frontend ConfigMap

---

### T-020: Create Backend Deployment Template
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 45 minutes
**Dependencies:** T-016

**Description:**
Create Kubernetes Deployment template for the backend service.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/backend-deployment.yaml`
- Uses values from values.yaml
- Includes resource requests and limits
- Includes readiness and liveness probes
- Includes environment variables from ConfigMap and Secret
- Template renders correctly

**Implementation Steps:**
1. Create file: `templates/backend-deployment.yaml`
2. Define Deployment resource
3. Reference values with `{{ .Values.backend.* }}`
4. Add container spec with:
   - Image from values
   - Resource limits
   - Environment variables from ConfigMap
   - Secret references for DATABASE_URL and JWT_SECRET
   - Health probes
5. Add labels

**File Location:** `k8s/helm/todo-app/templates/backend-deployment.yaml`

**Testing:**
```bash
helm template todo-app k8s/helm/todo-app | grep -A 50 "kind: Deployment" | grep -A 50 "backend"
```

**References:**
- Spec: US-4.6 Developer Defines Backend Kubernetes Resources
- Plan: Component Design > 2.1 Deployments > Backend Deployment

---

### T-021: Create Backend Service Template
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-020

**Description:**
Create Kubernetes Service template for the backend.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/backend-service.yaml`
- Type is ClusterIP
- Exposes port 8000
- Selector matches deployment labels
- Template renders correctly

**Implementation Steps:**
1. Create file: `templates/backend-service.yaml`
2. Define Service resource
3. Reference values for port
4. Set selector to match deployment labels
5. Name must be "todo-backend" for DNS resolution

**File Location:** `k8s/helm/todo-app/templates/backend-service.yaml`

**Testing:**
```bash
helm template todo-app k8s/helm/todo-app | grep -A 20 "kind: Service" | grep -A 20 "backend"
```

**References:**
- Spec: US-4.6 > Service template exists for backend
- Plan: Component Design > 2.2 Services > Backend Service

---

### T-022: Create Backend ConfigMap Template
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** T-020

**Description:**
Create Kubernetes ConfigMap template for backend configuration.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/backend-configmap.yaml`
- Contains non-sensitive configuration
- Values come from values.yaml
- Template renders correctly

**Implementation Steps:**
1. Create file: `templates/backend-configmap.yaml`
2. Define ConfigMap resource
3. Add data:
   - CORS_ORIGIN
   - LOG_LEVEL
   - PYTHONUNBUFFERED

**File Location:** `k8s/helm/todo-app/templates/backend-configmap.yaml`

**Testing:**
```bash
helm template todo-app k8s/helm/todo-app | grep -A 10 "kind: ConfigMap" | grep -A 10 "backend"
```

**References:**
- Plan: Component Design > 2.3 ConfigMaps > Backend ConfigMap

---

### T-023: Create Backend Secret Template
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-020

**Description:**
Create Kubernetes Secret template for backend sensitive configuration.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/backend-secret.yaml`
- Contains DATABASE_URL and JWT_SECRET
- Values come from values.yaml (or helm install --set)
- Uses base64 encoding if needed
- Template renders correctly

**Implementation Steps:**
1. Create file: `templates/backend-secret.yaml`
2. Define Secret resource
3. Add stringData (Kubernetes handles base64):
   - database-url
   - jwt-secret
4. Reference values from .Values.backend.secrets

**File Location:** `k8s/helm/todo-app/templates/backend-secret.yaml`

**Testing:**
```bash
helm template todo-app k8s/helm/todo-app \
  --set backend.secrets.databaseUrl="test" \
  --set backend.secrets.jwtSecret="test" \
  | grep -A 10 "kind: Secret"
```

**References:**
- Spec: US-4.6 > Secret template exists for sensitive config
- Plan: Component Design > 2.4 Secrets

---

### T-024: Create Template Helpers
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-014

**Description:**
Create helper template functions for consistent naming and labels.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/_helpers.tpl`
- Contains name helper function
- Contains fullname helper function
- Contains label helpers
- Helpers are used in all templates

**Implementation Steps:**
1. Create file: `templates/_helpers.tpl`
2. Add `todo-app.name` helper
3. Add `todo-app.fullname` helper
4. Add `todo-app.labels` helper
5. Add `todo-app.selectorLabels` helper
6. Update all templates to use helpers

**File Location:** `k8s/helm/todo-app/templates/_helpers.tpl`

**Testing:**
```bash
helm template todo-app k8s/helm/todo-app | grep "app.kubernetes.io"
# Should show consistent labels across all resources
```

**References:**
- Plan: Helm Chart Structure > templates/_helpers.tpl

---

### T-025: Create NOTES.txt
**Priority:** P1
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-014

**Description:**
Create NOTES.txt with post-install instructions for users.

**Acceptance Criteria:**
- File exists at `k8s/helm/todo-app/templates/NOTES.txt`
- Shows how to check pod status
- Shows how to access the application
- Shows helpful troubleshooting commands
- Displays after helm install

**Implementation Steps:**
1. Create file: `templates/NOTES.txt`
2. Add instructions for:
   - Checking deployment status
   - Port-forwarding to access app
   - Viewing logs
   - Getting service info
3. Use template syntax to show actual release name

**File Location:** `k8s/helm/todo-app/templates/NOTES.txt`

**Testing:**
```bash
helm install test-release k8s/helm/todo-app --dry-run
# Should display NOTES at the end
```

**References:**
- Plan: Helm Chart Structure > NOTES.txt

---

### T-026: Validate Helm Chart
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-014 through T-025

**Description:**
Validate the Helm chart for errors and best practices.

**Acceptance Criteria:**
- `helm lint` passes without errors
- `helm template` generates valid YAML
- Dry-run install succeeds
- All templates use values correctly
- No hardcoded values (except defaults)

**Implementation Steps:**
1. Run helm lint:
   ```bash
   helm lint k8s/helm/todo-app
   ```
2. Run helm template:
   ```bash
   helm template todo-app k8s/helm/todo-app > /tmp/output.yaml
   ```
3. Validate YAML:
   ```bash
   kubectl apply --dry-run=client -f /tmp/output.yaml
   ```
4. Dry-run install:
   ```bash
   helm install test-release k8s/helm/todo-app --dry-run --debug
   ```
5. Fix any errors found

**Testing:**
```bash
# All should pass without errors
helm lint k8s/helm/todo-app
helm template todo-app k8s/helm/todo-app > /tmp/output.yaml
kubectl apply --dry-run=client -f /tmp/output.yaml
```

**References:**
- Spec: US-4.4 > Chart passes helm lint validation
- Plan: Phase 2: Helm Chart Development > Step 2: Validate Chart

---

## Group 5: Deployment to Minikube (P0)

### T-027: Deploy Application to Minikube
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-007, T-012, T-026

**Description:**
Install the Helm chart to deploy the application to Minikube.

**Acceptance Criteria:**
- Helm install command succeeds
- All pods reach Running state within 60 seconds
- No pod restarts (0 in RESTARTS column)
- Services are created
- ConfigMaps and Secrets are created

**Implementation Steps:**
1. Get DATABASE_URL and JWT_SECRET values
2. Install chart:
   ```bash
   helm install todo-app k8s/helm/todo-app \
     --set backend.secrets.databaseUrl="$DATABASE_URL" \
     --set backend.secrets.jwtSecret="$JWT_SECRET"
   ```
3. Watch pods start:
   ```bash
   kubectl get pods -w
   ```
4. Wait for all pods to be Running
5. Verify deployment:
   ```bash
   kubectl get all
   ```

**Testing:**
```bash
# Check pod status
kubectl get pods
# All should show Running with 0 restarts

# Check services
kubectl get svc

# Check events for errors
kubectl get events --sort-by='.lastTimestamp'
```

**References:**
- Spec: US-4.7 Developer Deploys to Minikube
- Plan: Phase 3: Deployment to Minikube > Step 2: Install Helm Chart

---

### T-028: Verify Pod Health
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-027

**Description:**
Verify that all pods are healthy and ready to serve traffic.

**Acceptance Criteria:**
- All pods show 1/1 READY
- Liveness probes are passing
- Readiness probes are passing
- No errors in pod logs
- Health check endpoints return 200

**Implementation Steps:**
1. Check pod status:
   ```bash
   kubectl get pods
   ```
2. Describe pods:
   ```bash
   kubectl describe pod <frontend-pod>
   kubectl describe pod <backend-pod>
   ```
3. Check logs:
   ```bash
   kubectl logs -f <frontend-pod>
   kubectl logs -f <backend-pod>
   ```
4. Test health endpoints from within pods:
   ```bash
   kubectl exec <frontend-pod> -- curl http://localhost:3000/api/health
   kubectl exec <backend-pod> -- curl http://localhost:8000/health
   ```

**Testing:**
```bash
# All should show Running and 1/1 READY
kubectl get pods

# Should show no errors in events
kubectl describe pod <pod-name> | grep -A 10 Events
```

**References:**
- Spec: US-4.7 > All pods reach Running state
- Plan: Phase 4: Testing and Validation > Health Checks

---

### T-029: Verify Service Communication
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-028

**Description:**
Verify that frontend can communicate with backend via Kubernetes service.

**Acceptance Criteria:**
- Frontend pod can reach backend service
- Backend service resolves via DNS
- API requests succeed
- No network errors

**Implementation Steps:**
1. Get frontend pod name
2. Exec into frontend pod:
   ```bash
   kubectl exec -it <frontend-pod> -- /bin/sh
   ```
3. Test backend connectivity:
   ```bash
   curl http://todo-backend:8000/health
   ```
4. Should return: `{"status":"healthy",...}`
5. Exit pod: `exit`

**Testing:**
```bash
# From frontend pod
kubectl exec <frontend-pod> -- curl -s http://todo-backend:8000/health

# Should return healthy status
```

**References:**
- Spec: US-4.7 > Frontend pod is accessible via service
- Plan: Networking > Internal Communication

---

### T-030: Verify Database Connectivity
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** T-028

**Description:**
Verify that backend pod can connect to external Neon database.

**Acceptance Criteria:**
- Backend pod has DATABASE_URL from secret
- Connection to Neon database succeeds
- No database connection errors in logs
- Can execute test query

**Implementation Steps:**
1. Check backend logs for database connection:
   ```bash
   kubectl logs <backend-pod> | grep -i database
   ```
2. Exec into backend pod:
   ```bash
   kubectl exec -it <backend-pod> -- /bin/bash
   ```
3. Test database connection (if psql available):
   ```bash
   echo $DATABASE_URL
   ```
4. Check for connection errors in application logs

**Testing:**
```bash
# Check logs for successful database connection
kubectl logs <backend-pod> | grep -i "database\|connection"

# Should show successful connection, no errors
```

**References:**
- Spec: US-4.7 > Backend pod can connect to Neon database
- Plan: Networking > Database Access

---

### T-031: Access Application via Port-Forward
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** T-029

**Description:**
Access the deployed application from local browser using port-forwarding.

**Acceptance Criteria:**
- Port-forward command succeeds
- Application loads at http://localhost:3000
- Can navigate through pages
- No console errors
- Backend API is accessible

**Implementation Steps:**
1. Port-forward frontend service:
   ```bash
   kubectl port-forward service/todo-frontend 3000:3000
   ```
2. Open browser to http://localhost:3000
3. Verify application loads
4. Test navigation
5. Keep port-forward running for testing

**Testing:**
```bash
# In terminal 1: Port-forward
kubectl port-forward service/todo-frontend 3000:3000

# In terminal 2: Test access
curl http://localhost:3000
# Should return HTML

# Open in browser
open http://localhost:3000
```

**References:**
- Spec: US-4.8 Developer Accesses Application Locally
- Plan: Networking > External Access

---

### T-032: Test Application Functionality
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-031

**Description:**
Test all application features to ensure they work correctly in Kubernetes.

**Acceptance Criteria:**
- User can sign up
- User can log in
- User can create tasks
- User can view tasks
- User can update tasks
- User can mark tasks complete
- User can delete tasks
- All functionality from Phase 3 works

**Implementation Steps:**
1. With port-forward running, open http://localhost:3000
2. Test signup flow
3. Test login flow
4. Test task creation
5. Test task listing
6. Test task update
7. Test task completion
8. Test task deletion
9. Document any issues

**Testing:**
```
Manual test checklist:
[ ] Sign up with new account
[ ] Log in with credentials
[ ] Create a task
[ ] View task in list
[ ] Update task title
[ ] Mark task as complete
[ ] Mark task as incomplete
[ ] Delete task
[ ] Verify all operations persist
```

**References:**
- Spec: US-4.8 > All functionality from Phase 3 works identically
- Plan: Phase 4: Testing and Validation > Integration Testing

---

## Group 6: Documentation (P1)

### T-033: Create Kubernetes README
**Priority:** P1
**Status:** ⬜
**Estimated Time:** 1 hour
**Dependencies:** T-032

**Description:**
Create comprehensive documentation for deploying the application to Kubernetes.

**Acceptance Criteria:**
- File exists at `k8s/README.md`
- Includes prerequisites
- Includes step-by-step deployment instructions
- Includes verification steps
- Includes access instructions
- Includes troubleshooting section
- Includes cleanup instructions
- All commands are tested and work

**Implementation Steps:**
1. Create `k8s/README.md`
2. Add sections:
   - Prerequisites
   - Setup Minikube
   - Build Docker Images
   - Deploy with Helm
   - Verify Deployment
   - Access Application
   - Troubleshooting
   - Cleanup
3. Add actual commands (not placeholders)
4. Test all commands
5. Add screenshots (optional)

**File Location:** `k8s/README.md`

**Sections:**
- Prerequisites
- Minikube Setup
- Docker Image Build
- Helm Chart Deployment
- Verification Steps
- Accessing the App
- Troubleshooting
- Cleanup

**Testing:**
```bash
# Follow your own README from scratch
# Ensure all commands work
```

**References:**
- Spec: US-4.11 Developer Documents Deployment Process
- Plan: Documentation Validation

---

### T-034: Update Root README
**Priority:** P1
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-033

**Description:**
Update the root README.md to include Phase 4 information.

**Acceptance Criteria:**
- Root README.md is updated
- Includes Phase 4 section
- Links to k8s/README.md
- Mentions Kubernetes deployment
- Updated tech stack section

**Implementation Steps:**
1. Open root `README.md`
2. Add Phase 4 section
3. Update tech stack to include:
   - Docker
   - Kubernetes
   - Helm
   - Minikube
4. Add link to k8s/README.md
5. Update deployment section

**File Location:** `README.md`

**Testing:**
```bash
# Read through README
# Verify all links work
```

**References:**
- Spec: Deliverables > Documentation

---

### T-035: Add Deployment Diagram
**Priority:** P2
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-033

**Description:**
Create an architecture diagram showing the Kubernetes deployment.

**Acceptance Criteria:**
- Diagram shows pods, services, configmaps, secrets
- Diagram shows networking between components
- Diagram shows external database connection
- Saved as image in k8s/docs/
- Referenced in README

**Implementation Steps:**
1. Create diagram using draw.io, Excalidraw, or ASCII art
2. Show:
   - Minikube cluster boundary
   - Frontend pod + service
   - Backend pod + service
   - ConfigMaps
   - Secrets
   - External database
   - Network connections
3. Save as PNG or SVG
4. Add to k8s/docs/architecture.png
5. Reference in README

**File Location:** `k8s/docs/architecture.png`

**Testing:**
```bash
# Verify image displays in README
```

**References:**
- Plan: System Architecture diagrams

---

## Group 7: AI DevOps Tools (P2 - Optional)

### T-036: Install kubectl-ai
**Priority:** P2
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-002

**Description:**
Install and configure kubectl-ai for AI-assisted Kubernetes operations.

**Acceptance Criteria:**
- kubectl-ai is installed
- OpenAI API key is configured
- Can run simple kubectl-ai commands
- Commands execute successfully

**Implementation Steps:**
1. Install kubectl-ai:
   ```bash
   # macOS
   brew install kubectl-ai

   # Or download binary
   ```
2. Configure OpenAI API key:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```
3. Test:
   ```bash
   kubectl-ai "list all pods"
   ```

**Testing:**
```bash
kubectl-ai "show me the status of all pods"
kubectl-ai "describe the todo-frontend service"
```

**References:**
- Spec: US-4.9 Developer Uses kubectl-ai for Operations
- Plan: kubectl-ai and kagent Integration

---

### T-037: Install kagent
**Priority:** P2
**Status:** ⬜
**Estimated Time:** 20 minutes
**Dependencies:** T-002

**Description:**
Install and configure kagent for advanced cluster management.

**Acceptance Criteria:**
- kagent is installed
- Can run kagent commands
- Provides useful insights

**Implementation Steps:**
1. Install kagent:
   ```bash
   pip install kagent
   # Or follow official guide
   ```
2. Test:
   ```bash
   kagent "analyze cluster health"
   ```

**Testing:**
```bash
kagent "analyze the cluster health"
kagent "optimize resource allocation"
```

**References:**
- Spec: US-4.10 Developer Uses kagent for Cluster Management
- Plan: kubectl-ai and kagent Integration

---

### T-038: Document AI DevOps Usage
**Priority:** P2
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-036, T-037

**Description:**
Document examples of using kubectl-ai and kagent for this project.

**Acceptance Criteria:**
- Examples added to k8s/README.md
- Shows practical use cases
- Includes sample outputs
- Explains benefits

**Implementation Steps:**
1. Add section to k8s/README.md: "AI-Assisted Operations"
2. Add kubectl-ai examples
3. Add kagent examples
4. Show actual outputs
5. Explain when to use each tool

**File Location:** `k8s/README.md` (new section)

**Testing:**
```bash
# Follow examples in README
# Verify they work
```

**References:**
- Spec: US-4.9, US-4.10
- Plan: kubectl-ai and kagent Integration

---

## Group 8: Demo and Submission (P0)

### T-039: Record Demo Video
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 1 hour
**Dependencies:** T-032

**Description:**
Record a demo video showing the Kubernetes deployment and application functionality.

**Acceptance Criteria:**
- Video is under 90 seconds
- Shows helm install command
- Shows pods starting
- Shows kubectl commands
- Shows application running
- Shows at least one task operation
- Video quality is clear
- Audio is clear (if included)

**Implementation Steps:**
1. Plan video structure (30 seconds intro, 45 seconds demo, 15 seconds outro)
2. Practice walkthrough
3. Record screen:
   - Show helm install
   - Show kubectl get pods -w
   - Show port-forward command
   - Show browser with application
   - Create/complete a task
4. Edit video if needed
5. Export as MP4
6. Upload to YouTube/Vimeo/Google Drive
7. Get shareable link

**Content Outline:**
```
0:00-0:15  Introduction
0:15-0:30  Show helm install command
0:30-0:45  Show pods starting (kubectl get pods -w)
0:45-1:00  Show port-forward and browser
1:00-1:20  Demonstrate task operations
1:20-1:30  Conclusion
```

**Testing:**
```bash
# Watch video
# Verify under 90 seconds
# Verify all requirements shown
```

**References:**
- Spec: US-4.12 Developer Creates Demo Video
- Hackathon Requirements > Demo video link

---

### T-040: Prepare Submission Package
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 30 minutes
**Dependencies:** T-039

**Description:**
Prepare all materials for hackathon submission.

**Acceptance Criteria:**
- GitHub repository is public
- All code is committed and pushed
- README is up to date
- Demo video link is ready
- Vercel deployment link (Phase 3) is ready
- Submission form is filled out

**Implementation Steps:**
1. Commit all changes:
   ```bash
   git add .
   git commit -m "Phase 4 complete: Kubernetes deployment"
   git push origin phase-4-kubernetes
   ```
2. Merge to main (optional):
   ```bash
   git checkout main
   git merge phase-4-kubernetes
   git push origin main
   ```
3. Tag release:
   ```bash
   git tag phase-4-submission
   git push origin phase-4-submission
   ```
4. Verify GitHub repo is public
5. Get repository URL
6. Get demo video URL
7. Prepare Phase 3 Vercel URL

**Checklist:**
```
[ ] GitHub repo is public
[ ] All code is pushed
[ ] README is complete
[ ] Demo video is uploaded
[ ] Video link is accessible
[ ] Vercel link works
[ ] All links tested
```

**Testing:**
```bash
# Open repo in private/incognito window
# Verify it's accessible
# Click all links
```

**References:**
- Hackathon Requirements > Submit and Present Your Project

---

### T-041: Submit to Hackathon
**Priority:** P0
**Status:** ⬜
**Estimated Time:** 15 minutes
**Dependencies:** T-040

**Description:**
Submit Phase 4 via the hackathon submission form.

**Acceptance Criteria:**
- Form is submitted successfully
- Received confirmation (if applicable)
- All required fields are filled
- Links are correct and working

**Implementation Steps:**
1. Go to: https://forms.gle/KMKEKaFUD6ZX4UtY8
2. Fill in:
   - Public GitHub Repo Link
   - Published App Link (Vercel from Phase 3)
   - Demo video link
   - WhatsApp number
3. Double-check all links work
4. Submit form
5. Screenshot confirmation page

**Form Fields:**
- GitHub Repository: https://github.com/irza16/todo-console-app
- Vercel Link: https://todo-console-app-orcin.vercel.app
- Demo Video: [Your YouTube/Drive link]
- WhatsApp: [Your number]

**Testing:**
```bash
# Test all links in private browser
# Verify they work for someone else
```

**References:**
- Hackathon Requirements > Submission Deadline: January 4, 2026

---

## Task Summary

**Total Tasks:** 41

**By Priority:**
- P0 (Critical): 33 tasks
- P1 (High): 5 tasks
- P2 (Medium): 3 tasks

**By Group:**
- Environment Setup: 3 tasks
- Frontend Containerization: 5 tasks
- Backend Containerization: 5 tasks
- Helm Chart Creation: 13 tasks
- Deployment to Minikube: 6 tasks
- Documentation: 3 tasks
- AI DevOps Tools: 3 tasks (optional)
- Demo and Submission: 3 tasks

**Estimated Total Time:** 16-20 hours

**Critical Path:**
T-001 → T-002 → T-003 → T-004 → T-007 → T-009 → T-012 → T-014 → T-026 → T-027 → T-032 → T-039 → T-041

---

## Notes for Implementation

### Using Spec-Driven Development
Each task should be implemented by:
1. Reading the task description
2. Understanding acceptance criteria
3. Writing code (via Claude Code if following hackathon rules)
4. Testing against acceptance criteria
5. Marking task as complete

### Testing Strategy
- Test each task immediately after completion
- Don't proceed to dependent tasks until current task passes
- Keep notes of any deviations from plan
- Update specs if requirements change

### Time Management
- Focus on P0 tasks first (critical path)
- P1 tasks are important but can be simplified if time-constrained
- P2 tasks are optional enhancements
- Save P3 for after submission if time permits

### Troubleshooting
- Reference the Troubleshooting Guide in the Plan
- Check pod logs: `kubectl logs <pod-name>`
- Describe resources: `kubectl describe <resource-type> <name>`
- Check events: `kubectl get events --sort-by='.lastTimestamp'`

### Getting Help
- Consult Docker documentation
- Consult Kubernetes documentation
- Consult Helm documentation
- Use kubectl-ai/kagent for AI assistance
- Ask Claude Code for spec-driven solutions

---

## Completion Checklist

Before marking Phase 4 complete, verify:

- [ ] All P0 tasks are complete
- [ ] Docker images build successfully
- [ ] Helm chart installs without errors
- [ ] All pods are Running
- [ ] Application is accessible
- [ ] All Phase 3 features work
- [ ] Documentation is complete
- [ ] Demo video is recorded
- [ ] Submission is completed

**Phase 4 is complete when all P0 tasks are ✅ and the application is deployed and working in Minikube.**

The tasks.md should be immediately executable - each task must be specific enough that an LLM can complete it without additional context.

## Task Generation Rules

**CRITICAL**: Tasks MUST be organized by user story to enable independent implementation and testing.

**Tests are OPTIONAL**: Only generate test tasks if explicitly requested in the feature specification or if user requests TDD approach.

### Checklist Format (REQUIRED)

Every task MUST strictly follow this format:

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

**Format Components**:

1. **Checkbox**: ALWAYS start with `- [ ]` (markdown checkbox)
2. **Task ID**: Sequential number (T001, T002, T003...) in execution order
3. **[P] marker**: Include ONLY if task is parallelizable (different files, no dependencies on incomplete tasks)
4. **[Story] label**: REQUIRED for user story phase tasks only
   - Format: [US1], [US2], [US3], etc. (maps to user stories from spec.md)
   - Setup phase: NO story label
   - Foundational phase: NO story label
   - User Story phases: MUST have story label
   - Polish phase: NO story label
5. **Description**: Clear action with exact file path

**Examples**:

- ✅ CORRECT: `- [ ] T001 Create project structure per implementation plan`
- ✅ CORRECT: `- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- ✅ CORRECT: `- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- ✅ CORRECT: `- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- ❌ WRONG: `- [ ] Create User model` (missing ID and Story label)
- ❌ WRONG: `T001 [US1] Create model` (missing checkbox)
- ❌ WRONG: `- [ ] [US1] Create User model` (missing Task ID)
- ❌ WRONG: `- [ ] T001 [US1] Create model` (missing file path)

### Task Organization

1. **From User Stories (spec.md)** - PRIMARY ORGANIZATION:
   - Each user story (P1, P2, P3...) gets its own phase
   - Map all related components to their story:
     - Models needed for that story
     - Services needed for that story
     - Endpoints/UI needed for that story
     - If tests requested: Tests specific to that story
   - Mark story dependencies (most stories should be independent)

2. **From Contracts**:
   - Map each contract/endpoint → to the user story it serves
   - If tests requested: Each contract → contract test task [P] before implementation in that story's phase

3. **From Data Model**:
   - Map each entity to the user story(ies) that need it
   - If entity serves multiple stories: Put in earliest story or Setup phase
   - Relationships → service layer tasks in appropriate story phase

4. **From Setup/Infrastructure**:
   - Shared infrastructure → Setup phase (Phase 1)
   - Foundational/blocking tasks → Foundational phase (Phase 2)
   - Story-specific setup → within that story's phase

### Phase Structure

- **Phase 1**: Setup (project initialization)
- **Phase 2**: Foundational (blocking prerequisites - MUST complete before user stories)
- **Phase 3+**: User Stories in priority order (P1, P2, P3...)
  - Within each story: Tests (if requested) → Models → Services → Endpoints → Integration
  - Each phase should be a complete, independently testable increment
- **Final Phase**: Polish & Cross-Cutting Concerns

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record) using agent‑native tools when possible.

1) Determine Stage
   - Stage: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate Title and Determine Routing:
   - Generate Title: 3–7 words (slug for filename)
   - Route is automatically determined by stage:
     - `constitution` → `history/prompts/constitution/`
     - Feature stages → `history/prompts/<feature-name>/` (spec, plan, tasks, red, green, refactor, explainer, misc)
     - `general` → `history/prompts/general/`

3) Create and Fill PHR (Shell first; fallback agent‑native)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Open the file and fill remaining placeholders (YAML + body), embedding full PROMPT_TEXT (verbatim) and concise RESPONSE_TEXT.
   - If the script fails:
     - Read `.specify/templates/phr-template.prompt.md` (or `templates/…`)
     - Allocate an ID; compute the output path based on stage from step 2; write the file
     - Fill placeholders and embed full PROMPT_TEXT and concise RESPONSE_TEXT

4) Validate + report
   - No unresolved placeholders; path under `history/prompts/` and matches stage; stage/title/date coherent; print ID + path + stage + title.
   - On failure: warn, don't block. Skip only for `/sp.phr`.
```

## Response snapshot

I have successfully generated the tasks for Phase 4: Kubernetes Deployment based on the specification and plan. The tasks.md file contains 53 tasks organized in phases from setup through to final validation and submission. The tasks follow the required checklist format with sequential IDs, appropriate story labels for user-story-related tasks, and clear descriptions with file paths where applicable.

The tasks are organized in the following phases:
1. Setup Phase - Environment setup tasks
2. Foundational Phase - Containerization and Helm chart foundation
3. User Story 1-7 - Specific functionality tasks mapped to user stories
4. Polish Phase - Final validation and submission tasks

Each task follows the required format with checkboxes, sequential IDs, story labels where appropriate, and clear descriptions. Dependencies and parallel execution opportunities have been identified to help with project planning.

## Outcome

- ✅ Impact: Complete task breakdown created for Kubernetes deployment phase
- 🧪 Tests: Task format validated against requirements
- 📁 Files: specs/005-kubernetes-deployment/tasks.md created
- 🔁 Next prompts: Ready for /sp.implement to execute tasks
- 🧠 Reflection: Tasks organized by user stories for independent implementation

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All requirements met
- Prompt variant (if applicable): Standard task generation
- Next experiment (smallest change to try): Begin implementation of setup phase tasks