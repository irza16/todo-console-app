#!/bin/bash

# Deploy the Todo application to AKS

echo "Deploying Todo application to AKS..."

# Create the secrets (using dummy values for now - would need real values in production)
kubectl create secret generic todo-app-secrets \
  --from-literal=database-url="postgresql://username:password@neon-db-url.com/dbname" \
  --from-literal=jwt-secret="supersecretjwtkey" \
  --save-config --dry-run=client -o yaml | kubectl apply -f -

# Deploy via Helm
helm upgrade --install todo-app ./k8s/helm/todo-app \
  --set images.registry=todoappcr12345.azurecr.io \
  --set images.frontend.tag=v5.0 \
  --set images.backend.tag=v5.0 \
  --set images.reminderService.tag=v5.0 \
  --set images.recurringService.tag=v5.0 \
  --timeout 10m

echo "Deployment initiated. Checking status..."
kubectl get pods