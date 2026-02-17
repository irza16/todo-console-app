---
id: 001
title: Phase 4 Specification
stage: spec
date: 2026-02-06
surface: agent
model: google/gemini-2.0-flash-exp:free
feature: kubernetes-deployment
branch: 005-kubernetes-deployment
user: irza
command: sp.specify
labels: [kubernetes, deployment, containerization, docker, helm]
links:
  spec: specs/005-kubernetes-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-kubernetes-deployment/spec.md
  - specs/005-kubernetes-deployment/checklists/requirements.md
tests:
  - specification completeness check
  - requirements validation
---

## Prompt

```text
# Phase 4 Specification: Local Kubernetes Deployment

## Overview
Deploy the existing Todo AI Chatbot (from Phase 3) to a local Kubernetes cluster using Minikube, Docker containers, and Helm charts. This phase focuses on containerization and orchestration without adding new features.

## User Stories

### US-4.1: Developer Containerizes Frontend
**As a** developer
**I want to** containerize the Next.js frontend application
**So that** it can run in Kubernetes pods

**Acceptance Criteria:**
- Dockerfile exists in `/frontend/Dockerfile`
- Docker image builds successfully without errors
- Image size is under 500MB
- Container runs as non-root user
- Container serves the application on port 3000
- Health check endpoint responds at `/api/health`
- Environment variables control API_URL configuration
- `.dockerignore` excludes unnecessary files (node_modules, .git, etc.)

**Priority:** P0 (Critical)

---

### US-4.2: Developer Containerizes Backend
**As a** developer
**I want to** containerize the FastAPI backend application
**So that** it can run in Kubernetes pods

**Acceptance Criteria:**
- Dockerfile exists in `/backend/Dockerfile`
- Docker image builds successfully without errors
- Image size is under 300MB
- Container runs as non-root user
- Container serves the API on port 8000
- Health check endpoint responds at `/health`
- Environment variables control DATABASE_URL and other config
- `.dockerignore` excludes unnecessary files (\_\_pycache\_\_, .venv, etc.)
- All Python dependencies are properly installed

**Priority:** P0 (Critical)

---

### US-4.3: Developer Tests Containers Locally
**As a** developer
**I want to** test Docker containers before Kubernetes deployment
**So that** I can catch issues early

**Acceptance Criteria:**
- Frontend container starts successfully with `docker run`
- Backend container starts successfully with `docker run`
- Frontend serves pages and loads correctly
- Backend responds to API requests
- Backend can connect to external Neon database
- Containers can be stopped gracefully
- docker-compose.yml exists for local multi-container testing (optional)

**Priority:** P1 (High)

---

### US-4.4: Developer Creates Helm Chart Structure
**As a** developer
**I want to** create Helm charts for deployment
**So that** I can manage Kubernetes resources declaratively

**Acceptance Criteria:**
- Helm chart directory exists at `/k8s/helm/todo-app/`
- Chart.yaml contains proper metadata (name, version, description)
- values.yaml contains all configurable parameters
- Templates directory contains resource definitions
- Chart passes `helm lint` validation
- Default values are sensible for local development

**Priority:** P0 (Critical)

---

### US-4.5: Developer Defines Frontend Kubernetes Resources
**As a** developer
**I want to** define Kubernetes resources for the frontend
**So that** it can be deployed and accessed in the cluster

**Acceptance Criteria:**
- Deployment template exists for frontend
- Deployment specifies replica count (default: 1)
- Deployment includes resource requests and limits
- Deployment includes readiness and liveness probes
- Service template exists for frontend (ClusterIP type)
- Service exposes port 3000
- ConfigMap template exists for frontend configuration
- All resources have appropriate labels

**Priority:** P0 (Critical)

---

### US-4.6: Developer Defines Backend Kubernetes Resources
**As a** developer
**I want to** define Kubernetes resources for the backend
**So that** it can be deployed and accessed in the cluster

**Acceptance Criteria:**
- Deployment template exists for backend
- Deployment specifies replica count (default: 1)
- Deployment includes resource requests and limits
- Deployment includes readiness and liveness probes
- Service template exists for backend (ClusterIP type)
- Service exposes port 8000
- Secret template exists for sensitive config (DATABASE_URL, JWT_SECRET)
- ConfigMap template exists for non-sensitive config
- All resources have appropriate labels

**Priority:** P0 (Critical)

---

### US-4.7: Developer Deploys to Minikube
**As a** developer
**I want to** deploy the application to Minikube
**So that** I can run it in a local Kubernetes environment

**Acceptance Criteria:**
- Minikube cluster starts successfully
- Docker images are accessible to Minikube
- `helm install` completes without errors
- All pods reach Running state within 60 seconds
- `kubectl get pods` shows 0 restarts
- Frontend pod is accessible via service
- Backend pod is accessible via service
- Backend pod can connect to Neon database

**Priority:** P0 (Critical)

---

### US-4.8: Developer Accesses Application Locally
**As a** developer
**I want to** access the deployed application from my browser
**So that** I can verify it works correctly

**Acceptance Criteria:**
- Frontend is accessible via `kubectl port-forward` or NodePort
- Login page loads successfully
- User can sign up and log in
- Todo list displays correctly
- User can create, update, and delete tasks
- Chatbot interface works (if implemented in Phase 3)
- All functionality from Phase 3 works identically

**Priority:** P0 (Critical)

---

### US-4.9: Developer Uses kubectl-ai for Operations
**As a** developer
**I want to** use AI-assisted tools for Kubernetes operations
**So that** I can manage the cluster more efficiently

**Acceptance Criteria:**
- kubectl-ai is installed and configured
- Can use kubectl-ai to check pod status
- Can use kubectl-ai to scale deployments
- Can use kubectl-ai to debug failing pods
- Can use kubectl-ai to view logs
- Commands execute successfully and provide useful output

**Priority:** P2 (Medium)

---

### US-4.10: Developer Uses kagent for Cluster Management
**As a** developer
**I want to** use kagent for advanced cluster operations
**So that** I can analyze and optimize the deployment

**Acceptance Criteria:**
- kagent is installed and configured
- Can use kagent to analyze cluster health
- Can use kagent to optimize resource allocation
- Can use kagent to identify issues
- kagent provides actionable insights

**Priority:** P2 (Medium)

---

### US-4.11: Developer Documents Deployment Process
**As a** developer
**I want to** create comprehensive deployment documentation
**So that** others (and judges) can reproduce the deployment

**Acceptance Criteria:**
- README.md exists in `/k8s/` directory
- README includes prerequisites (Minikube, Docker, Helm, kubectl)
- README includes step-by-step deployment instructions
- README includes commands to verify deployment
- README includes commands to access the application
- README includes troubleshooting section
- README includes cleanup instructions
- All commands are copy-pasteable and work correctly

**Priority:** P1 (High)

---

### US-4.12: Developer Creates Demo Video
**As a** developer
**I want to** create a demo video showing the deployment
**So that** I can submit it with the hackathon

**Acceptance Criteria:**
- Video is under 90 seconds
- Video shows `helm install` command execution
- Video shows pods starting and reaching Running state
- Video shows accessing the application via browser
- Video demonstrates at least one task operation
- Video quality is clear and professional
- Video is uploaded and link is available

**Priority:** P1 (High)

---

## Technical Requirements

### Docker Images

#### Frontend Image
- **Base Image:** node:20-alpine or node:20-slim
- **Multi-Stage Build:** Yes (build stage + runtime stage)
- **Final Size:** < 500MB
- **User:** Non-root (node user)
- **Port:** 3000
- **Health Check:** GET /api/health returns 200
- **Environment Variables:**
  - NEXT_PUBLIC_API_URL (backend service URL)

#### Backend Image
- **Base Image:** python:3.13-slim or python:3.13-alpine
- **Multi-Stage Build:** Yes (build stage + runtime stage)
- **Final Size:** < 300MB
- **User:** Non-root (created user)
- **Port:** 8000
- **Health Check:** GET /health returns 200
- **Environment Variables:**
  - DATABASE_URL (Neon PostgreSQL connection string)
  - JWT_SECRET (signing key)
  - CORS_ORIGIN (frontend URL)

### Kubernetes Resources

#### Frontend Deployment
- **Replicas:** 1 (configurable via Helm values)
- **Image Pull Policy:** IfNotPresent (for local images)
- **Resource Requests:** 128Mi RAM, 0.25 CPU
- **Resource Limits:** 256Mi RAM, 0.5 CPU
- **Readiness Probe:** HTTP GET /api/health, initialDelaySeconds: 10
- **Liveness Probe:** HTTP GET /api/health, initialDelaySeconds: 15
- **Environment:** From ConfigMap

#### Backend Deployment
- **Replicas:** 1 (configurable via Helm values)
- **Image Pull Policy:** IfNotPresent (for local images)
- **Resource Requests:** 256Mi RAM, 0.5 CPU
- **Resource Limits:** 512Mi RAM, 1.0 CPU
- **Readiness Probe:** HTTP GET /health, initialDelaySeconds: 10
- **Liveness Probe:** HTTP GET /health, initialDelaySeconds: 15
- **Environment:** From ConfigMap and Secret

#### Services
- **Frontend Service:**
  - Type: ClusterIP (or NodePort for local access)
  - Port: 3000
  - TargetPort: 3000
  - Selector: app=todo-frontend

- **Backend Service:**
  - Type: ClusterIP
  - Port: 8000
  - TargetPort: 8000
  - Selector: app=todo-backend

### Helm Chart Structure

```
k8s/helm/todo-app/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration values
├── templates/
│   ├── _helpers.tpl        # Template helpers
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── frontend-configmap.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── backend-configmap.yaml
│   ├── backend-secret.yaml
│   └── NOTES.txt          # Post-install instructions
└── .helmignore
```

### Configuration Management

#### ConfigMaps (Non-Sensitive)
- Frontend:
  - NEXT_PUBLIC_API_URL: http://todo-backend:8000

- Backend:
  - CORS_ORIGIN: http://localhost:3000
  - LOG_LEVEL: info

#### Secrets (Sensitive)
- Backend:
  - DATABASE_URL: (Neon PostgreSQL connection string)
  - JWT_SECRET: (random secure string)
  - BETTER_AUTH_SECRET: (if applicable)

## Non-Functional Requirements

### Performance
- Pod startup time: < 30 seconds
- Application response time: < 500ms
- Container restart time: < 15 seconds

### Reliability
- Pods restart automatically on crash
- Zero-downtime for rolling updates (future phase)
- Graceful shutdown on SIGTERM

### Security
- No secrets in Docker images
- Containers run as non-root
- Minimal base images (alpine/slim)
- Network policies (optional enhancement)

### Maintainability
- Clear documentation for all components
- Helm values for easy configuration
- Meaningful labels and annotations
- Logical resource organization

## Testing Strategy

### Docker Image Testing
1. Build frontend image: `docker build -t todo-frontend:latest ./frontend`
2. Run frontend container: `docker run -p 3000:3000 todo-frontend:latest`
3. Verify frontend loads in browser: http://localhost:3000
4. Build backend image: `docker build -t todo-backend:latest ./backend`
5. Run backend container with env vars: `docker run -p 8000:8000 -e DATABASE_URL=... todo-backend:latest`
6. Verify backend health: curl http://localhost:8000/health

### Helm Chart Testing
1. Lint chart: `helm lint k8s/helm/todo-app`
2. Dry-run install: `helm install todo-app k8s/helm/todo-app --dry-run --debug`
3. Template output: `helm template todo-app k8s/helm/todo-app`
4. Verify templates are valid YAML

### Kubernetes Deployment Testing
1. Install chart: `helm install todo-app k8s/helm/todo-app`
2. Check pod status: `kubectl get pods -w`
3. Check pod logs: `kubectl logs -f <pod-name>`
4. Port-forward frontend: `kubectl port-forward service/todo-frontend 3000:3000`
5. Port-forward backend: `kubectl port-forward service/todo-backend 8000:8000`
6. Test application functionality
7. Check resource usage: `kubectl top pods`

### Integration Testing
1. Verify frontend → backend communication
2. Verify backend → database communication
3. Test complete user flow (signup → login → create task → view tasks)
4. Verify chatbot functionality (if implemented)

## Out of Scope

### Explicitly NOT Included
- ❌ New application features (use Phase 3 as-is)
- ❌ ChatKit integration (skipped due to time constraints)
- ❌ Cloud deployment (that's Phase 5)
- ❌ Kafka/Dapr (that's Phase 5)
- ❌ CI/CD pipelines (optional for Phase 5)
- ❌ Ingress controllers (use port-forward or NodePort)
- ❌ Persistent volumes (database is external)
- ❌ StatefulSets (not needed for stateless app)
- ❌ Horizontal Pod Autoscaling (nice-to-have)
- ❌ Advanced networking (service mesh, etc.)

## Success Metrics

### Quantitative
- ✅ 2 Docker images built successfully
- ✅ 1 Helm chart created
- ✅ 2 services deployed (frontend + backend)
- ✅ 2 deployments running (frontend + backend)
- ✅ 100% of pods in Running state
- ✅ 0 pod restarts
- ✅ 1 demo video created (< 90 seconds)

### Qualitative
- ✅ Application works identically to Phase 3
- ✅ Deployment process is reproducible
- ✅ Documentation is clear and complete
- ✅ Docker images follow best practices
- ✅ Kubernetes resources are properly configured
- ✅ Demonstrates understanding of container orchestration

## Dependencies

### External Dependencies
- Neon PostgreSQL database (from Phase 2/3)
- GitHub repository (for version control)
- Vercel deployment (Phase 3, for comparison)

### Tool Dependencies
- Docker Desktop 4.53+ (or Docker Engine + Minikube with Docker driver)
- Minikube (latest stable version)
- kubectl (matching Minikube Kubernetes version)
- Helm 3.x
- kubectl-ai (optional but recommended)
- kagent (optional but recommended)

### Knowledge Dependencies
- Docker fundamentals (images, containers, Dockerfiles)
- Kubernetes basics (pods, services, deployments)
- Helm basics (charts, templates, values)
- YAML syntax
- Environment variable management

## Risks and Mitigations

### Risk: Docker Image Too Large
**Mitigation:** Use multi-stage builds, alpine base images, minimize dependencies

### Risk: Pods Failing to Start
**Mitigation:** Test containers locally first, check logs, verify health checks

### Risk: Database Connection Issues
**Mitigation:** Verify network connectivity, check credentials, test from within pod

### Risk: Time Constraint (Due Jan 4)
**Mitigation:** Focus on P0/P1 user stories first, skip optional features (kubectl-ai, kagent)

### Risk: Minikube Resource Limitations
**Mitigation:** Set conservative resource requests/limits, ensure enough RAM allocated to Minikube

## Acceptance Criteria Summary

The Phase 4 submission is considered complete when:

1. ✅ Frontend Dockerfile exists and builds successfully
2. ✅ Backend Dockerfile exists and builds successfully
3. ✅ Helm chart exists with all required templates
4. ✅ Application deploys to Minikube without errors
5. ✅ All pods are Running with 0 restarts
6. ✅ Application is accessible via port-forward
7. ✅ All Phase 3 functionality works correctly
8. ✅ Documentation is complete and accurate
9. ✅ Demo video is recorded and submitted
10. ✅ GitHub repository is updated with all files

## References
- Hackathon Phase 4 requirements
- Phase 3 application (baseline)
- Docker documentation: https://docs.docker.com
- Kubernetes documentation: https://kubernetes.io/docs
- Helm documentation: https://helm.sh/docs
- Minikube documentation: https://minikube.sigs.k8s.io
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/sp.specify` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `# Phase 4 Specification: Local Kubernetes Deployment

## Overview
Deploy the existing Todo AI Chatbot (from Phase 3) to a local Kubernetes cluster using Minikube, Docker containers, and Helm charts. This phase focuses on containerization and orchestration without adding new features.

## User Stories

### US-4.1: Developer Containerizes Frontend
**As a** developer
**I want to** containerize the Next.js frontend application
**So that** it can run in Kubernetes pods

**Acceptance Criteria:**
- Dockerfile exists in `/frontend/Dockerfile`
- Docker image builds successfully without errors
- Image size is under 500MB
- Container runs as non-root user
- Container serves the application on port 3000
- Health check endpoint responds at `/api/health`
- Environment variables control API_URL configuration
- `.dockerignore` excludes unnecessary files (node_modules, .git, etc.)

**Priority:** P0 (Critical)

---

### US-4.2: Developer Containerizes Backend
**As a** developer
**I want to** containerize the FastAPI backend application
**So that** it can run in Kubernetes pods

**Acceptance Criteria:**
- Dockerfile exists in `/backend/Dockerfile`
- Docker image builds successfully without errors
- Image size is under 300MB
- Container runs as non-root user
- Container serves the API on port 8000
- Health check endpoint responds at `/health`
- Environment variables control DATABASE_URL and other config
- `.dockerignore` excludes unnecessary files (\_\_pycache\_\_, .venv, etc.)
- All Python dependencies are properly installed

**Priority:** P0 (Critical)

---

### US-4.3: Developer Tests Containers Locally
**As a** developer
**I want to** test Docker containers before Kubernetes deployment
**So that** I can catch issues early

**Acceptance Criteria:**
- Frontend container starts successfully with `docker run`
- Backend container starts successfully with `docker run`
- Frontend serves pages and loads correctly
- Backend responds to API requests
- Backend can connect to external Neon database
- Containers can be stopped gracefully
- docker-compose.yml exists for local multi-container testing (optional)

**Priority:** P1 (High)

---

### US-4.4: Developer Creates Helm Chart Structure
**As a** developer
**I want to** create Helm charts for deployment
**So that** I can manage Kubernetes resources declaratively

**Acceptance Criteria:**
- Helm chart directory exists at `/k8s/helm/todo-app/`
- Chart.yaml contains proper metadata (name, version, description)
- values.yaml contains all configurable parameters
- Templates directory contains resource definitions
- Chart passes `helm lint` validation
- Default values are sensible for local development

**Priority:** P0 (Critical)

---

### US-4.5: Developer Defines Frontend Kubernetes Resources
**As a** developer
**I want to** define Kubernetes resources for the frontend
**So that** it can be deployed and accessed in the cluster

**Acceptance Criteria:**
- Deployment template exists for frontend
- Deployment specifies replica count (default: 1)
- Deployment includes resource requests and limits
- Deployment includes readiness and liveness probes
- Service template exists for frontend (ClusterIP type)
- Service exposes port 3000
- ConfigMap template exists for frontend configuration
- All resources have appropriate labels

**Priority:** P0 (Critical)

---

### US-4.6: Developer Defines Backend Kubernetes Resources
**As a** developer
**I want to** define Kubernetes resources for the backend
**So that** it can be deployed and accessed in the cluster

**Acceptance Criteria:**
- Deployment template exists for backend
- Deployment specifies replica count (default: 1)
- Deployment includes resource requests and limits
- Deployment includes readiness and liveness probes
- Service template exists for backend (ClusterIP type)
- Service exposes port 8000
- Secret template exists for sensitive config (DATABASE_URL, JWT_SECRET)
- ConfigMap template exists for non-sensitive config
- All resources have appropriate labels

**Priority:** P0 (Critical)

---

### US-4.7: Developer Deploys to Minikube
**As a** developer
**I want to** deploy the application to Minikube
**So that** I can run it in a local Kubernetes environment

**Acceptance Criteria:**
- Minikube cluster starts successfully
- Docker images are accessible to Minikube
- `helm install` completes without errors
- All pods reach Running state within 60 seconds
- `kubectl get pods` shows 0 restarts
- Frontend pod is accessible via service
- Backend pod is accessible via service
- Backend pod can connect to Neon database

**Priority:** P0 (Critical)

---

### US-4.8: Developer Accesses Application Locally
**As a** developer
**I want to** access the deployed application from my browser
**So that** I can verify it works correctly

**Acceptance Criteria:**
- Frontend is accessible via `kubectl port-forward` or NodePort
- Login page loads successfully
- User can sign up and log in
- Todo list displays correctly
- User can create, update, and delete tasks
- Chatbot interface works (if implemented in Phase 3)
- All functionality from Phase 3 works identically

**Priority:** P0 (Critical)

---

### US-4.9: Developer Uses kubectl-ai for Operations
**As a** developer
**I want to** use AI-assisted tools for Kubernetes operations
**So that** I can manage the cluster more efficiently

**Acceptance Criteria:**
- kubectl-ai is installed and configured
- Can use kubectl-ai to check pod status
- Can use kubectl-ai to scale deployments
- Can use kubectl-ai to debug failing pods
- Can use kubectl-ai to view logs
- Commands execute successfully and provide useful output

**Priority:** P2 (Medium)

---

### US-4.10: Developer Uses kagent for Cluster Management
**As a** developer
**I want to** use kagent for advanced cluster operations
**So that** I can analyze and optimize the deployment

**Acceptance Criteria:**
- kagent is installed and configured
- Can use kagent to analyze cluster health
- Can use kagent to optimize resource allocation
- Can use kagent to identify issues
- kagent provides actionable insights

**Priority:** P2 (Medium)

---

### US-4.11: Developer Documents Deployment Process
**As a** developer
**I want to** create comprehensive deployment documentation
**So that** others (and judges) can reproduce the deployment

**Acceptance Criteria:**
- README.md exists in `/k8s/` directory
- README includes prerequisites (Minikube, Docker, Helm, kubectl)
- README includes step-by-step deployment instructions
- README includes commands to verify deployment
- README includes commands to access the application
- README includes troubleshooting section
- README includes cleanup instructions
- All commands are copy-pasteable and work correctly

**Priority:** P1 (High)

---

### US-4.12: Developer Creates Demo Video
**As a** developer
**I want to** create a demo video showing the deployment
**So that** I can submit it with the hackathon

**Acceptance Criteria:**
- Video is under 90 seconds
- Video shows `helm install` command execution
- Video shows pods starting and reaching Running state
- Video shows accessing the application via browser
- Video demonstrates at least one task operation
- Video quality is clear and professional
- Video is uploaded and link is available

**Priority:** P1 (High)

---

## Technical Requirements

### Docker Images

#### Frontend Image
- **Base Image:** node:20-alpine or node:20-slim
- **Multi-Stage Build:** Yes (build stage + runtime stage)
- **Final Size:** < 500MB
- **User:** Non-root (node user)
- **Port:** 3000
- **Health Check:** GET /api/health returns 200
- **Environment Variables:**
  - NEXT_PUBLIC_API_URL (backend service URL)

#### Backend Image
- **Base Image:** python:3.13-slim or python:3.13-alpine
- **Multi-Stage Build:** Yes (build stage + runtime stage)
- **Final Size:** < 300MB
- **User:** Non-root (created user)
- **Port:** 8000
- **Health Check:** GET /health returns 200
- **Environment Variables:**
  - DATABASE_URL (Neon PostgreSQL connection string)
  - JWT_SECRET (signing key)
  - CORS_ORIGIN (frontend URL)

### Kubernetes Resources

#### Frontend Deployment
- **Replicas:** 1 (configurable via Helm values)
- **Image Pull Policy:** IfNotPresent (for local images)
- **Resource Requests:** 128Mi RAM, 0.25 CPU
- **Resource Limits:** 256Mi RAM, 0.5 CPU
- **Readiness Probe:** HTTP GET /api/health, initialDelaySeconds: 10
- **Liveness Probe:** HTTP GET /api/health, initialDelaySeconds: 15
- **Environment:** From ConfigMap

#### Backend Deployment
- **Replicas:** 1 (configurable via Helm values)
- **Image Pull Policy:** IfNotPresent (for local images)
- **Resource Requests:** 256Mi RAM, 0.5 CPU
- **Resource Limits:** 512Mi RAM, 1.0 CPU
- **Readiness Probe:** HTTP GET /health, initialDelaySeconds: 10
- **Liveness Probe:** HTTP GET /health, initialDelaySeconds: 15
- **Environment:** From ConfigMap and Secret

#### Services
- **Frontend Service:**
  - Type: ClusterIP (or NodePort for local access)
  - Port: 3000
  - TargetPort: 3000
  - Selector: app=todo-frontend

- **Backend Service:**
  - Type: ClusterIP
  - Port: 8000
  - TargetPort: 8000
  - Selector: app=todo-backend

### Helm Chart Structure

```
k8s/helm/todo-app/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration values
├── templates/
│   ├── _helpers.tpl        # Template helpers
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── frontend-configmap.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── backend-configmap.yaml
│   ├── backend-secret.yaml
│   └── NOTES.txt          # Post-install instructions
└── .helmignore
```

### Configuration Management

#### ConfigMaps (Non-Sensitive)
- Frontend:
  - NEXT_PUBLIC_API_URL: http://todo-backend:8000

- Backend:
  - CORS_ORIGIN: http://localhost:3000
  - LOG_LEVEL: info

#### Secrets (Sensitive)
- Backend:
  - DATABASE_URL: (Neon PostgreSQL connection string)
  - JWT_SECRET: (random secure string)
  - BETTER_AUTH_SECRET: (if applicable)

## Non-Functional Requirements

### Performance
- Pod startup time: < 30 seconds
- Application response time: < 500ms
- Container restart time: < 15 seconds

### Reliability
- Pods restart automatically on crash
- Zero-downtime for rolling updates (future phase)
- Graceful shutdown on SIGTERM

### Security
- No secrets in Docker images
- Containers run as non-root
- Minimal base images (alpine/slim)
- Network policies (optional enhancement)

### Maintainability
- Clear documentation for all components
- Helm values for easy configuration
- Meaningful labels and annotations
- Logical resource organization

## Testing Strategy

### Docker Image Testing
1. Build frontend image: `docker build -t todo-frontend:latest ./frontend`
2. Run frontend container: `docker run -p 3000:3000 todo-frontend:latest`
3. Verify frontend loads in browser: http://localhost:3000
4. Build backend image: `docker build -t todo-backend:latest ./backend`
5. Run backend container with env vars: `docker run -p 8000:8000 -e DATABASE_URL=... todo-backend:latest`
6. Verify backend health: curl http://localhost:8000/health

### Helm Chart Testing
1. Lint chart: `helm lint k8s/helm/todo-app`
2. Dry-run install: `helm install todo-app k8s/helm/todo-app --dry-run --debug`
3. Template output: `helm template todo-app k8s/helm/todo-app`
4. Verify templates are valid YAML

### Kubernetes Deployment Testing
1. Install chart: `helm install todo-app k8s/helm/todo-app`
2. Check pod status: `kubectl get pods -w`
3. Check pod logs: `kubectl logs -f <pod-name>`
4. Port-forward frontend: `kubectl port-forward service/todo-frontend 3000:3000`
5. Port-forward backend: `kubectl port-forward service/todo-backend 8000:8000`
6. Test application functionality
7. Check resource usage: `kubectl top pods`

### Integration Testing
1. Verify frontend → backend communication
2. Verify backend → database communication
3. Test complete user flow (signup → login → create task → view tasks)
4. Verify chatbot functionality (if implemented)

## Out of Scope

### Explicitly NOT INCLUDED
- ❌ New application features (use Phase 3 as-is)
- ❌ ChatKit integration (skipped due to time constraints)
- ❌ Cloud deployment (that's Phase 5)
- ❌ Kafka/Dapr (that's Phase 5)
- ❌ CI/CD pipelines (optional for Phase 5)
- ❌ Ingress controllers (use port-forward or NodePort)
- ❌ Persistent volumes (database is external)
- ❌ StatefulSets (not needed for stateless app)
- ❌ Horizontal Pod Autoscaling (nice-to-have)
- ❌ Advanced networking (service mesh, etc.)

## Success Metrics

### Quantitative
- ✅ 2 Docker images built successfully
- ✅ 1 Helm chart created
- ✅ 2 services deployed (frontend + backend)
- ✅ 2 deployments running (frontend + backend)
- ✅ 100% of pods in Running state
- ✅ 0 pod restarts
- ✅ 1 demo video created (< 90 seconds)

### Qualitative
- ✅ Application works identically to Phase 3
- ✅ Deployment process is reproducible
- ✅ Documentation is clear and complete
- ✅ Docker images follow best practices
- ✅ Kubernetes resources are properly configured
- ✅ Demonstrates understanding of container orchestration

## Dependencies

### External Dependencies
- Neon PostgreSQL database (from Phase 2/3)
- GitHub repository (for version control)
- Vercel deployment (Phase 3, for comparison)

### Tool Dependencies
- Docker Desktop 4.53+ (or Docker Engine + Minikube with Docker driver)
- Minikube (latest stable version)
- kubectl (matching Minikube Kubernetes version)
- Helm 3.x
- kubectl-ai (optional but recommended)
- kagent (optional but recommended)

### Knowledge Dependencies
- Docker fundamentals (images, containers, Dockerfiles)
- Kubernetes basics (pods, services, deployments)
- Helm basics (charts, templates, values)
- YAML syntax
- Environment variable management

## Risks and Mitigations

### Risk: Docker Image Too Large
**Mitigation:** Use multi-stage builds, alpine base images, minimize dependencies

### Risk: Pods Failing to Start
**Mitigation:** Test containers locally first, check logs, verify health checks

### Risk: Database Connection Issues
**Mitigation:** Verify network connectivity, check credentials, test from within pod

### Risk: Time Constraint (Due Jan 4)
**Mitigation:** Focus on P0/P1 user stories first, skip optional features (kubectl-ai, kagent)

### Risk: Minikube Resource Limitations
**Mitigation:** Set conservative resource requests/limits, ensure enough RAM allocated to Minikube

## Acceptance Criteria Summary

The Phase 4 submission is considered complete when:

1. ✅ Frontend Dockerfile exists and builds successfully
2. ✅ Backend Dockerfile exists and builds successfully
3. ✅ Helm chart exists with all required templates
4. ✅ Application deploys to Minikube without errors
5. ✅ All pods are Running with 0 restarts
6. ✅ Application is accessible via port-forward
7. ✅ All Phase 3 functionality works correctly
8. ✅ Documentation is complete and accurate
9. ✅ Demo video is recorded and submitted
10. ✅ GitHub repository is updated with all files

## References
- Hackathon Phase 4 requirements
- Phase 3 application (baseline)
- Docker documentation: https://docs.docker.com
- Kubernetes documentation: https://kubernetes.io/docs
- Helm documentation: https://helm.sh/docs
- Minikube documentation: https://minikube.sigs.k8s.io` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that feature description, do this:

