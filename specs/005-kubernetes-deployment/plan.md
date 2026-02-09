# Phase 4 Plan: Kubernetes Deployment Architecture

## 1. Technical Context

### 1.1 Feature Overview
- **Feature Name**: Kubernetes Deployment for Todo AI Chatbot
- **Feature ID**: 005-kubernetes-deployment
- **Specification Path**: `specs/005-kubernetes-deployment/spec.md`
- **Implementation Plan Path**: `specs/005-kubernetes-deployment/plan.md`
- **Branch**: `005-kubernetes-deployment`

### 1.2 Current State Analysis
The application consists of a frontend Next.js application and a backend FastAPI application that currently run in a local development environment or deployed separately on Vercel and Koyeb. The Neon PostgreSQL database is already external and will remain so during the Kubernetes deployment.

### 1.3 Target State
The application will be deployed to a local Minikube cluster using Docker containers and Helm charts, maintaining the existing two-service architecture (frontend + backend) while introducing container orchestration and declarative configuration management.

### 1.4 Architecture Overview
- **Frontend**: Next.js application containerized with multi-stage Docker build
- **Backend**: FastAPI application containerized with multi-stage Docker build
- **Database**: External Neon PostgreSQL (remains unchanged)
- **Orchestration**: Kubernetes via Minikube
- **Configuration**: Helm charts for declarative deployments
- **Service Discovery**: Internal communication via Kubernetes DNS

### 1.5 Technology Stack
- **Containerization**: Docker (multi-stage builds)
- **Orchestration**: Kubernetes (Minikube for local)
- **Packaging**: Helm charts
- **Frontend Base Image**: node:20-alpine
- **Backend Base Image**: python:3.13-slim
- **Health Checks**: HTTP endpoints for liveness/readiness probes

### 1.6 Known Unknowns
- **NEEDS CLARIFICATION**: Actual database connection string for Neon PostgreSQL
- **NEEDS CLARIFICATION**: JWT secret value for authentication
- **NEEDS CLARIFICATION**: Current application source code structure for health check implementation
- **NEEDS CLARIFICATION**: Exact environment variables required by the frontend and backend applications

## 2. Constitution Check

Based on the project constitution (version 4.0.0), the following principles apply:

### 2.1 Compliance Check
- ✅ **Spec-Driven Development with Subagent Orchestration**: Following the spec created in the previous step
- ✅ **Multi-User Architecture**: Maintaining existing user isolation patterns
- ✅ **Type-Safe Full-Stack**: Preserving existing TypeScript/Python type safety
- ✅ **Secure by Default**: Using Kubernetes Secrets for sensitive data
- ✅ **Production-Ready Patterns**: Including health checks, resource limits, etc.
- ✅ **Conversational AI-First Interface**: Maintaining existing AI features
- ✅ **MCP (Model Context Protocol) Architecture**: Preserving existing MCP functionality
- ✅ **Backward Compatibility**: Ensuring all Phase 3 functionality remains
- ✅ **Cloud-Native Architecture**: Containerizing applications as required
- ✅ **Separation of Concerns**: Deploying frontend and backend as separate services
- ✅ **Reproducibility and Portability**: Using multi-stage builds and Helm charts
- ✅ **Security First**: Running containers as non-root users, using secrets properly
- ✅ **Observability and Debugging**: Including health checks and proper logging

### 2.2 Potential Violations
None identified - all constitutional principles are supported by this architecture plan.

## 3. Implementation Gates

### 3.1 Security Gate
- **Pass**: Containers will run as non-root users
- **Pass**: Secrets will be managed via Kubernetes Secrets
- **Pass**: No hardcoded credentials in Docker images
- **Pass**: Health checks will be implemented for both services

### 3.2 Performance Gate
- **Pass**: Resource requests and limits defined for both deployments
- **Pass**: Multi-stage Docker builds will optimize image sizes
- **Pass**: Health checks will monitor service readiness/liveness

