---
id: 001
title: Phase 4 Planning
stage: plan
date: 2026-02-06
surface: agent
model: google/gemini-2.0-flash-exp:free
feature: kubernetes-deployment
branch: 005-kubernetes-deployment
user: irza
command: sp.plan
labels: [kubernetes, deployment, architecture, docker, helm]
links:
  spec: specs/005-kubernetes-deployment/spec.md
  plan: specs/005-kubernetes-deployment/plan.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-kubernetes-deployment/plan.md
  - specs/005-kubernetes-deployment/research.md
  - specs/005-kubernetes-deployment/data-model.md
  - specs/005-kubernetes-deployment/quickstart.md
tests:
  - architecture validation
  - constitution compliance check
  - security gate evaluation
  - performance gate evaluation
---

## Prompt

```text
# Phase 4 Plan: Kubernetes Deployment Architecture

## Executive Summary
This plan outlines the technical approach for containerizing and deploying the Todo AI Chatbot to a local Kubernetes cluster using Docker, Minikube, and Helm. The deployment maintains the existing two-service architecture (frontend + backend) while introducing container orchestration and declarative configuration management.

## System Architecture

### Current State (Phase 3)
```
┌─────────────────────────────────────────────┐
│  Local Development / Vercel                 │
│                                             │
│  ┌──────────────┐      ┌──────────────┐   │
│  │  Frontend    │─────▶│  Backend     │   │
│  │  (Next.js)   │      │  (FastAPI)   │   │
│  │  Port 3000   │      │  Port 8000   │   │
│  └──────────────┘      └──────┬───────┘   │
│                                │           │
└────────────────────────────────┼───────────┘
                                 │
                                 ▼
                        ┌──────────────┐
                        │   Neon DB    │
                        │ (PostgreSQL) │
                        └──────────────┘
```

### Target State (Phase 4)
```
┌────────────────────────────────────────────────────────────┐
│  Minikube Cluster (Local Kubernetes)                       │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Namespace: default                                 │  │
│  │                                                     │  │
│  │  ┌────────────────────┐    ┌────────────────────┐  │  │
│  │  │  Frontend Pod      │    │  Backend Pod       │  │  │
│  │  │  ┌──────────────┐  │    │  ┌──────────────┐  │  │  │
│  │  │  │ Next.js      │  │    │  │ FastAPI      │  │  │  │
│  │  │  │ Container    │  │    │  │ Container    │  │  │  │
│  │  │  │ Port: 3000   │  │    │  │ Port: 8000   │  │  │  │
│  │  │  └──────────────┘  │    │  └──────────────┘  │  │  │
│  │  │                    │    │                    │  │  │
│  │  │  ConfigMap ────────┤    │  ConfigMap ────────┤  │  │
│  │  │  (API_URL)         │    │  Secret ───────────┤  │  │
│  │  └────────────────────┘    │  (DB_URL, JWT)     │  │  │
│  │           │                └────────────────────┘  │  │
│  │           │                         │              │  │
│  │           │                         │              │  │
│  │  ┌────────▼────────┐      ┌────────▼────────┐    │  │
│  │  │  Service        │      │  Service        │    │  │
│  │  │  todo-frontend  │      │  todo-backend   │    │  │
│  │  │  ClusterIP:3000 │      │  ClusterIP:8000 │    │  │
│  │  └─────────────────┘      └─────────────────┘    │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  Access via:                                             │
│  - kubectl port-forward service/todo-frontend 3000:3000 │
│  - minikube service todo-frontend (if NodePort)         │
└──────────────────────────┬───────────────────────────────┘
                           │
                           │ External Connection
                           ▼
                  ┌──────────────┐
                  │   Neon DB    │
                  │ (PostgreSQL) │
                  │  (External)  │
                  └──────────────┘
```

## Component Design

### 1. Docker Images

#### 1.1 Frontend Image (todo-frontend)

**Dockerfile Strategy: Multi-Stage Build**

```dockerfile
# Stage 1: Build Stage
FROM node:20-alpine AS builder
- Install dependencies
- Build Next.js production bundle
- Output: .next/ directory with optimized build