1. **Generate a concise short name** (2-4 words) for the branch:
   - Analyze the feature description and extract the most meaningful keywords
   - Create a 2-4 word short name that captures the essence of the feature
   - Use action-noun format when possible (e.g., "add-user-auth", "fix-payment-bug")
   - Preserve technical terms and acronyms (OAuth2, API, JWT, etc.)
   - Keep it concise but descriptive enough to understand the feature at a glance
   - Examples:
     - "I want to add user authentication" → "user-auth"
     - "Implement OAuth2 integration for the API" → "oauth2-api-integration"
     - "Create a dashboard for analytics" → "analytics-dashboard"
     - "Fix payment processing timeout bug" → "fix-payment-timeout"

2. **Check for existing branches before creating new one**:

   a. First, fetch all remote branches to ensure we have the latest information:

      ```bash
      git fetch --all --prune
      ```

   b. Find the highest feature number across all sources for the short-name:
      - Remote branches: `git ls-remote --heads origin | grep -E 'refs/heads/[0-9]+-<short-name>$'`
      - Local branches: `git branch | grep -E '^[* ]*[0-9]+-<short-name>$'`
      - Specs directories: Check for directories matching `specs/[0-9]+-<short-name>`

   c. Determine the next available number:
      - Extract all numbers from all three sources
      - Find the highest number N
      - Use N+1 for the new branch number

   d. Run the script `.specify/scripts/bash/create-new-feature.sh --json "# Phase 4 Specification: Local Kubernetes Deployment

## Overview
Deploy the existing Todo AI Chatbot (from Phase 3) to a local Kubernetes cluster using Minikube, Docker containers, and Helm charts. This phase focuses on containerization and orchestration without adding new features.

## User Stories

### US-4.1: Developer Containerizes Frontend
**As a** developer
**I want to** containerize the Next.js frontend application
**So that** it can run in Kubernetes pods

**Acceptance Criteria:**
- Dockerfile exists in `/frontend/Dockerfile`
- Docker image builds successfully without errors
- Image size is under 500MB
- Container runs as non-root user
- Container serves the application on port 3000
- Health check endpoint responds at `/api/health`
- Environment variables control API_URL configuration
- `.dockerignore` excludes unnecessary files (node_modules, .git, etc.)

**Priority:** P0 (Critical)

---

### US-4.2: Developer Containerizes Backend
**As a** developer
**I want to** containerize the FastAPI backend application
**So that** it can run in Kubernetes pods

**Acceptance Criteria:**
- Dockerfile exists in `/backend/Dockerfile`
- Docker image builds successfully without errors
- Image size is under 300MB
- Container runs as non-root user
- Container serves the API on port 8000
- Health check endpoint responds at `/health`
- Environment variables control DATABASE_URL and other config
- `.dockerignore` excludes unnecessary files (\_\_pycache\_\_, .venv, etc.)
- All Python dependencies are properly installed

**Priority:** P0 (Critical)

---

### US-4.3: Developer Tests Containers Locally
**As a** developer
**I want to** test Docker containers before Kubernetes deployment
**So that** I can catch issues early

**Acceptance Criteria:**
- Frontend container starts successfully with `docker run`
- Backend container starts successfully with `docker run`
- Frontend serves pages and loads correctly
- Backend responds to API requests
- Backend can connect to external Neon database
- Containers can be stopped gracefully
- docker-compose.yml exists for local multi-container testing (optional)

**Priority:** P1 (High)

---

### US-4.4: Developer Creates Helm Chart Structure
**As a** developer
**I want to** create Helm charts for deployment
**So that** I can manage Kubernetes resources declaratively

**Acceptance Criteria:**
- Helm chart directory exists at `/k8s/helm/todo-app/`
- Chart.yaml contains proper metadata (name, version, description)
- values.yaml contains all configurable parameters
- Templates directory contains resource definitions
- Chart passes `helm lint` validation
- Default values are sensible for local development

**Priority:** P0 (Critical)

---

### US-4.5: Developer Defines Frontend Kubernetes Resources
**As a** developer
**I want to** define Kubernetes resources for the frontend
**So that** it can be deployed and accessed in the cluster

**Acceptance Criteria:**
- Deployment template exists for frontend
- Deployment specifies replica count (default: 1)
- Deployment includes resource requests and limits
- Deployment includes readiness and liveness probes
- Service template exists for frontend (ClusterIP type)
- Service exposes port 3000
- ConfigMap template exists for frontend configuration
- All resources have appropriate labels

**Priority:** P0 (Critical)

---

### US-4.6: Developer Defines Backend Kubernetes Resources
**As a** developer
**I want to** define Kubernetes resources for the backend
**So that** it can be deployed and accessed in the cluster

**Acceptance Criteria:**
- Deployment template exists for backend
- Deployment specifies replica count (default: 1)
- Deployment includes resource requests and limits
- Deployment includes readiness and liveness probes
- Service template exists for backend (ClusterIP type)
- Service exposes port 8000
- Secret template exists for sensitive config (DATABASE_URL, JWT_SECRET)
- ConfigMap template exists for non-sensitive config
- All resources have appropriate labels

**Priority:** P0 (Critical)

---

### US-4.7: Developer Deploys to Minikube
**As a** developer
**I want to** deploy the application to Minikube
**So that** I can run it in a local Kubernetes environment

**Acceptance Criteria:**
- Minikube cluster starts successfully
- Docker images are accessible to Minikube
- `helm install` completes without errors
- All pods reach Running state within 60 seconds
- `kubectl get pods` shows 0 restarts
- Frontend pod is accessible via service
- Backend pod is accessible via service
- Backend pod can connect to Neon database

**Priority:** P0 (Critical)

---

### US-4.8: Developer Accesses Application Locally
**As a** developer
**I want to** access the deployed application from my browser
**So that** I can verify it works correctly

**Acceptance Criteria:**
- Frontend is accessible via `kubectl port-forward` or NodePort
- Login page loads successfully
- User can sign up and log in
- Todo list displays correctly
- User can create, update, and delete tasks
- Chatbot interface works (if implemented in Phase 3)
- All functionality from Phase 3 works identically

**Priority:** P0 (Critical)

---

### US-4.9: Developer Uses kubectl-ai for Operations
**As a** developer
**I want to** use AI-assisted tools for Kubernetes operations
**So that** I can manage the cluster more efficiently

**Acceptance Criteria:**
- kubectl-ai is installed and configured
- Can use kubectl-ai to check pod status
- Can use kubectl-ai to scale deployments
- Can use kubectl-ai to debug failing pods
- Can use kubectl-ai to view logs
- Commands execute successfully and provide useful output

**Priority:** P2 (Medium)

---

### US-4.10: Developer Uses kagent for Cluster Management
**As a** developer
**I want to** use kagent for advanced cluster operations
**So that** I can analyze and optimize the deployment

**Acceptance Criteria:**
- kagent is installed and configured
- Can use kagent to analyze cluster health
- Can use kagent to optimize resource allocation
- Can use kagent to identify issues
- kagent provides actionable insights

**Priority:** P2 (Medium)

---

### US-4.11: Developer Documents Deployment Process
**As a** developer
**I want to** create comprehensive deployment documentation
**So that** others (and judges) can reproduce the deployment

**Acceptance Criteria:**
- README.md exists in `/k8s/` directory
- README includes prerequisites (Minikube, Docker, Helm, kubectl)
- README includes step-by-step deployment instructions
- README includes commands to verify deployment
- README includes commands to access the application
- README includes troubleshooting section
- README includes cleanup instructions
- All commands are copy-pasteable and work correctly

**Priority:** P1 (High)

---

### US-4.12: Developer Creates Demo Video
**As a** developer
**I want to** create a demo video showing the deployment
**So that** I can submit it with the hackathon

**Acceptance Criteria:**
- Video is under 90 seconds
- Video shows `helm install` command execution
- Video shows pods starting and reaching Running state
- Video shows accessing the application via browser
- Video demonstrates at least one task operation
- Video quality is clear and professional
- Video is uploaded and link is available

**Priority:** P1 (High)

---

## Technical Requirements

### Docker Images

#### Frontend Image
- **Base Image:** node:20-alpine or node:20-slim
- **Multi-Stage Build:** Yes (build stage + runtime stage)
- **Final Size:** < 500MB
- **User:** Non-root (node user)
- **Port:** 3000
- **Health Check:** GET /api/health returns 200
- **Environment Variables:**
  - NEXT_PUBLIC_API_URL (backend service URL)

#### Backend Image
- **Base Image:** python:3.13-slim or python:3.13-alpine
- **Multi-Stage Build:** Yes (build stage + runtime stage)
- **Final Size:** < 300MB
- **User:** Non-root (created user)
- **Port:** 8000
- **Health Check:** GET /health returns 200
- **Environment Variables:**
  - DATABASE_URL (Neon PostgreSQL connection string)
  - JWT_SECRET (signing key)
  - CORS_ORIGIN (frontend URL)

### Kubernetes Resources

#### Frontend Deployment
- **Replicas:** 1 (configurable via Helm values)
- **Image Pull Policy:** IfNotPresent (for local images)
- **Resource Requests:** 128Mi RAM, 0.25 CPU
- **Resource Limits:** 256Mi RAM, 0.5 CPU
- **Readiness Probe:** HTTP GET /api/health, initialDelaySeconds: 10
- **Liveness Probe:** HTTP GET /api/health, initialDelaySeconds: 15
- **Environment:** From ConfigMap

#### Backend Deployment
- **Replicas:** 1 (configurable via Helm values)
- **Image Pull Policy:** IfNotPresent (for local images)
- **Resource Requests:** 256Mi RAM, 0.5 CPU
- **Resource Limits:** 512Mi RAM, 1.0 CPU
- **Readiness Probe:** HTTP GET /health, initialDelaySeconds: 10
- **Liveness Probe:** HTTP GET /health, initialDelaySeconds: 15
- **Environment:** From ConfigMap and Secret

#### Services
- **Frontend Service:**
  - Type: ClusterIP (or NodePort for local access)
  - Port: 3000
  - TargetPort: 3000
  - Selector: app=todo-frontend

- **Backend Service:**
  - Type: ClusterIP
  - Port: 8000
  - TargetPort: 8000
  - Selector: app=todo-backend

### Helm Chart Structure

```
k8s/helm/todo-app/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration values
├── templates/
│   ├── _helpers.tpl        # Template helpers
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── frontend-configmap.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── backend-configmap.yaml
│   ├── backend-secret.yaml
│   └── NOTES.txt          # Post-install instructions
└── .helmignore
```

### Configuration Management

#### ConfigMaps (Non-Sensitive)
- Frontend:
  - NEXT_PUBLIC_API_URL: http://todo-backend:8000

- Backend:
  - CORS_ORIGIN: http://localhost:3000
  - LOG_LEVEL: info

#### Secrets (Sensitive)
- Backend:
  - DATABASE_URL: (Neon PostgreSQL connection string)
  - JWT_SECRET: (random secure string)
  - BETTER_AUTH_SECRET: (if applicable)

## Non-Functional Requirements

### Performance
- Pod startup time: < 30 seconds
- Application response time: < 500ms
- Container restart time: < 15 seconds

### Reliability
- Pods restart automatically on crash
- Zero-downtime for rolling updates (future phase)
- Graceful shutdown on SIGTERM

### Security
- No secrets in Docker images
- Containers run as non-root
- Minimal base images (alpine/slim)
- Network policies (optional enhancement)

### Maintainability
- Clear documentation for all components
- Helm values for easy configuration
- Meaningful labels and annotations
- Logical resource organization

## Testing Strategy

### Docker Image Testing
1. Build frontend image: `docker build -t todo-frontend:latest ./frontend`
2. Run frontend container: `docker run -p 3000:3000 todo-frontend:latest`
3. Verify frontend loads in browser: http://localhost:3000
4. Build backend image: `docker build -t todo-backend:latest ./backend`
5. Run backend container with env vars: `docker run -p 8000:8000 -e DATABASE_URL=... todo-backend:latest`
6. Verify backend health: curl http://localhost:8000/health

### Helm Chart Testing
1. Lint chart: `helm lint k8s/helm/todo-app`
2. Dry-run install: `helm install todo-app k8s/helm/todo-app --dry-run --debug`
3. Template output: `helm template todo-app k8s/helm/todo-app`
4. Verify templates are valid YAML

### Kubernetes Deployment Testing
1. Install chart: `helm install todo-app k8s/helm/todo-app`
2. Check pod status: `kubectl get pods -w`
3. Check pod logs: `kubectl logs -f <pod-name>`
4. Port-forward frontend: `kubectl port-forward service/todo-frontend 3000:3000`
5. Port-forward backend: `kubectl port-forward service/todo-backend 8000:8000`
6. Test application functionality
7. Check resource usage: `kubectl top pods`

### Integration Testing
1. Verify frontend → backend communication
2. Verify backend → database communication
3. Test complete user flow (signup → login → create task → view tasks)
4. Verify chatbot functionality (if implemented)

## Out of Scope

### Explicitly NOT INCLUDED
- ❌ New application features (use Phase 3 as-is)
- ❌ ChatKit integration (skipped due to time constraints)
- ❌ Cloud deployment (that's Phase 5)
- ❌ Kafka/Dapr (that's Phase 5)
- ❌ CI/CD pipelines (optional for Phase 5)
- ❌ Ingress controllers (use port-forward or NodePort)
- ❌ Persistent volumes (database is external)
- ❌ StatefulSets (not needed for stateless app)
- ❌ Horizontal Pod Autoscaling (nice-to-have)
- ❌ Advanced networking (service mesh, etc.)

## Success Metrics

### Quantitative
- ✅ 2 Docker images built successfully
- ✅ 1 Helm chart created
- ✅ 2 services deployed (frontend + backend)
- ✅ 2 deployments running (frontend + backend)
- ✅ 100% of pods in Running state
- ✅ 0 pod restarts
- ✅ 1 demo video created (< 90 seconds)

### Qualitative
- ✅ Application works identically to Phase 3
- ✅ Deployment process is reproducible
- ✅ Documentation is clear and complete
- ✅ Docker images follow best practices
- ✅ Kubernetes resources are properly configured
- ✅ Demonstrates understanding of container orchestration

## Dependencies

### External Dependencies
- Neon PostgreSQL database (from Phase 2/3)
- GitHub repository (for version control)
- Vercel deployment (Phase 3, for comparison)

### Tool Dependencies
- Docker Desktop 4.53+ (or Docker Engine + Minikube with Docker driver)
- Minikube (latest stable version)
- kubectl (matching Minikube Kubernetes version)
- Helm 3.x
- kubectl-ai (optional but recommended)
- kagent (optional but recommended)

### Knowledge Dependencies
- Docker fundamentals (images, containers, Dockerfiles)
- Kubernetes basics (pods, services, deployments)
- Helm basics (charts, templates, values)
- YAML syntax
- Environment variable management

## Risks and Mitigations

### Risk: Docker Image Too Large
**Mitigation:** Use multi-stage builds, alpine base images, minimize dependencies

### Risk: Pods Failing to Start
**Mitigation:** Test containers locally first, check logs, verify health checks

### Risk: Database Connection Issues
**Mitigation:** Verify network connectivity, check credentials, test from within pod

### Risk: Time Constraint (Due Jan 4)
**Mitigation:** Focus on P0/P1 user stories first, skip optional features (kubectl-ai, kagent)

### Risk: Minikube Resource Limitations
**Mitigation:** Set conservative resource requests/limits, ensure enough RAM allocated to Minikube

## Acceptance Criteria Summary

The Phase 4 submission is considered complete when:

1. ✅ Frontend Dockerfile exists and builds successfully
2. ✅ Backend Dockerfile exists and builds successfully
3. ✅ Helm chart exists with all required templates
4. ✅ Application deploys to Minikube without errors
5. ✅ All pods are Running with 0 restarts
6. ✅ Application is accessible via port-forward
7. ✅ All Phase 3 functionality works correctly
8. ✅ Documentation is complete and accurate
9. ✅ Demo video is recorded and submitted
10. ✅ GitHub repository is updated with all files

## References
- Hackathon Phase 4 requirements
- Phase 3 application (baseline)
- Docker documentation: https://docs.docker.com
- Kubernetes documentation: https://kubernetes.io/docs
- Helm documentation: https://helm.sh/docs
- Minikube documentation: https://minikube.sigs.k8s.io"` with the calculated number and short-name:
      - Pass `--number N+1` and `--short-name "your-short-name"` along with the feature description
      - Bash example: `.specify/scripts/bash/create-new-feature.sh --json "# Phase 4 Specification: Local Kubernetes Deployment

## Overview
Deploy the existing Todo AI Chatbot (from Phase 3) to a local Kubernetes cluster using Minikube, Docker containers, and Helm charts. This phase focuses on containerization and orchestration without adding new features.

## User Stories

### US-4.1: Developer Containerizes Frontend
**As a** developer
**I want to** containerize the Next.js frontend application
**So that** it can run in Kubernetes pods

**Acceptance Criteria:**
- Dockerfile exists in `/frontend/Dockerfile`
- Docker image builds successfully without errors
- Image size is under 500MB
- Container runs as non-root user
- Container serves the application on port 3000
- Health check endpoint responds at `/api/health`
- Environment variables control API_URL configuration
- `.dockerignore` excludes unnecessary files (node_modules, .git, etc.)

**Priority:** P0 (Critical)

---

### US-4.2: Developer Containerizes Backend
**As a** developer
**I want to** containerize the FastAPI backend application
**So that** it can run in Kubernetes pods

**Acceptance Criteria:**
- Dockerfile exists in `/backend/Dockerfile`
- Docker image builds successfully without errors
- Image size is under 300MB
- Container runs as non-root user
- Container serves the API on port 8000
- Health check endpoint responds at `/health`
- Environment variables control DATABASE_URL and other config
- `.dockerignore` excludes unnecessary files (\_\_pycache\_\_, .venv, etc.)
- All Python dependencies are properly installed

**Priority:** P0 (Critical)

---

### US-4.3: Developer Tests Containers Locally
**As a** developer
**I want to** test Docker containers before Kubernetes deployment
**So that** I can catch issues early

**Acceptance Criteria:**
- Frontend container starts successfully with `docker run`
- Backend container starts successfully with `docker run`
- Frontend serves pages and loads correctly
- Backend responds to API requests
- Backend can connect to external Neon database
- Containers can be stopped gracefully
- docker-compose.yml exists for local multi-container testing (optional)

**Priority:** P1 (High)

---

### US-4.4: Developer Creates Helm Chart Structure
**As a** developer
**I want to** create Helm charts for deployment
**So that** I can manage Kubernetes resources declaratively

**Acceptance Criteria:**
- Helm chart directory exists at `/k8s/helm/todo-app/`
- Chart.yaml contains proper metadata (name, version, description)
- values.yaml contains all configurable parameters
- Templates directory contains resource definitions
- Chart passes `helm lint` validation
- Default values are sensible for local development

**Priority:** P0 (Critical)

---

### US-4.5: Developer Defines Frontend Kubernetes Resources
**As a** developer
**I want to** define Kubernetes resources for the frontend
**So that** it can be deployed and accessed in the cluster

**Acceptance Criteria:**
- Deployment template exists for frontend
- Deployment specifies replica count (default: 1)
- Deployment includes resource requests and limits
- Deployment includes readiness and liveness probes
- Service template exists for frontend (ClusterIP type)
- Service exposes port 3000
- ConfigMap template exists for frontend configuration
- All resources have appropriate labels

**Priority:** P0 (Critical)

---

### US-4.6: Developer Defines Backend Kubernetes Resources
**As a** developer
**I want to** define Kubernetes resources for the backend
**So that** it can be deployed and accessed in the cluster

**Acceptance Criteria:**
- Deployment template exists for backend
- Deployment specifies replica count (default: 1)
- Deployment includes resource requests and limits
- Deployment includes readiness and liveness probes
- Service template exists for backend (ClusterIP type)
- Service exposes port 8000
- Secret template exists for sensitive config (DATABASE_URL, JWT_SECRET)
- ConfigMap template exists for non-sensitive config
- All resources have appropriate labels

**Priority:** P0 (Critical)

---

### US-4.7: Developer Deploys to Minikube
**As a** developer
**I want to** deploy the application to Minikube
**So that** I can run it in a local Kubernetes environment

**Acceptance Criteria:**
- Minikube cluster starts successfully
- Docker images are accessible to Minikube
- `helm install` completes without errors
- All pods reach Running state within 60 seconds
- `kubectl get pods` shows 0 restarts
- Frontend pod is accessible via service
- Backend pod is accessible via service
- Backend pod can connect to Neon database

**Priority:** P0 (Critical)

---

### US-4.8: Developer Accesses Application Locally
**As a** developer
**I want to** access the deployed application from my browser
**So that** I can verify it works correctly

**Acceptance Criteria:**
- Frontend is accessible via `kubectl port-forward` or NodePort
- Login page loads successfully
- User can sign up and log in
- Todo list displays correctly
- User can create, update, and delete tasks
- Chatbot interface works (if implemented in Phase 3)
- All functionality from Phase 3 works identically

**Priority:** P0 (Critical)

---

### US-4.9: Developer Uses kubectl-ai for Operations
**As a** developer
**I want to** use AI-assisted tools for Kubernetes operations
**So that** I can manage the cluster more efficiently

**Acceptance Criteria:**
- kubectl-ai is installed and configured
- Can use kubectl-ai to check pod status
- Can use kubectl-ai to scale deployments
- Can use kubectl-ai to debug failing pods
- Can use kubectl-ai to view logs
- Commands execute successfully and provide useful output

**Priority:** P2 (Medium)

---

### US-4.10: Developer Uses kagent for Cluster Management
**As a** developer
**I want to** use kagent for advanced cluster operations
**So that** I can analyze and optimize the deployment

**Acceptance Criteria:**
- kagent is installed and configured
- Can use kagent to analyze cluster health
- Can use kagent to optimize resource allocation
- Can use kagent to identify issues
- kagent provides actionable insights

**Priority:** P2 (Medium)

---

### US-4.11: Developer Documents Deployment Process
**As a** developer
**I want to** create comprehensive deployment documentation
**So that** others (and judges) can reproduce the deployment

**Acceptance Criteria:**
- README.md exists in `/k8s/` directory
- README includes prerequisites (Minikube, Docker, Helm, kubectl)
- README includes step-by-step deployment instructions
- README includes commands to verify deployment
- README includes commands to access the application
- README includes troubleshooting section
- README includes cleanup instructions
- All commands are copy-pasteable and work correctly

**Priority:** P1 (High)

---

### US-4.12: Developer Creates Demo Video
**As a** developer
**I want to** create a demo video showing the deployment
**So that** I can submit it with the hackathon

**Acceptance Criteria:**
- Video is under 90 seconds
- Video shows `helm install` command execution
- Video shows pods starting and reaching Running state
- Video shows accessing the application via browser
- Video demonstrates at least one task operation
- Video quality is clear and professional
- Video is uploaded and link is available

**Priority:** P1 (High)

---

## Technical Requirements

### Docker Images

#### Frontend Image
- **Base Image:** node:20-alpine or node:20-slim
- **Multi-Stage Build:** Yes (build stage + runtime stage)
- **Final Size:** < 500MB
- **User:** Non-root (node user)
- **Port:** 3000
- **Health Check:** GET /api/health returns 200
- **Environment Variables:**
  - NEXT_PUBLIC_API_URL (backend service URL)

#### Backend Image
- **Base Image:** python:3.13-slim or python:3.13-alpine
- **Multi-Stage Build:** Yes (build stage + runtime stage)
- **Final Size:** < 300MB
- **User:** Non-root (created user)
- **Port:** 8000
- **Health Check:** GET /health returns 200
- **Environment Variables:**
  - DATABASE_URL (Neon PostgreSQL connection string)
  - JWT_SECRET (signing key)
  - CORS_ORIGIN (frontend URL)

### Kubernetes Resources

#### Frontend Deployment
- **Replicas:** 1 (configurable via Helm values)
- **Image Pull Policy:** IfNotPresent (for local images)
- **Resource Requests:** 128Mi RAM, 0.25 CPU
- **Resource Limits:** 256Mi RAM, 0.5 CPU
- **Readiness Probe:** HTTP GET /api/health, initialDelaySeconds: 10
- **Liveness Probe:** HTTP GET /api/health, initialDelaySeconds: 15
- **Environment:** From ConfigMap

#### Backend Deployment
- **Replicas:** 1 (configurable via Helm values)
- **Image Pull Policy:** IfNotPresent (for local images)
- **Resource Requests:** 256Mi RAM, 0.5 CPU
- **Resource Limits:** 512Mi RAM, 1.0 CPU
- **Readiness Probe:** HTTP GET /health, initialDelaySeconds: 10
- **Liveness Probe:** HTTP GET /health, initialDelaySeconds: 15
- **Environment:** From ConfigMap and Secret

#### Services
- **Frontend Service:**
  - Type: ClusterIP (or NodePort for local access)
  - Port: 3000
  - TargetPort: 3000
  - Selector: app=todo-frontend

- **Backend Service:**
  - Type: ClusterIP
  - Port: 8000
  - TargetPort: 8000
  - Selector: app=todo-backend

### Helm Chart Structure

```
k8s/helm/todo-app/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration values
├── templates/
│   ├── _helpers.tpl        # Template helpers
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── frontend-configmap.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── backend-configmap.yaml
│   ├── backend-secret.yaml
│   └── NOTES.txt          # Post-install instructions
└── .helmignore
```

### Configuration Management

#### ConfigMaps (Non-Sensitive)
- Frontend:
  - NEXT_PUBLIC_API_URL: http://todo-backend:8000

- Backend:
  - CORS_ORIGIN: http://localhost:3000
  - LOG_LEVEL: info

#### Secrets (Sensitive)
- Backend:
  - DATABASE_URL: (Neon PostgreSQL connection string)
  - JWT_SECRET: (random secure string)
  - BETTER_AUTH_SECRET: (if applicable)

## Non-Functional Requirements

### Performance
- Pod startup time: < 30 seconds
- Application response time: < 500ms
- Container restart time: < 15 seconds

### Reliability
- Pods restart automatically on crash
- Zero-downtime for rolling updates (future phase)
- Graceful shutdown on SIGTERM

### Security
- No secrets in Docker images
- Containers run as non-root
- Minimal base images (alpine/slim)
- Network policies (optional enhancement)

### Maintainability
- Clear documentation for all components
- Helm values for easy configuration
- Meaningful labels and annotations
- Logical resource organization

## Testing Strategy

### Docker Image Testing
1. Build frontend image: `docker build -t todo-frontend:latest ./frontend`
2. Run frontend container: `docker run -p 3000:3000 todo-frontend:latest`
3. Verify frontend loads in browser: http://localhost:3000
4. Build backend image: `docker build -t todo-backend:latest ./backend`
5. Run backend container with env vars: `docker run -p 8000:8000 -e DATABASE_URL=... todo-backend:latest`
6. Verify backend health: curl http://localhost:8000/health

### Helm Chart Testing
1. Lint chart: `helm lint k8s/helm/todo-app`
2. Dry-run install: `helm install todo-app k8s/helm/todo-app --dry-run --debug`
3. Template output: `helm template todo-app k8s/helm/todo-app`
4. Verify templates are valid YAML

### Kubernetes Deployment Testing
1. Install chart: `helm install todo-app k8s/helm/todo-app`
2. Check pod status: `kubectl get pods -w`
3. Check pod logs: `kubectl logs -f <pod-name>`
4. Port-forward frontend: `kubectl port-forward service/todo-frontend 3000:3000`
5. Port-forward backend: `kubectl port-forward service/todo-backend 8000:8000`
6. Test application functionality
7. Check resource usage: `kubectl top pods`

### Integration Testing
1. Verify frontend → backend communication
2. Verify backend → database communication
3. Test complete user flow (signup → login → create task → view tasks)
4. Verify chatbot functionality (if implemented)

## Out of Scope

### Explicitly NOT INCLUDED
- ❌ New application features (use Phase 3 as-is)
- ❌ ChatKit integration (skipped due to time constraints)
- ❌ Cloud deployment (that's Phase 5)
- ❌ Kafka/Dapr (that's Phase 5)
- ❌ CI/CD pipelines (optional for Phase 5)
- ❌ Ingress controllers (use port-forward or NodePort)
- ❌ Persistent volumes (database is external)
- ❌ StatefulSets (not needed for stateless app)
- ❌ Horizontal Pod Autoscaling (nice-to-have)
- ❌ Advanced networking (service mesh, etc.)

## Success Metrics

### Quantitative
- ✅ 2 Docker images built successfully
- ✅ 1 Helm chart created
- ✅ 2 services deployed (frontend + backend)
- ✅ 2 deployments running (frontend + backend)
- ✅ 100% of pods in Running state
- ✅ 0 pod restarts
- ✅ 1 demo video created (< 90 seconds)

### Qualitative
- ✅ Application works identically to Phase 3
- ✅ Deployment process is reproducible
- ✅ Documentation is clear and complete
- ✅ Docker images follow best practices
- ✅ Kubernetes resources are properly configured
- ✅ Demonstrates understanding of container orchestration

## Dependencies

### External Dependencies
- Neon PostgreSQL database (from Phase 2/3)
- GitHub repository (for version control)
- Vercel deployment (Phase 3, for comparison)

### Tool Dependencies
- Docker Desktop 4.53+ (or Docker Engine + Minikube with Docker driver)
- Minikube (latest stable version)
- kubectl (matching Minikube Kubernetes version)
- Helm 3.x
- kubectl-ai (optional but recommended)
- kagent (optional but recommended)

### Knowledge Dependencies
- Docker fundamentals (images, containers, Dockerfiles)
- Kubernetes basics (pods, services, deployments)
- Helm basics (charts, templates, values)
- YAML syntax
- Environment variable management

## Risks and Mitigations

### Risk: Docker Image Too Large
**Mitigation:** Use multi-stage builds, alpine base images, minimize dependencies

### Risk: Pods Failing to Start
**Mitigation:** Test containers locally first, check logs, verify health checks

### Risk: Database Connection Issues
**Mitigation:** Verify network connectivity, check credentials, test from within pod

### Risk: Time Constraint (Due Jan 4)
**Mitigation:** Focus on P0/P1 user stories first, skip optional features (kubectl-ai, kagent)

### Risk: Minikube Resource Limitations
**Mitigation:** Set conservative resource requests/limits, ensure enough RAM allocated to Minikube

## Acceptance Criteria Summary

The Phase 4 submission is considered complete when:

1. ✅ Frontend Dockerfile exists and builds successfully
2. ✅ Backend Dockerfile exists and builds successfully
3. ✅ Helm chart exists with all required templates
4. ✅ Application deploys to Minikube without errors
5. ✅ All pods are Running with 0 restarts
6. ✅ Application is accessible via port-forward
7. ✅ All Phase 3 functionality works correctly
8. ✅ Documentation is complete and accurate
9. ✅ Demo video is recorded and submitted
10. ✅ GitHub repository is updated with all files

## References
- Hackathon Phase 4 requirements
- Phase 3 application (baseline)
- Docker documentation: https://docs.docker.com
- Kubernetes documentation: https://kubernetes.io/docs
- Helm documentation: https://helm.sh/docs
- Minikube documentation: https://minikube.sigs.k8s.io" --json --number 5 --short-name "user-auth" "Add user authentication"`
      - PowerShell example: `.specify/scripts/bash/create-new-feature.sh --json "# Phase 4 Specification: Local Kubernetes Deployment

## Overview
Deploy the existing Todo AI Chatbot (from Phase 3) to a local Kubernetes cluster using Minikube, Docker containers, and Helm charts. This phase focuses on containerization and orchestration without adding new features.

## User Stories

### US-4.1: Developer Containerizes Frontend
**As a** developer
**I want to** containerize the Next.js frontend application
**So that** it can run in Kubernetes pods

**Acceptance Criteria:**
- Dockerfile exists in `/frontend/Dockerfile`
- Docker image builds successfully without errors
- Image size is under 500MB
- Container runs as non-root user
- Container serves the application on port 3000
- Health check endpoint responds at `/api/health`
- Environment variables control API_URL configuration
- `.dockerignore` excludes unnecessary files (node_modules, .git, etc.)

**Priority:** P0 (Critical)

---

### US-4.2: Developer Containerizes Backend
**As a** developer
**I want to** containerize the FastAPI backend application
**So that** it can run in Kubernetes pods

**Acceptance Criteria:**
- Dockerfile exists in `/backend/Dockerfile`
- Docker image builds successfully without errors
- Image size is under 300MB
- Container runs as non-root user
- Container serves the API on port 8000
- Health check endpoint responds at `/health`
- Environment variables control DATABASE_URL and other config
- `.dockerignore` excludes unnecessary files (\_\_pycache\_\_, .venv, etc.)
- All Python dependencies are properly installed

**Priority:** P0 (Critical)

---

### US-4.3: Developer Tests Containers Locally
**As a** developer
**I want to** test Docker containers before Kubernetes deployment
**So that** I can catch issues early

**Acceptance Criteria:**
- Frontend container starts successfully with `docker run`
- Backend container starts successfully with `docker run`
- Frontend serves pages and loads correctly
- Backend responds to API requests
- Backend can connect to external Neon database
- Containers can be stopped gracefully
- docker-compose.yml exists for local multi-container testing (optional)

**Priority:** P1 (High)

---

### US-4.4: Developer Creates Helm Chart Structure
**As a** developer
**I want to** create Helm charts for deployment
**So that** I can manage Kubernetes resources declaratively

**Acceptance Criteria:**
- Helm chart directory exists at `/k8s/helm/todo-app/`
- Chart.yaml contains proper metadata (name, version, description)
- values.yaml contains all configurable parameters
- Templates directory contains resource definitions
- Chart passes `helm lint` validation
- Default values are sensible for local development

**Priority:** P0 (Critical)

---

### US-4.5: Developer Defines Frontend Kubernetes Resources
**As a** developer
**I want to** define Kubernetes resources for the frontend
**So that** it can be deployed and accessed in the cluster

**Acceptance Criteria:**
- Deployment template exists for frontend
- Deployment specifies replica count (default: 1)
- Deployment includes resource requests and limits
- Deployment includes readiness and liveness probes
- Service template exists for frontend (ClusterIP type)
- Service exposes port 3000
- ConfigMap template exists for frontend configuration
- All resources have appropriate labels

**Priority:** P0 (Critical)

---

### US-4.6: Developer Defines Backend Kubernetes Resources
**As a** developer
**I want to** define Kubernetes resources for the backend
**So that** it can be deployed and accessed in the cluster

**Acceptance Criteria:**
- Deployment template exists for backend
- Deployment specifies replica count (default: 1)
- Deployment includes resource requests and limits
- Deployment includes readiness and liveness probes
- Service template exists for backend (ClusterIP type)
- Service exposes port 8000
- Secret template exists for sensitive config (DATABASE_URL, JWT_SECRET)
- ConfigMap template exists for non-sensitive config
- All resources have appropriate labels

**Priority:** P0 (Critical)

---

### US-4.7: Developer Deploys to Minikube
**As a** developer
**I want to** deploy the application to Minikube
**So that** I can run it in a local Kubernetes environment

**Acceptance Criteria:**
- Minikube cluster starts successfully
- Docker images are accessible to Minikube
- `helm install` completes without errors
- All pods reach Running state within 60 seconds
- `kubectl get pods` shows 0 restarts
- Frontend pod is accessible via service
- Backend pod is accessible via service
- Backend pod can connect to Neon database

**Priority:** P0 (Critical)

---

### US-4.8: Developer Accesses Application Locally
**As a** developer
**I want to** access the deployed application from my browser
**So that** I can verify it works correctly

**Acceptance Criteria:**
- Frontend is accessible via `kubectl port-forward` or NodePort
- Login page loads successfully
- User can sign up and log in
- Todo list displays correctly
- User can create, update, and delete tasks
- Chatbot interface works (if implemented in Phase 3)
- All functionality from Phase 3 works identically

**Priority:** P0 (Critical)

---

### US-4.9: Developer Uses kubectl-ai for Operations
**As a** developer
**I want to** use AI-assisted tools for Kubernetes operations
**So that** I can manage the cluster more efficiently

**Acceptance Criteria:**
- kubectl-ai is installed and configured
- Can use kubectl-ai to check pod status
- Can use kubectl-ai to scale deployments
- Can use kubectl-ai to debug failing pods
- Can use kubectl-ai to view logs
- Commands execute successfully and provide useful output

**Priority:** P2 (Medium)

---

### US-4.10: Developer Uses kagent for Cluster Management
**As a** developer
**I want to** use kagent for advanced cluster operations
**So that** I can analyze and optimize the deployment

**Acceptance Criteria:**
- kagent is installed and configured
- Can use kagent to analyze cluster health
- Can use kagent to optimize resource allocation
- Can use kagent to identify issues
- kagent provides actionable insights

**Priority:** P2 (Medium)

---

### US-4.11: Developer Documents Deployment Process
**As a** developer
**I want to** create comprehensive deployment documentation
**So that** others (and judges) can reproduce the deployment

**Acceptance Criteria:**
- README.md exists in `/k8s/` directory
- README includes prerequisites (Minikube, Docker, Helm, kubectl)
- README includes step-by-step deployment instructions
- README includes commands to verify deployment
- README includes commands to access the application
- README includes troubleshooting section
- README includes cleanup instructions
- All commands are copy-pasteable and work correctly

**Priority:** P1 (High)

---

### US-4.12: Developer Creates Demo Video
**As a** developer
**I want to** create a demo video showing the deployment
**So that** I can submit it with the hackathon

**Acceptance Criteria:**
- Video is under 90 seconds
- Video shows `helm install` command execution
- Video shows pods starting and reaching Running state
- Video shows accessing the application via browser
- Video demonstrates at least one task operation
- Video quality is clear and professional
- Video is uploaded and link is available

**Priority:** P1 (High)

---

## Technical Requirements

### Docker Images

#### Frontend Image
- **Base Image:** node:20-alpine or node:20-slim
- **Multi-Stage Build:** Yes (build stage + runtime stage)
- **Final Size:** < 500MB
- **User:** Non-root (node user)
- **Port:** 3000
- **Health Check:** GET /api/health returns 200
- **Environment Variables:**
  - NEXT_PUBLIC_API_URL (backend service URL)

#### Backend Image
- **Base Image:** python:3.13-slim or python:3.13-alpine
- **Multi-Stage Build:** Yes (build stage + runtime stage)
- **Final Size:** < 300MB
- **User:** Non-root (created user)
- **Port:** 8000
- **Health Check:** GET /health returns 200
- **Environment Variables:**
  - DATABASE_URL (Neon PostgreSQL connection string)
  - JWT_SECRET (signing key)
  - CORS_ORIGIN (frontend URL)

### Kubernetes Resources

#### Frontend Deployment
- **Replicas:** 1 (configurable via Helm values)
- **Image Pull Policy:** IfNotPresent (for local images)
- **Resource Requests:** 128Mi RAM, 0.25 CPU
- **Resource Limits:** 256Mi RAM, 0.5 CPU
- **Readiness Probe:** HTTP GET /api/health, initialDelaySeconds: 10
- **Liveness Probe:** HTTP GET /api/health, initialDelaySeconds: 15
- **Environment:** From ConfigMap

#### Backend Deployment
- **Replicas:** 1 (configurable via Helm values)
- **Image Pull Policy:** IfNotPresent (for local images)
- **Resource Requests:** 256Mi RAM, 0.5 CPU
- **Resource Limits:** 512Mi RAM, 1.0 CPU
- **Readiness Probe:** HTTP GET /health, initialDelaySeconds: 10
- **Liveness Probe:** HTTP GET /health, initialDelaySeconds: 15
- **Environment:** From ConfigMap and Secret

#### Services
- **Frontend Service:**
  - Type: ClusterIP (or NodePort for local access)
  - Port: 3000
  - TargetPort: 3000
  - Selector: app=todo-frontend

- **Backend Service:**
  - Type: ClusterIP
  - Port: 8000
  - TargetPort: 8000
  - Selector: app=todo-backend

### Helm Chart Structure

```
k8s/helm/todo-app/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration values
├── templates/
│   ├── _helpers.tpl        # Template helpers
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── frontend-configmap.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── backend-configmap.yaml
│   ├── backend-secret.yaml
│   └── NOTES.txt          # Post-install instructions
└── .helmignore
```

### Configuration Management

#### ConfigMaps (Non-Sensitive)
- Frontend:
  - NEXT_PUBLIC_API_URL: http://todo-backend:8000

- Backend:
  - CORS_ORIGIN: http://localhost:3000
  - LOG_LEVEL: info

#### Secrets (Sensitive)
- Backend:
  - DATABASE_URL: (Neon PostgreSQL connection string)
  - JWT_SECRET: (random secure string)
  - BETTER_AUTH_SECRET: (if applicable)

## Non-Functional Requirements

### Performance
- Pod startup time: < 30 seconds
- Application response time: < 500ms
- Container restart time: < 15 seconds

### Reliability
- Pods restart automatically on crash
- Zero-downtime for rolling updates (future phase)
- Graceful shutdown on SIGTERM

### Security
- No secrets in Docker images
- Containers run as non-root
- Minimal base images (alpine/slim)
- Network policies (optional enhancement)

### Maintainability
- Clear documentation for all components
- Helm values for easy configuration
- Meaningful labels and annotations
- Logical resource organization

## Testing Strategy

### Docker Image Testing
1. Build frontend image: `docker build -t todo-frontend:latest ./frontend`
2. Run frontend container: `docker run -p 3000:3000 todo-frontend:latest`
3. Verify frontend loads in browser: http://localhost:3000
4. Build backend image: `docker build -t todo-backend:latest ./backend`
5. Run backend container with env vars: `docker run -p 8000:8000 -e DATABASE_URL=... todo-backend:latest`
6. Verify backend health: curl http://localhost:8000/health

### Helm Chart Testing
1. Lint chart: `helm lint k8s/helm/todo-app`
2. Dry-run install: `helm install todo-app k8s/helm/todo-app --dry-run --debug`
3. Template output: `helm template todo-app k8s/helm/todo-app`
4. Verify templates are valid YAML

### Kubernetes Deployment Testing
1. Install chart: `helm install todo-app k8s/helm/todo-app`
2. Check pod status: `kubectl get pods -w`
3. Check pod logs: `kubectl logs -f <pod-name>`
4. Port-forward frontend: `kubectl port-forward service/todo-frontend 3000:3000`
5. Port-forward backend: `kubectl port-forward service/todo-backend 8000:8000`
6. Test application functionality
7. Check resource usage: `kubectl top pods`

### Integration Testing
1. Verify frontend → backend communication
2. Verify backend → database communication
3. Test complete user flow (signup → login → create task → view tasks)
4. Verify chatbot functionality (if implemented)

## Out of Scope

### Explicitly NOT INCLUDED
- ❌ New application features (use Phase 3 as-is)
- ❌ ChatKit integration (skipped due to time constraints)
- ❌ Cloud deployment (that's Phase 5)
- ❌ Kafka/Dapr (that's Phase 5)
- ❌ CI/CD pipelines (optional for Phase 5)
- ❌ Ingress controllers (use port-forward or NodePort)
- ❌ Persistent volumes (database is external)
- ❌ StatefulSets (not needed for stateless app)
- ❌ Horizontal Pod Autoscaling (nice-to-have)
- ❌ Advanced networking (service mesh, etc.)

## Success Metrics

### Quantitative
- ✅ 2 Docker images built successfully
- ✅ 1 Helm chart created
- ✅ 2 services deployed (frontend + backend)
- ✅ 2 deployments running (frontend + backend)
- ✅ 100% of pods in Running state
- ✅ 0 pod restarts
- ✅ 1 demo video created (< 90 seconds)

### Qualitative
- ✅ Application works identically to Phase 3
- ✅ Deployment process is reproducible
- ✅ Documentation is clear and complete
- ✅ Docker images follow best practices
- ✅ Kubernetes resources are properly configured
- ✅ Demonstrates understanding of container orchestration

## Dependencies

### External Dependencies
- Neon PostgreSQL database (from Phase 2/3)
- GitHub repository (for version control)
- Vercel deployment (Phase 3, for comparison)

### Tool Dependencies
- Docker Desktop 4.53+ (or Docker Engine + Minikube with Docker driver)
- Minikube (latest stable version)
- kubectl (matching Minikube Kubernetes version)
- Helm 3.x
- kubectl-ai (optional but recommended)
- kagent (optional but recommended)

### Knowledge Dependencies
- Docker fundamentals (images, containers, Dockerfiles)
- Kubernetes basics (pods, services, deployments)
- Helm basics (charts, templates, values)
- YAML syntax
- Environment variable management

## Risks and Mitigations

### Risk: Docker Image Too Large
**Mitigation:** Use multi-stage builds, alpine base images, minimize dependencies

### Risk: Pods Failing to Start
**Mitigation:** Test containers locally first, check logs, verify health checks

### Risk: Database Connection Issues
**Mitigation:** Verify network connectivity, check credentials, test from within pod

### Risk: Time Constraint (Due Jan 4)
**Mitigation:** Focus on P0/P1 user stories first, skip optional features (kubectl-ai, kagent)

### Risk: Minikube Resource Limitations
**Mitigation:** Set conservative resource requests/limits, ensure enough RAM allocated to Minikube

## Acceptance Criteria Summary

The Phase 4 submission is considered complete when:

1. ✅ Frontend Dockerfile exists and builds successfully
2. ✅ Backend Dockerfile exists and builds successfully
3. ✅ Helm chart exists with all required templates
4. ✅ Application deploys to Minikube without errors
5. ✅ All pods are Running with 0 restarts
6. ✅ Application is accessible via port-forward
7. ✅ All Phase 3 functionality works correctly
8. ✅ Documentation is complete and accurate
9. ✅ Demo video is recorded and submitted
10. ✅ GitHub repository is updated with all files

## References
- Hackathon Phase 4 requirements
- Phase 3 application (baseline)
- Docker documentation: https://docs.docker.com
- Kubernetes documentation: https://kubernetes.io/docs
- Helm documentation: https://helm.sh/docs
- Minikube documentation: https://minikube.sigs.k8s.io" -Json -Number 5 -ShortName "user-auth" "Add user authentication"`

   **IMPORTANT**:
   - Check all three sources (remote branches, local branches, specs directories) to find the highest number
   - Only match branches/directories with the exact short-name pattern
   - If no existing branches/directories found with this short-name, start with number 1
   - You must only ever run this script once per feature
   - The JSON is provided in the terminal as output - always refer to it to get the actual content you're looking for
   - The JSON output will contain BRANCH_NAME and SPEC_FILE paths
   - For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot")

