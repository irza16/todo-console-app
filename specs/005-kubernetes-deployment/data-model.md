# Data Models for Kubernetes Deployment

## Kubernetes Resources

### Frontend Deployment Entity
- **Name**: todo-frontend
- **Type**: Kubernetes Deployment
- **Fields**:
  - replicas: configurable via Helm values (default: 1)
  - image: configurable via Helm values (default: todo-frontend:latest)
  - resources: configurable via Helm values (requests/limits for CPU/Memory)
  - environment: from ConfigMap and direct assignment
  - ports: containerPort 3000
  - health checks: liveness and readiness probes to /api/health
- **Validation**:
  - replicas must be >= 1 and <= 10
  - image tag must follow semantic versioning or "latest"
  - resource limits must be >= requests

### Backend Deployment Entity
- **Name**: todo-backend
- **Type**: Kubernetes Deployment
- **Fields**:
  - replicas: configurable via Helm values (default: 1)
  - image: configurable via Helm values (default: todo-backend:latest)
  - resources: configurable via Helm values (requests/limits for CPU/Memory)
  - environment: from ConfigMap and Secrets
  - ports: containerPort 8000
  - health checks: liveness and readiness probes to /health
- **Validation**:
  - replicas must be >= 1 and <= 10
  - image tag must follow semantic versioning or "latest"
  - resource limits must be >= requests

### Frontend Service Entity
- **Name**: todo-frontend
- **Type**: Kubernetes Service
- **Fields**:
  - name: configurable via Helm values (default: todo-frontend)
  - type: configurable via Helm values (default: ClusterIP)
  - port: configurable via Helm values (default: 3000)
  - targetPort: 3000
  - selector: app=todo-frontend
- **Validation**:
  - port must be in range 1-65535
  - service type must be ClusterIP, NodePort, or LoadBalancer

### Backend Service Entity
- **Name**: todo-backend
- **Type**: Kubernetes Service
- **Fields**:
  - name: configurable via Helm values (default: todo-backend)
  - type: configurable via Helm values (default: ClusterIP)
  - port: configurable via Helm values (default: 8000)
  - targetPort: 8000
  - selector: app=todo-backend
- **Validation**:
  - port must be in range 1-65535
  - service type must be ClusterIP, NodePort, or LoadBalancer

### Frontend ConfigMap Entity
- **Name**: frontend-config
- **Type**: Kubernetes ConfigMap
- **Fields**:
  - name: configurable via Helm values (default: frontend-config)
  - data: NEXT_PUBLIC_API_URL, NODE_ENV
- **Validation**:
  - NEXT_PUBLIC_API_URL must be a valid URL
  - NODE_ENV must be "development", "production", or "test"

### Backend ConfigMap Entity
- **Name**: backend-config
- **Type**: Kubernetes ConfigMap
- **Fields**:
  - name: configurable via Helm values (default: backend-config)
  - data: CORS_ORIGIN, LOG_LEVEL, PYTHONUNBUFFERED
- **Validation**:
  - CORS_ORIGIN must be a valid URL or "*"
  - LOG_LEVEL must be "debug", "info", "warning", "error", or "critical"
  - PYTHONUNBUFFERED must be "0" or "1"

### Backend Secret Entity
- **Name**: backend-secrets
- **Type**: Kubernetes Secret
- **Fields**:
  - name: configurable via Helm values (default: backend-secrets)
  - data: database-url, jwt-secret
- **Validation**:
  - database-url must be a valid PostgreSQL connection string
  - jwt-secret must be at least 32 characters long