# Stage 2: Runtime Stage
FROM node:20-alpine AS runner
- Copy built artifacts from builder
- Install only production dependencies
- Configure non-root user
- Expose port 3000
- Health check: curl /api/health
- CMD: npm start (runs production server)
```

**Key Decisions:**
- **Base Image:** node:20-alpine (small footprint, ~120MB)
- **Multi-Stage:** Separates build tools from runtime (reduces image size by ~60%)
- **User:** Run as 'node' user (UID 1000) for security
- **Health Check:** HTTP GET /api/health returns 200 OK

**Environment Variables:**
- `NEXT_PUBLIC_API_URL`: Backend service URL (from ConfigMap)
- `NODE_ENV`: production (hardcoded)

**Expected Size:** ~350-450MB

---

#### 1.2 Backend Image (todo-backend)

**Dockerfile Strategy: Multi-Stage Build**

```dockerfile
# Stage 1: Build Stage
FROM python:3.13-slim AS builder
- Create virtual environment
- Install build dependencies
- Install Python packages
- Output: /app/.venv/ with all dependencies

# Stage 2: Runtime Stage
FROM python:3.13-slim AS runner
- Copy virtual environment from builder
- Copy application code
- Configure non-root user (appuser)
- Expose port 8000
- Health check: curl /health
- CMD: uvicorn main:app --host 0.0.0.0 --port 8000
```

**Key Decisions:**
- **Base Image:** python:3.13-slim (smaller than full image, ~150MB)
- **Multi-Stage:** Build dependencies not needed at runtime
- **User:** Create 'appuser' (UID 1000) for security
- **Health Check:** HTTP GET /health returns {"status": "healthy"}

**Environment Variables:**
- `DATABASE_URL`: Neon PostgreSQL connection string (from Secret)
- `JWT_SECRET`: Signing key for tokens (from Secret)
- `CORS_ORIGIN`: Frontend URL (from ConfigMap)
- `PYTHONUNBUFFERED`: 1 (for proper logging)

**Expected Size:** ~250-300MB

---

### 2. Kubernetes Resources

#### 2.1 Deployments

**Frontend Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend
  labels:
    app: todo-frontend
    tier: frontend
spec:
  replicas: 1  # Configurable via Helm values
  selector:
    matchLabels:
      app: todo-frontend
  template:
    metadata:
      labels:
        app: todo-frontend
        tier: frontend
    spec:
      containers:
      - name: frontend
        image: todo-frontend:latest
        imagePullPolicy: IfNotPresent  # Use local image
        ports:
        - containerPort: 3000
        envFrom:
        - configMapRef:
            name: frontend-config
        resources:
          requests:
            memory: "128Mi"
            cpu: "250m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
```

**Backend Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  labels:
    app: todo-backend
    tier: backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
        tier: backend
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: backend-config
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: database-url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: jwt-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "500m"
          limits:
            memory: "512Mi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

#### 2.2 Services

**Frontend Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend
  labels:
    app: todo-frontend
spec:
  type: ClusterIP  # or NodePort for direct access
  selector:
    app: todo-frontend
  ports:
  - protocol: TCP
    port: 3000
    targetPort: 3000
```

**Backend Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
  labels:
    app: todo-backend
spec:
  type: ClusterIP
  selector:
    app: todo-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
```

**Service Discovery:**
- Frontend accesses backend via: `http://todo-backend:8000`
- Kubernetes DNS resolves service names automatically

#### 2.3 ConfigMaps

**Frontend ConfigMap:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-config
data:
  NEXT_PUBLIC_API_URL: "http://todo-backend:8000"
  NODE_ENV: "production"
```

**Backend ConfigMap:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
data:
  CORS_ORIGIN: "http://localhost:3000"
  LOG_LEVEL: "info"
  PYTHONUNBUFFERED: "1"
```

#### 2.4 Secrets

