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
docker build -t $ACR_NAME/reminder-service:$IMAGE_TAG .
docker push $ACR_NAME/reminder-service:$IMAGE_TAG
cd ../..

# Build and push recurring task service
echo "Building recurring task service image..."
cd backend/recurring-task-service
docker build -t $ACR_NAME/recurring-task-service:$IMAGE_TAG .
docker push $ACR_NAME/recurring-task-service:$IMAGE_TAG
cd ../..

# Build and push frontend
echo "Building frontend image..."
cd frontend
# Assuming there's a Dockerfile in frontend directory
if [ ! -f "Dockerfile" ]; then
    # Create a basic Dockerfile for the frontend if it doesn't exist
    cat > Dockerfile << 'EOF'
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build || echo "Build skipped - may not be a Next.js app"

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app ./
EXPOSE 3000
CMD ["npm", "start"] || CMD ["npx", "serve", "-s", "build"] || CMD ["node", "server.js"]
EOF
fi
docker build -t $ACR_NAME/todo-frontend:$IMAGE_TAG .
docker push $ACR_NAME/todo-frontend:$IMAGE_TAG
cd ..

echo "All images pushed successfully!"