3. Load `.specify/templates/spec-template.md` to understand required sections.

4. Follow this execution flow:

    1. Parse user description from Input
       If empty: ERROR "No feature description provided"
    2. Extract key concepts from description
       Identify: actors, actions, data, constraints
    3. For unclear aspects:
       - Make informed guesses based on context and industry standards
       - Only mark with [NEEDS CLARIFICATION: specific question] if:
         - The choice significantly impacts feature scope or user experience
         - Multiple reasonable interpretations exist with different implications
         - No reasonable default exists
       - **LIMIT: Maximum 3 [NEEDS CLARIFICATION] markers total**
       - Prioritize clarifications by impact: scope > security/privacy > user experience > technical details
    4. Fill User Scenarios & Testing section
       If no clear user flow: ERROR "Cannot determine user scenarios"
    5. Generate Functional Requirements
       Each requirement must be testable
       Use reasonable defaults for unspecified details (document assumptions in Assumptions section)
    6. Define Success Criteria
       Create measurable, technology-agnostic outcomes
       Include both quantitative metrics (time, performance, volume) and qualitative measures (user satisfaction, task completion)
       Each criterion must be verifiable without implementation details
    7. Identify Key Entities (if data involved)
    8. Return: SUCCESS (spec ready for planning)

5. Write the specification to SPEC_FILE using the template structure, replacing placeholders with concrete details derived from the feature description (arguments) while preserving section order and headings.