### 3.3 Scalability Gate
- **Pass**: Deployments will be configurable via Helm values
- **Pass**: Service discovery via Kubernetes DNS enables scaling

### 3.4 Maintainability Gate
- **Pass**: Helm charts provide declarative configuration
- **Pass**: Clear separation of frontend and backend services
- **Pass**: Documentation and troubleshooting guides planned

## 4. Phase 0: Research

### 4.1 Research Tasks

#### 4.1.1 Database Connection Research
**Task**: Research how to properly configure the Neon PostgreSQL connection for Kubernetes deployment
**Objective**: Obtain the correct database connection string format for the external Neon database

#### 4.1.2 JWT Secret Configuration Research
**Task**: Research how JWT authentication is currently implemented in the application
**Objective**: Determine the proper format and requirements for the JWT secret

#### 4.1.3 Application Health Check Research
**Task**: Research the current application structure to implement health check endpoints
**Objective**: Understand where to add health check endpoints in both frontend and backend

#### 4.1.4 Environment Variables Research
**Task**: Research the environment variables currently used by the applications
**Objective**: Determine all required environment variables for both frontend and backend

#### 4.1.5 Docker Best Practices Research
**Task**: Research best practices for multi-stage Docker builds for Next.js and FastAPI
**Objective**: Optimize Docker images for size and security

### 4.2 Research Findings

#### 4.2.1 Database Connection Implementation
**Decision**: Use the existing Neon PostgreSQL connection string with SSL enforcement
**Rationale**: Neon requires SSL connections, which is already implemented in the current application
**Implementation**: Store the connection string in a Kubernetes Secret and mount it as an environment variable in the backend container

#### 4.2.2 JWT Secret Configuration
**Decision**: Generate a secure random JWT secret and store in Kubernetes Secret
**Rationale**: Security best practice requires strong secrets that are not hardcoded
**Implementation**: Use Helm templating to allow users to provide their own secret during installation

#### 4.2.3 Health Check Endpoints
**Decision**: Implement simple health check endpoints in both applications
**Rationale**: Kubernetes liveness and readiness probes require HTTP endpoints to monitor container health
**Implementation**:
- Frontend: `GET /api/health` returning 200 with status information
- Backend: `GET /health` returning 200 with status information

#### 4.2.4 Environment Variables Identification
**Decision**: Map all required environment variables from current application
**Rationale**: Applications need proper configuration to handle requests in the Kubernetes environment
**Implementation**:
- Frontend: NEXT_PUBLIC_API_URL (from ConfigMap)
- Backend: DATABASE_URL (from Secret), JWT_SECRET (from Secret), CORS_ORIGIN (from ConfigMap)

#### 4.2.5 Docker Optimization
**Decision**: Use multi-stage builds with Alpine base images
**Rationale**: Reduces image size and attack surface
**Implementation**:
- Frontend: node:20-alpine base (~450MB target)
- Backend: python:3.13-slim base (~300MB target)
- Both: Non-root users for security

## 5. Phase 1: Design & Contracts

### 5.1 Data Model for Kubernetes Resources

#### 5.1.1 Frontend Deployment Entity
- **Name**: todo-frontend
- **Type**: Kubernetes Deployment
- **Fields**:
  - replicas: configurable via Helm values (default: 1)
  - image: configurable via Helm values (default: todo-frontend:latest)
  - resources: configurable via Helm values (requests/limits for CPU/Memory)
  - environment: from ConfigMap and direct assignment
  - ports: containerPort 3000
  - health checks: liveness and readiness probes to /api/health

#### 5.1.2 Backend Deployment Entity
- **Name**: todo-backend
- **Type**: Kubernetes Deployment
- **Fields**:
  - replicas: configurable via Helm values (default: 1)
  - image: configurable via Helm values (default: todo-backend:latest)
  - resources: configurable via Helm values (requests/limits for CPU/Memory)
  - environment: from ConfigMap and Secrets
  - ports: containerPort 8000
  - health checks: liveness and readiness probes to /health

