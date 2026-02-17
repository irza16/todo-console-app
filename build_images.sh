#!/bin/bash

# Script to build Docker images for Minikube

# Set Docker environment to use Minikube's Docker daemon
eval $(minikube docker-env)

echo "Building frontend Docker image..."
cd /home/irza/projects/todo-console-app/frontend
docker build -t todo-frontend:latest .

echo "Building backend Docker image..."
cd /home/irza/projects/todo-console-app/backend
docker build -t todo-backend:latest .

echo "Images built successfully!"
docker images | grep todo