6. **Specification Quality Validation**: After writing the initial spec, validate it against quality criteria:

   a. **Create Spec Quality Checklist**: Generate a checklist file at `FEATURE_DIR/checklists/requirements.md` using the checklist template structure with these validation items:

      ```markdown
      # Specification Quality Checklist: [FEATURE NAME]

      **Purpose**: Validate specification completeness and quality before proceeding to planning
      **Created**: [DATE]
      **Feature**: [Link to spec.md]

      ## Content Quality

      - [ ] No implementation details (languages, frameworks, APIs)
      - [ ] Focused on user value and business needs
      - [ ] Written for non-technical stakeholders
      - [ ] All mandatory sections completed

      ## Requirement Completeness

      - [ ] No [NEEDS CLARIFICATION] markers remain
      - [ ] Requirements are testable and unambiguous
      - [ ] Success criteria are measurable
      - [ ] Success criteria are technology-agnostic (no implementation details)
      - [ ] All acceptance scenarios are defined
      - [ ] Edge cases are identified
      - [ ] Scope is clearly bounded
      - [ ] Dependencies and assumptions identified

      ## Feature Readiness

      - [ ] All functional requirements have clear acceptance criteria
      - [ ] User scenarios cover primary flows
      - [ ] Feature meets measurable outcomes defined in Success Criteria
      - [ ] No implementation details leak into specification

      ## Notes

      - Items marked incomplete require spec updates before `/sp.clarify` or `/sp.plan`
      ```

   b. **Run Validation Check**: Review the spec against each checklist item:
      - For each item, determine if it passes or fails
      - Document specific issues found (quote relevant spec sections)

   c. **Handle Validation Results**:

      - **If all items pass**: Mark checklist complete and proceed to step 6

      - **If items fail (excluding [NEEDS CLARIFICATION])**:
        1. List the failing items and specific issues
        2. Update the spec to address each issue
        3. Re-run validation until all items pass (max 3 iterations)
        4. If still failing after 3 iterations, document remaining issues in checklist notes and warn user

      - **If [NEEDS CLARIFICATION] markers remain**:
        1. Extract all [NEEDS CLARIFICATION: ...] markers from the spec
        2. **LIMIT CHECK**: If more than 3 markers exist, keep only the 3 most critical (by scope/security/UX impact) and make informed guesses for the rest
        3. For each clarification needed (max 3), present options to user in this format:

           ```markdown
           ## Question [N]: [Topic]

           **Context**: [Quote relevant spec section]

           **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]

           **Suggested Answers**:

           | Option | Answer | Implications |
           |--------|--------|--------------|
           | A      | [First suggested answer] | [What this means for the feature] |
           | B      | [Second suggested answer] | [What this means for the feature] |
           | C      | [Third suggested answer] | [What this means for the feature] |
           | Custom | Provide your own answer | [Explain how to provide custom input] |

           **Your choice**: _[Wait for user response]_
           ```

        4. **CRITICAL - Table Formatting**: Ensure markdown tables are properly formatted:
           - Use consistent spacing with pipes aligned
           - Each cell should have spaces around content: `| Content |` not `|Content|`
           - Header separator must have at least 3 dashes: `|--------|`
           - Test that the table renders correctly in markdown preview
        5. Number questions sequentially (Q1, Q2, Q3 - max 3 total)
        6. Present all questions together before waiting for responses
        7. Wait for user to respond with their choices for all questions (e.g., "Q1: A, Q2: Custom - [details], Q3: B")
        8. Update the spec by replacing each [NEEDS CLARIFICATION] marker with the user's selected or provided answer
        9. Re-run validation after all clarifications are resolved

   d. **Update Checklist**: After each validation iteration, update the checklist file with current pass/fail status