#### 5.1.3 Service Entities
- **Frontend Service**:
  - name: todo-frontend
  - type: configurable via Helm values (default: ClusterIP)
  - port: configurable via Helm values (default: 3000)
  - targetPort: 3000

- **Backend Service**:
  - name: todo-backend
  - type: configurable via Helm values (default: ClusterIP)
  - port: configurable via Helm values (default: 8000)
  - targetPort: 8000

#### 5.1.4 ConfigMap Entities
- **Frontend ConfigMap**:
  - name: frontend-config
  - data: NEXT_PUBLIC_API_URL, NODE_ENV

- **Backend ConfigMap**:
  - name: backend-config
  - data: CORS_ORIGIN, LOG_LEVEL, PYTHONUNBUFFERED

#### 5.1.5 Secret Entities
- **Backend Secret**:
  - name: backend-secrets
  - data: database-url, jwt-secret

### 5.2 API Contract Definitions

#### 5.2.1 Health Check Endpoints
- **Frontend Health Endpoint**:
  - Method: GET
  - Path: /api/health
  - Response: 200 OK with JSON payload { "status": "healthy", "timestamp": "ISO8601" }

- **Backend Health Endpoint**:
  - Method: GET
  - Path: /health
  - Response: 200 OK with JSON payload { "status": "healthy", "timestamp": "ISO8601" }

#### 5.2.2 Internal Service Communication
- **Frontend to Backend**:
  - Host: todo-backend (Kubernetes service name)
  - Port: 8000
  - Protocol: HTTP/HTTPS
  - API: Existing REST API endpoints

### 5.3 Quickstart Guide for Developers

#### 5.3.1 Prerequisites
- Docker Desktop with Kubernetes enabled OR Minikube
- Helm 3.x
- kubectl
- Access to Neon PostgreSQL database

#### 5.3.2 Setup Instructions
1. Clone the repository
2. Navigate to the project directory
3. Start Minikube: `minikube start --cpus=4 --memory=4096 --driver=docker`
4. Build Docker images:
   ```bash
   # Set Docker to point to Minikube registry
   eval $(minikube docker-env)

   # Build frontend image
   cd frontend
   docker build -t todo-frontend:latest .

   # Build backend image
   cd ../backend
   docker build -t todo-backend:latest .
   ```
5. Install Helm chart:
   ```bash
   # Navigate to Helm chart directory
   cd ../k8s/helm/todo-app

   # Install with your database credentials
   helm install todo-app . \
     --set backend.secrets.databaseUrl="your-neon-db-url" \
     --set backend.secrets.jwtSecret="your-jwt-secret"
   ```

#### 5.3.3 Accessing the Application
1. Port forward the frontend service:
   ```bash
   kubectl port-forward service/todo-frontend 3000:3000
   ```
2. Open browser to http://localhost:3000

#### 5.3.4 Verification Steps
1. Check all pods are running:
   ```bash
   kubectl get pods
   ```
2. Check services are available:
   ```bash
   kubectl get services
   ```
3. Check application logs:
   ```bash
   kubectl logs deployment/todo-frontend
   kubectl logs deployment/todo-backend
   ```

## 6. Implementation Plan Summary

### 6.1 Phase 2 Preparation
The next phase will involve creating the actual Dockerfiles, Kubernetes resource templates, and Helm chart based on the designs outlined above. The implementation will follow the architecture plan with attention to security, performance, and maintainability requirements.

### 6.2 Key Deliverables
1. Dockerfiles for frontend and backend applications
2. Kubernetes resource definitions (Deployments, Services, ConfigMaps, Secrets)
3. Helm chart with proper templating and default values
4. Health check implementations in both applications
5. Documentation for deployment and troubleshooting

### 6.3 Success Criteria Validation
- Docker images build successfully and meet size requirements
- Kubernetes resources deploy without errors
- All pods reach Running state with 0 restarts
- Application functions identically to Phase 3
- Health checks respond appropriately
- Helm chart passes validation
- Documentation is complete and accurate