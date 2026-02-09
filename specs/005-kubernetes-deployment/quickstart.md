# Quickstart Guide: Kubernetes Deployment

## Prerequisites

- Docker Desktop with Kubernetes enabled OR Minikube
- Helm 3.x
- kubectl
- Access to Neon PostgreSQL database
- Git

## Setup Instructions

### 1. Clone and Prepare Repository
```bash
# Clone the repository
git clone <repository-url>
cd <repository-directory>

# If using Minikube, start the cluster
minikube start --cpus=4 --memory=4096 --driver=docker
```

### 2. Build Docker Images
```bash
# Set Docker to point to Minikube registry (if using Minikube)
eval $(minikube docker-env)

# Build frontend image
cd frontend
docker build -t todo-frontend:latest .

# Build backend image
cd ../backend
docker build -t todo-backend:latest .

# Verify images were created
docker images | grep todo-
```

### 3. Install Helm Chart
```bash
# Navigate to Helm chart directory
cd ../k8s/helm/todo-app

# Install with your database credentials
# Replace with your actual Neon database URL and a secure JWT secret
helm install todo-app . \
  --set backend.secrets.databaseUrl="postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require" \
  --set backend.secrets.jwtSecret="a-very-long-and-secure-random-string-at-least-32-characters-long"
```

### 4. Verify Installation
```bash
# Check all pods are running
kubectl get pods

# Check services are available
kubectl get services

# Check the status of the Helm release
helm status todo-app
```

## Accessing the Application

### 1. Port Forward to Access the Frontend
```bash
# Port forward the frontend service
kubectl port-forward service/todo-frontend 3000:3000
```

### 2. Open Browser
Navigate to http://localhost:3000 in your browser

## Verification Steps

### 1. Check Pod Status
```bash
# All pods should show "Running" status
kubectl get pods

# Check for any restarts (should be 0)
kubectl get pods --sort-by=.status.containerStatuses[0].restartCount
```

### 2. Check Application Logs
```bash
# Check frontend logs
kubectl logs deployment/todo-frontend

# Check backend logs
kubectl logs deployment/todo-backend
```

### 3. Test Health Endpoints
```bash
# Get pod names
kubectl get pods

# Test frontend health (replace POD_NAME with actual pod name)
kubectl exec -it <frontend-pod-name> -- curl http://localhost:3000/api/health

# Test backend health (replace POD_NAME with actual pod name)
kubectl exec -it <backend-pod-name> -- curl http://localhost:8000/health
```

## Troubleshooting

### Pods in CrashLoopBackOff
```bash
# Check pod description for errors
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

### Service Unavailable
```bash
# Check if service exists
kubectl get services

# Check endpoints
kubectl get endpoints todo-frontend
kubectl get endpoints todo-backend
```

### Database Connection Issues
```bash
# Exec into backend pod
kubectl exec -it <backend-pod-name> -- /bin/bash

# Inside the pod, test database connection
python -c "import os; print(os.environ.get('DATABASE_URL'))"
```

## Cleanup

### Uninstall Helm Release
```bash
helm uninstall todo-app
```

### Stop Minikube (if used)
```bash
minikube stop
```

## Advanced Configuration

### Override Default Values
Create a custom values file:
```bash
# Create custom-values.yaml
cat << EOF > custom-values.yaml
frontend:
  replicaCount: 2
  resources:
    requests:
      memory: "256Mi"
      cpu: "500m"
    limits:
      memory: "512Mi"
      cpu: "1000m"
backend:
  replicaCount: 2
  resources:
    requests:
      memory: "512Mi"
      cpu: "1000m"
    limits:
      memory: "1Gi"
      cpu: "2000m"
EOF

# Install with custom values
helm install todo-app . -f custom-values.yaml \
  --set backend.secrets.databaseUrl="your-db-url" \
  --set backend.secrets.jwtSecret="your-jwt-secret"
```

### Enable NodePort for Direct Access
```bash
# Install with NodePort service type
helm install todo-app . \
  --set frontend.service.type=NodePort \
  --set backend.secrets.databaseUrl="your-db-url" \
  --set backend.secrets.jwtSecret="your-jwt-secret"

# Get the NodePort URL
minikube service todo-frontend --url
```