7. Report completion with branch name, spec file path, checklist results, and readiness for the next phase (`/sp.clarify` or `/sp.plan`).

**NOTE:** The script creates and checks out the new branch and initializes the spec file before writing.

## General Guidelines

## Quick Guidelines

- Focus on **WHAT** users need and **WHY**.
- Avoid HOW to implement (no tech stack, APIs, code structure).
- Written for business stakeholders, not developers.
- DO NOT create any checklists that are embedded in the spec. That will be a separate command.

### Section Requirements

- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation

When creating this spec from a user prompt:

1. **Make informed guesses**: Use context, industry standards, and common patterns to fill gaps
2. **Document assumptions**: Record reasonable defaults in the Assumptions section
3. **Limit clarifications**: Maximum 3 [NEEDS CLARIFICATION] markers - use only for critical decisions that:
   - Significantly impact feature scope or user experience
   - Have multiple reasonable interpretations with different implications
   - Lack any reasonable default
4. **Prioritize clarifications**: scope > security/privacy > user experience > technical details
5. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
6. **Common areas needing clarification** (only if no reasonable default exists):
   - Feature scope and boundaries (include/exclude specific use cases)
   - User types and permissions (if multiple conflicting interpretations possible)
   - Security/compliance requirements (when legally/financially significant)
   - Integration patterns (when multiple approaches have significantly different implications)

