# Kubernetes Deployment for Todo AI Chatbot

This document explains how to deploy the Todo AI Chatbot application to a Kubernetes cluster using Helm charts.

## Prerequisites

- Docker
- Kubernetes cluster (tested with Minikube)
- kubectl
- Helm 3.x

## Architecture

The application consists of two main services:

1. **Frontend** (Next.js):
   - Serves the user interface
   - Communicates with the backend API
   - Runs on port 3000

2. **Backend** (FastAPI):
   - Provides REST API endpoints
   - Connects to Neon PostgreSQL database
   - Runs on port 8000

Both services are deployed as separate deployments with corresponding services in Kubernetes.

## Deployment Steps

### 1. Build Docker Images

First, build the Docker images for both frontend and backend:

```bash
# Build frontend image
docker build -t todo-frontend:latest ./frontend

# Build backend image
docker build -t todo-backend:latest ./backend
```

For Minikube, make sure to use the Minikube Docker environment:

```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Build images
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend
```

### 2. Install Helm Chart

Deploy the application using the Helm chart:

```bash
helm install todo-app ./k8s/helm/todo-app \
  --set backend.secrets.databaseUrl="your-neon-db-url" \
  --set backend.secrets.jwtSecret="your-jwt-secret"
```

### 3. Access the Application

To access the frontend service, run:

```bash
kubectl port-forward svc/todo-app-frontend 3000:3000
```

To access the backend service, run:

```bash
kubectl port-forward svc/todo-app-backend 8000:8000
```

Then visit `http://localhost:3000` in your browser to access the application.

## Configuration

The Helm chart accepts the following values:

### Frontend Configuration
- `frontend.replicaCount` - Number of frontend replicas (default: 1)
- `frontend.image.repository` - Frontend image repository (default: todo-frontend)
- `frontend.image.tag` - Frontend image tag (default: latest)
- `frontend.image.pullPolicy` - Image pull policy (default: IfNotPresent)
- `frontend.service.type` - Service type (default: ClusterIP)
- `frontend.service.port` - Service port (default: 3000)
- `frontend.resources.requests.cpu` - CPU request (default: 100m)
- `frontend.resources.requests.memory` - Memory request (default: 128Mi)
- `frontend.resources.limits.cpu` - CPU limit (default: 500m)
- `frontend.resources.limits.memory` - Memory limit (default: 256Mi)
- `frontend.healthCheck.initialDelaySeconds` - Initial delay for health checks (default: 10)
- `frontend.healthCheck.periodSeconds` - Period for health checks (default: 30)
- `frontend.env.NEXT_PUBLIC_API_URL` - Backend API URL (default: http://todo-backend:8000)

### Backend Configuration
- `backend.replicaCount` - Number of backend replicas (default: 1)
- `backend.image.repository` - Backend image repository (default: todo-backend)
- `backend.image.tag` - Backend image tag (default: latest)
- `backend.image.pullPolicy` - Image pull policy (default: IfNotPresent)
- `backend.service.type` - Service type (default: ClusterIP)
- `backend.service.port` - Service port (default: 8000)
- `backend.resources.requests.cpu` - CPU request (default: 100m)
- `backend.resources.requests.memory` - Memory request (default: 128Mi)
- `backend.resources.limits.cpu` - CPU limit (default: 500m)
- `backend.resources.limits.memory` - Memory limit (default: 256Mi)
- `backend.healthCheck.initialDelaySeconds` - Initial delay for health checks (default: 10)
- `backend.healthCheck.periodSeconds` - Period for health checks (default: 30)
- `backend.config.corsOrigin` - CORS origin (default: *)
- `backend.config.logLevel` - Log level (default: info)
- `backend.config.pythonUnbuffered` - Python unbuffered flag (default: 1)
- `backend.secrets.databaseUrl` - Database URL (required)
- `backend.secrets.jwtSecret` - JWT secret (required)

## Health Checks

Both services include health check endpoints:
- Frontend: `GET /api/health`
- Backend: `GET /health`

These endpoints are used for Kubernetes liveness and readiness probes.

## Troubleshooting

### Pods in CrashLoopBackOff
- Check the logs: `kubectl logs deployment/todo-app-backend`
- Verify the database connection string is correct
- Ensure the database is accessible from the cluster

### Unable to Access Services
- Verify the services are running: `kubectl get svc`
- Check the pods are running: `kubectl get pods`
- Ensure you're using the correct port-forward command

### Database Connection Issues
- Verify the Neon database URL is correctly set in the backend secrets
- Check that the database allows connections from the Kubernetes cluster
- Ensure SSL settings are correct in the connection string

## Scaling

To scale the deployments, you can use:

```bash
# Scale frontend
kubectl scale deployment todo-app-frontend --replicas=3

# Scale backend
kubectl scale deployment todo-app-backend --replicas=2
```

## Cleanup

To remove the deployment:

```bash
helm uninstall todo-app
```

## Development

For local development with Minikube:

1. Start Minikube: `minikube start --driver=docker`
2. Set Docker environment: `eval $(minikube docker-env)`
3. Build images: `docker build -t todo-frontend:latest ./frontend` and `docker build -t todo-backend:latest ./backend`
4. Install Helm chart: `helm install todo-app ./k8s/helm/todo-app --set ...`