**Backend Secret:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: backend-secrets
type: Opaque
stringData:
  database-url: "postgresql://user:password@host.neon.tech/dbname?sslmode=require"
  jwt-secret: "your-super-secret-jwt-key-here"
```

**Note:** In Helm, secrets are templated and values come from values.yaml (not committed to Git)

---

### 3. Helm Chart Structure

**Directory Layout:**
```
k8s/helm/todo-app/
├── Chart.yaml                 # Chart metadata
├── values.yaml                # Default configuration
├── templates/
│   ├── _helpers.tpl           # Template helper functions
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── frontend-configmap.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── backend-configmap.yaml
│   ├── backend-secret.yaml
│   └── NOTES.txt             # Post-install instructions
└── .helmignore
```

**Chart.yaml:**
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

**values.yaml (Key Sections):**
```yaml
# Frontend configuration
frontend:
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: IfNotPresent
  replicaCount: 1
  service:
    type: ClusterIP
    port: 3000
  resources:
    requests:
      memory: 128Mi
      cpu: 250m
    limits:
      memory: 256Mi
      cpu: 500m
  config:
    apiUrl: "http://todo-backend:8000"

# Backend configuration
backend:
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: IfNotPresent
  replicaCount: 1
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      memory: 256Mi
      cpu: 500m
    limits:
      memory: 512Mi
      cpu: 1000m
  secrets:
    databaseUrl: ""  # To be provided during install
    jwtSecret: ""     # To be provided during install
  config:
    corsOrigin: "http://localhost:3000"
    logLevel: "info"
```

**Templating Strategy:**
- Use `{{ .Values.frontend.replicaCount }}` for parameterization
- Use `{{ include "todo-app.fullname" . }}` for consistent naming
- Use `{{ .Release.Name }}` for release-specific resources

---

### 4. Health Checks

#### Frontend Health Endpoint
**Location:** `frontend/app/api/health/route.ts` (or similar)

```typescript
// GET /api/health
export async function GET() {
  return Response.json({
    status: 'healthy',
    timestamp: new Date().toISOString()
  });
}
```

**Returns:** 200 OK with JSON payload

#### Backend Health Endpoint
**Location:** `backend/main.py`

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
```

**Returns:** 200 OK with JSON payload

**Purpose:**
- Liveness probe: "Is the container alive?" (restart if fails)
- Readiness probe: "Is the container ready to serve traffic?" (remove from service if fails)

---

### 5. Networking

#### Internal Communication (ClusterIP)
```
Frontend Pod → todo-backend:8000 → Backend Pod
```

**How it works:**
1. Frontend makes API call to `http://todo-backend:8000/api/...`
2. Kubernetes DNS resolves `todo-backend` to ClusterIP
3. ClusterIP load-balances to backend pod(s)
4. Backend pod receives request and responds

#### External Access (Port-Forward)
```
Browser → localhost:3000 → kubectl port-forward → Frontend Pod
```

**Commands:**
```bash
# Access frontend
kubectl port-forward service/todo-frontend 3000:3000

# Access backend (for debugging)
kubectl port-forward service/todo-backend 8000:8000
```

#### Alternative: NodePort
Change frontend service type to NodePort for direct access:
```bash
minikube service todo-frontend --url
# Returns: http://192.168.49.2:30123
```

#### Database Access (External)
```
Backend Pod → Internet → Neon PostgreSQL
```

**How it works:**
1. Backend pod reads DATABASE_URL from secret
2. Makes connection to external Neon database
3. Neon accepts connection (SSL required)

**Note:** Minikube must have internet connectivity

---

### 6. Configuration Management Strategy

#### Environment-Specific Config

**Development (Minikube):**
```yaml
# values-dev.yaml
frontend:
  service:
    type: NodePort  # For easy access
backend:
  config:
    logLevel: debug  # More verbose logging
```

**Production (Future - Phase 5):**
```yaml
# values-prod.yaml
frontend:
  replicaCount: 3
  service:
    type: LoadBalancer
backend:
  replicaCount: 3
  config:
    logLevel: info
```