**Examples of reasonable defaults** (don't ask about these):

- Data retention: Industry-standard practices for the domain
- Performance targets: Standard web/mobile app expectations unless specified
- Error handling: User-friendly messages with appropriate fallbacks
- Authentication method: Standard session-based or OAuth2 for web apps
- Integration patterns: RESTful APIs unless specified otherwise

### Success Criteria Guidelines

Success criteria must be:

1. **Measurable**: Include specific metrics (time, percentage, count, rate)
2. **Technology-agnostic**: No mention of frameworks, languages, databases, or tools
3. **User-focused**: Describe outcomes from user/business perspective, not system internals
4. **Verifiable**: Can be tested/validated without knowing implementation details

**Good examples**:

- "Users can complete checkout in under 3 minutes"
- "System supports 10,000 concurrent users"
- "95% of searches return results in under 1 second"
- "Task completion rate improves by 40%"

**Bad examples** (implementation-focused):

- "API response time is under 200ms" (too technical, use "Users see results instantly")
- "Database can handle 1000 TPS" (implementation detail, use user-facing metric)
- "React components render efficiently" (framework-specific)
- "Redis cache hit rate above 80%" (technology-specific)

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

I've successfully created a comprehensive specification for deploying the Todo AI Chatbot application to a local Kubernetes cluster using Minikube, Docker containers, and Helm charts. The specification includes:

- Detailed functional requirements for containerization of both frontend and backend services
- Specifications for Helm chart creation and Kubernetes resource definitions
- Clear acceptance criteria for each requirement
- Non-functional requirements covering performance, security, and reliability
- Success criteria with both quantitative and qualitative measures
- Risk mitigation strategies
- Complete dependency listing

The specification follows the template structure and maintains focus on user value without implementation details. It's ready for the planning phase.

## Outcome

- ✅ Impact: Complete specification created for Kubernetes deployment
- 🧪 Tests: Specification validated with comprehensive checklist
- 📁 Files: spec.md and requirements checklist created
- 🔁 Next prompts: Ready for /sp.plan to create implementation plan
- 🧠 Reflection: Specification covers all aspects of Phase 4 requirements

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All requirements met
- Prompt variant (if applicable): Standard specification creation
- Next experiment (smallest change to try): Create implementation plan from spec