# Quick Start Guide: Todo AI Chatbot on Kubernetes

## Prerequisites
- Docker
- Minikube
- kubectl
- Helm 3.x

## Setup Instructions

### 1. Start Minikube
```bash
minikube start --driver=docker --cpus=2 --memory=2048mb
```

### 2. Set Docker Environment
```bash
eval $(minikube docker-env)
```

### 3. Build Docker Images
```bash
# Build frontend
docker build -t todo-frontend:latest /home/irza/projects/todo-console-app/frontend

# Build backend
docker build -t todo-backend:latest /home/irza/projects/todo-console-app/backend
```

### 4. Deploy with Helm
```bash
helm install todo-app /home/irza/projects/todo-console-app/k8s/helm/todo-app \
  --set backend.secrets.databaseUrl="YOUR_NEON_DB_URL" \
  --set backend.secrets.jwtSecret="YOUR_JWT_SECRET"
```

### 5. Access the Application
```bash
# Get the frontend service IP
minikube service todo-app-frontend --url

# Or port-forward for local access
kubectl port-forward svc/todo-app-frontend 3000:3000
```

Visit `http://localhost:3000` to access the application.

## Verification Commands
```bash
# Check pods
kubectl get pods

# Check services
kubectl get svc

# Check logs
kubectl logs deployment/todo-app-frontend
kubectl logs deployment/todo-app-backend
```

## Troubleshooting
- If pods are not starting, check logs with `kubectl logs <pod-name>`
- If you can't access the service, try `minikube tunnel` in a separate terminal
- For database connection issues, verify your Neon database URL and credentials