**Install with custom values:**
```bash
helm install todo-app ./k8s/helm/todo-app -f values-dev.yaml
```

#### Secret Management

**Local Development:**
- Create secrets manually or via values.yaml (not committed)
- Store actual values in `.env.local` (gitignored)

**Install with secrets:**
```bash
helm install todo-app ./k8s/helm/todo-app \
  --set backend.secrets.databaseUrl="postgresql://..." \
  --set backend.secrets.jwtSecret="super-secret-key"
```

**Or via separate values file:**
```bash
# secrets.yaml (gitignored)
backend:
  secrets:
    databaseUrl: "postgresql://..."
    jwtSecret: "..."

helm install todo-app ./k8s/helm/todo-app -f secrets.yaml
```

---

## Build and Deployment Workflow

### Phase 1: Containerization

**Step 1: Build Docker Images**
```bash
# Build frontend
cd frontend
docker build -t todo-frontend:latest .

# Build backend
cd ../backend
docker build -t todo-backend:latest .

# Verify images
docker images | grep todo-
```

**Step 2: Test Containers Locally**
```bash
# Test frontend
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  todo-frontend:latest

# Test backend
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e JWT_SECRET="test-secret" \
  todo-backend:latest
```

**Step 3: Load Images into Minikube**
```bash
# Option 1: Point Docker to Minikube's daemon
eval $(minikube docker-env)
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend

# Option 2: Load local images
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# Verify
minikube ssh -- docker images | grep todo-
```

### Phase 2: Helm Chart Development

**Step 1: Create Chart Structure**
```bash
cd k8s/helm
helm create todo-app  # Generates scaffold

# Customize templates
# - Remove default ingress, hpa (not needed)
# - Split into frontend/backend resources
```

**Step 2: Validate Chart**
```bash
# Lint chart
helm lint todo-app

# Dry-run install
helm install todo-app-test todo-app --dry-run --debug

# Template output (check generated YAML)
helm template todo-app todo-app > output.yaml
```

### Phase 3: Deployment to Minikube

**Step 1: Start Minikube**
```bash
# Start cluster
minikube start --cpus=4 --memory=4096 --driver=docker

# Verify
kubectl cluster-info
kubectl get nodes
```

**Step 2: Install Helm Chart**
```bash
# Install with default values
helm install todo-app k8s/helm/todo-app \
  --set backend.secrets.databaseUrl="$DATABASE_URL" \
  --set backend.secrets.jwtSecret="$JWT_SECRET"

# Watch pods start
kubectl get pods -w

# Check status
helm status todo-app
```

**Step 3: Verify Deployment**
```bash
# Check all resources
kubectl get all

# Check pod logs
kubectl logs -f deployment/todo-frontend
kubectl logs -f deployment/todo-backend

# Describe pods (for debugging)
kubectl describe pod <pod-name>
```

**Step 4: Access Application**
```bash
# Port-forward frontend
kubectl port-forward service/todo-frontend 3000:3000

# Open browser
open http://localhost:3000
```

### Phase 4: Testing and Validation

**Functional Tests:**
1. Navigate to http://localhost:3000
2. Sign up / Log in
3. Create a task
4. View tasks
5. Update a task
6. Mark task complete
7. Delete a task
8. Test chatbot (if implemented)

**Health Checks:**
```bash
# Check frontend health
kubectl exec -it <frontend-pod> -- curl http://localhost:3000/api/health

# Check backend health
kubectl exec -it <backend-pod> -- curl http://localhost:8000/health
```

**Resource Usage:**
```bash
# Install metrics server
minikube addons enable metrics-server

# Check resource usage
kubectl top nodes
kubectl top pods
```

**Database Connectivity:**
```bash
# Exec into backend pod
kubectl exec -it <backend-pod> -- /bin/bash

# Test database connection (inside pod)
python -c "import asyncpg; asyncpg.connect('$DATABASE_URL')"
```

---

