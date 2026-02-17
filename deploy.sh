#!/bin/bash

# Deployment script for Todo Console App to Kubernetes

set -e  # Exit on any error

echo "Starting deployment of Todo Console App to Kubernetes..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "kubectl is required but not installed. Please install kubectl first."
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    echo "Helm is required but not installed. Please install Helm first."
    exit 1
fi

# Check if docker is available
if ! command -v docker &> /dev/null; then
    echo "Docker is required but not installed. Please install Docker first."
    exit 1
fi

# Option to use Minikube or existing Kubernetes cluster
USE_MINIKUBE=${USE_MINIKUBE:-true}

if [ "$USE_MINIKUBE" = true ]; then
    echo "Starting Minikube..."
    
    # Check if minikube is available
    if ! command -v minikube &> /dev/null; then
        echo "Minikube is required but not installed. Please install Minikube first."
        exit 1
    fi
    
    # Start Minikube cluster if not already running
    if ! minikube status &> /dev/null; then
        minikube start --cpus=4 --memory=4096 --driver=docker
    else
        echo "Minikube is already running."
    fi
    
    # Point Docker client to Minikube's Docker daemon
    eval $(minikube docker-env)
fi

echo "Building Docker images..."

# Build frontend image
echo "Building frontend image..."
cd frontend
docker build -t todo-frontend:latest .
cd ..

# Build backend image
echo "Building backend image..."
cd backend
docker build -t todo-backend:latest .
cd ..

# Verify images were created
if [[ "$(docker images -q todo-frontend:latest 2> /dev/null)" == "" ]] || [[ "$(docker images -q todo-backend:latest 2> /dev/null)" == "" ]]; then
    echo "Failed to build Docker images"
    exit 1
fi

echo "Docker images built successfully!"

# Check if Helm release already exists
if helm status todo-app &> /dev/null; then
    echo "Helm release 'todo-app' already exists. Upgrading..."
    helm upgrade todo-app ./k8s/helm/todo-app
else
    echo "Installing Helm chart..."
    # Install the Helm chart with required parameters
    # Note: You need to provide actual database URL and JWT secret
    # For demonstration purposes, we'll use placeholder values
    # In a real deployment, you would use actual values
    echo "Using placeholder values for demonstration. In a real deployment, use actual database URL and JWT secret."
    helm install todo-app ./k8s/helm/todo-app \
        --set backend.secrets.databaseUrl="postgresql://placeholder:placeholder@placeholder-db:5432/placeholddb" \
        --set backend.secrets.jwtSecret="placeholder-jwt-secret-for-demo-purposes-only"
fi

echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-app --timeout=120s

echo "Checking pod status..."
kubectl get pods

echo "Checking services..."
kubectl get services

echo "Deployment completed successfully!"
echo ""
echo "To access the application:"
echo "1. Frontend: kubectl port-forward svc/\$(kubectl get svc -o jsonpath='{.items[?(@.metadata.name==\"*todo-app-frontend\"*])}'.metadata.name) 3000:3000"
echo "2. Backend: kubectl port-forward svc/\$(kubectl get svc -o jsonpath='{.items[?(@.metadata.name==\"*todo-app-backend\"*])}'.metadata.name) 8000:8000"
echo ""
echo "Then visit http://localhost:3000 in your browser to access the Todo Console App."

if [ "$USE_MINIKUBE" = true ]; then
    echo ""
    echo "To access the application in Minikube:"
    echo "minikube service \$(kubectl get svc -o jsonpath='{.items[?(@.metadata.name==\"*todo-app-frontend\"*])}'.metadata.name) --url"
fi