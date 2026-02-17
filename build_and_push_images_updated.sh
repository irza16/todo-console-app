#!/bin/bash

# Build and push Docker images to ACR

ACR_NAME="todoappcr12345.azurecr.io"
IMAGE_TAG="v5.0"

# Login to ACR
echo "Logging into ACR..."
az acr login --name todoappcr12345

# Build and push backend
echo "Building backend image..."
cd backend
docker build -t $ACR_NAME/todo-backend:$IMAGE_TAG .
docker push $ACR_NAME/todo-backend:$IMAGE_TAG
cd ..

# Build and push reminder service
echo "Building reminder service image..."
cd backend/reminder-service
docker build -f Dockerfile -t $ACR_NAME/reminder-service:$IMAGE_TAG .
docker push $ACR_NAME/reminder-service:$IMAGE_TAG
cd ../..

# Build and push recurring task service
echo "Building recurring task service image..."
cd backend/recurring-task-service
docker build -f Dockerfile -t $ACR_NAME/recurring-task-service:$IMAGE_TAG .
docker push $ACR_NAME/recurring-task-service:$IMAGE_TAG
cd ../..

# Build and push frontend
echo "Building frontend image..."
cd frontend
docker build -t $ACR_NAME/todo-frontend:$IMAGE_TAG .
docker push $ACR_NAME/todo-frontend:$IMAGE_TAG
cd ..

echo "All images pushed successfully!"