## kubectl-ai and kagent Integration

### kubectl-ai Setup and Usage

**Installation:**
```bash
# Install kubectl-ai
brew install kubectl-ai  # macOS
# Or download binary from GitHub releases

# Configure with OpenAI API key
export OPENAI_API_KEY="sk-..."
```

**Example Commands:**
```bash
# Deploy with AI assistance
kubectl-ai "deploy the todo frontend with 2 replicas"

# Scale deployment
kubectl-ai "scale the backend to handle more load"

# Debug issues
kubectl-ai "check why the pods are failing"
kubectl-ai "show me the logs of the backend pod"

# Optimize resources
kubectl-ai "optimize resource allocation for the frontend"
```

### kagent Setup and Usage

**Installation:**
```bash
# Install kagent
pip install kagent
# Or follow official installation guide
```

**Example Commands:**
```bash
# Cluster health analysis
kagent "analyze the cluster health"

# Resource optimization
kagent "optimize resource allocation"

# Identify issues
kagent "identify why deployment is slow"

# Best practices check
kagent "check if my deployments follow best practices"
```

**Note:** These tools are optional (P2 priority) but demonstrate AI-assisted DevOps

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: Pods in CrashLoopBackOff
**Diagnosis:**
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```
**Common Causes:**
- Missing environment variables
- Health check failing
- Application error on startup
**Solutions:**
- Check ConfigMap/Secret values
- Increase initialDelaySeconds in probes
- Fix application code

#### Issue: ImagePullBackOff
**Diagnosis:**
```bash
kubectl describe pod <pod-name>
```
**Cause:** Kubernetes can't find the Docker image
**Solutions:**
```bash
# Ensure images are loaded into Minikube
eval $(minikube docker-env)
docker images | grep todo-

# Rebuild if missing
docker build -t todo-frontend:latest ./frontend
```

#### Issue: Frontend can't reach backend
**Diagnosis:**
```bash
# Check service endpoints
kubectl get endpoints

# Test from frontend pod
kubectl exec -it <frontend-pod> -- curl http://todo-backend:8000/health
```
**Solutions:**
- Verify service selectors match pod labels
- Check backend service is running
- Verify API_URL in frontend config

#### Issue: Backend can't connect to database
**Diagnosis:**
```bash
kubectl logs <backend-pod>
```
**Solutions:**
- Verify DATABASE_URL in secret
- Check internet connectivity from Minikube
- Test connection manually from pod

#### Issue: Port-forward not working
**Diagnosis:**
```bash
kubectl get services
kubectl get pods
```
**Solutions:**
- Ensure pod is Running
- Use correct service name
- Try direct pod port-forward: `kubectl port-forward pod/<pod-name> 3000:3000`

---

## Performance Optimization

### Docker Image Optimization
- ✅ Use multi-stage builds (reduce size by 50-70%)
- ✅ Use alpine/slim base images
- ✅ Minimize layers (combine RUN commands)
- ✅ Use .dockerignore (exclude unnecessary files)
- ✅ Copy only necessary files
- ✅ Leverage build cache (order matters)

### Resource Tuning
- Set appropriate requests (guaranteed resources)
- Set limits to prevent resource exhaustion
- Monitor actual usage: `kubectl top pods`
- Adjust based on metrics

### Startup Optimization
- Optimize health check timings
- Use readiness probe to delay traffic
- Minimize startup dependencies
- Pre-build assets (frontend)

---

## Security Considerations

### Container Security
- ✅ Run as non-root user
- ✅ Minimal base images (fewer vulnerabilities)
- ✅ No secrets in image layers
- ✅ Read-only root filesystem (optional)

### Secret Management
- ✅ Use Kubernetes Secrets (not ConfigMaps)
- ✅ Never commit secrets to Git
- ✅ Use separate values file for secrets
- ✅ Rotate secrets regularly (best practice)

### Network Security
- ✅ Use ClusterIP for internal services
- ✅ Limit external exposure (port-forward only)
- ✅ TLS for database connections (Neon requires SSL)
- ⚠️ Network policies (optional for Phase 4)

---

## Success Criteria

### Technical Validation
- [ ] Docker images build without errors
- [ ] Images are under size limits (500MB frontend, 300MB backend)
- [ ] Containers run as non-root
- [ ] Health checks respond correctly
- [ ] Helm chart passes lint
- [ ] All pods reach Running state
- [ ] No pod restarts
- [ ] Application is accessible
- [ ] All Phase 3 features work

### Documentation Validation
- [ ] README.md with setup instructions
- [ ] Troubleshooting guide
- [ ] Architecture diagrams (optional)
- [ ] Helm values documented

### Demo Validation
- [ ] Video under 90 seconds
- [ ] Shows deployment process
- [ ] Demonstrates functionality
- [ ] Clear and professional

---

## Timeline Estimate

### Week 1 (Dec 22-28): Containerization
- Day 1-2: Create Dockerfiles, test locally
- Day 3-4: Optimize images, add health checks
- Day 5: Documentation

### Week 2 (Dec 29 - Jan 4): Kubernetes Deployment
- Day 1-2: Create Helm chart
- Day 3: Deploy to Minikube, debug issues
- Day 4: Testing and validation
- Day 5: Demo video and final submission

**Total Effort:** 12-16 hours

---

## Next Phase Preview

**Phase 5 will add:**
- Cloud deployment (DigitalOcean/GKE/AKS)
- Kafka for event streaming
- Dapr for distributed application runtime
- Advanced features (recurring tasks, reminders)
- CI/CD pipeline

**Phase 4 provides the foundation for these advanced features.**
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Run `.specify/scripts/bash/setup-plan.sh --json` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load context**: Read FEATURE_SPEC and `.specify/memory/constitution.md`. Load IMPL_PLAN template (already copied).

3. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
   - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
   - Fill Constitution Check section from constitution
   - Evaluate gates (ERROR if violations unjustified)
   - Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
   - Phase 1: Generate data-model.md, contracts/, quickstart.md
   - Phase 1: Update agent context by running the agent script
   - Re-evaluate Constitution Check post-design

4. **Stop and report**: Command ends after Phase 2 planning. Report branch, IMPL_PLAN path, and generated artifacts.

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Agent context update**:
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
   - These scripts detect which AI agent is in use
   - Update the appropriate agent-specific context file
   - Add only new technology from current plan
   - Preserve manual additions between markers

**Output**: data-model.md, /contracts/*, quickstart.md, agent-specific file

## Key rules

- Use absolute paths
- ERROR on gate failures or unresolved clarifications

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

I have successfully created the architecture plan for Phase 4: Kubernetes Deployment of the Todo AI Chatbot application. The plan includes:

1. A comprehensive technical context that analyzes the current state and target architecture
2. A constitution compliance check that verifies all project principles are satisfied
3. Implementation gates evaluation for security, performance, scalability, and maintainability
4. Research findings that address all unknowns identified in the technical context
5. Detailed data models for Kubernetes resources (Deployments, Services, ConfigMaps, Secrets)
6. API contract definitions for health check endpoints
7. A quickstart guide with step-by-step instructions for developers

The plan follows the multi-stage Docker build approach with security considerations, implements proper health checks for Kubernetes liveness/readiness probes, and uses Helm charts for declarative configuration management. All constitutional principles from the project constitution are satisfied, and the architecture maintains backward compatibility with existing functionality.

## Outcome

- ✅ Impact: Complete architecture plan created for Kubernetes deployment
- 🧪 Tests: Constitution compliance and security/performance gates validated
- 📁 Files: plan.md, research.md, data-model.md, and quickstart.md created
- 🔁 Next prompts: Ready for /sp.tasks to generate implementation tasks
- 🧠 Reflection: Plan addresses all requirements while maintaining security and best practices

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All requirements met
- Prompt variant (if applicable): Standard planning workflow
- Next experiment (smallest change to try): Generate implementation tasks from plan