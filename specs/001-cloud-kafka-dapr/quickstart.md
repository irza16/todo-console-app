# Quickstart Guide: Cloud Deployment with Kafka & Dapr

## Prerequisites
- Azure account with active subscription
- Azure CLI installed and logged in
- Docker installed and running
- kubectl installed
- Helm 3.x installed
- Dapr CLI installed

## Setup Steps

### 1. Clone and Navigate to Repository
```bash
git clone [repo-url]
cd todo-console-app
git checkout 001-cloud-kafka-dapr
```

### 2. Set Up Azure Resources
```bash
# Create resource group
az group create --name todo-app-rg --location eastus

# Create AKS cluster (cost-optimized for demo)
az aks create \
  --resource-group todo-app-rg \
  --name todo-aks-cluster \
  --node-count 1 \
  --node-vm-size Standard_B1s \
  --enable-managed-identity \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --kubernetes-version 1.28

# Get credentials
az aks get-credentials --resource-group todo-app-rg --name todo-aks-cluster
```

### 3. Set Up Container Registry
```bash
# Create ACR
az acr create --resource-group todo-app-rg --name todoappcr --sku Basic

# Attach ACR to AKS
az aks update --resource-group todo-app-rg --name todo-aks-cluster --attach-acr todoappcr
```

### 4. Install Dapr
```bash
# Install Dapr on AKS
dapr init --kubernetes --wait

# Verify installation
kubectl get pods -n dapr-system
```

### 5. Deploy Kafka
```bash
# Add Bitnami chart repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Deploy Kafka
helm install kafka bitnami/kafka \
  --namespace kafka --create-namespace \
  --set replicaCount=1 \
  --set persistence.size=10Gi \
  --set deleteTopicEnable=true

# Create Kafka topics
kubectl run kafka-client --restart='Never' --image docker.io/bitnami/kafka:3.6.0 \
  --command -- sleep infinity

kubectl exec -it kafka-client -- kafka-topics.sh --create \
  --bootstrap-server kafka.kafka.svc.cluster.local:9092 \
  --topic task-events --partitions 3 --replication-factor 1

kubectl exec -it kafka-client -- kafka-topics.sh --create \
  --bootstrap-server kafka.kafka.svc.cluster.local:9092 \
  --topic reminder-events --partitions 3 --replication-factor 1

kubectl exec -it kafka-client -- kafka-topics.sh --create \
  --bootstrap-server kafka.kafka.svc.cluster.local:9092 \
  --topic task-updates --partitions 3 --replication-factor 1
```

### 6. Build and Push Docker Images
```bash
# Login to ACR
az acr login --name todoappcr

# Build and push frontend
cd frontend
docker build -t todoappcr.azurecr.io/todo-frontend:v5.0 .
docker push todoappcr.azurecr.io/todo-frontend:v5.0

# Build and push backend
cd ../backend
docker build -t todoappcr.azurecr.io/todo-backend:v5.0 .
docker push todoappcr.azurecr.io/todo-backend:v5.0

# Build and push reminder service
cd reminder-service
docker build -t todoappcr.azurecr.io/reminder-service:v5.0 .
docker push todoappcr.azurecr.io/reminder-service:v5.0

# Build and push recurring task service
cd ../recurring-task-service
docker build -t todoappcr.azurecr.io/recurring-task-service:v5.0 .
docker push todoappcr.azurecr.io/recurring-task-service:v5.0
```

### 7. Deploy Application
```bash
# Create Kubernetes secrets for database connection
kubectl create secret generic todo-app-secrets \
  --from-literal=database-url="your-neon-db-url" \
  --from-literal=jwt-secret="your-jwt-secret"

# Apply Dapr components
kubectl apply -f k8s/dapr-components/

# Deploy application with Helm
helm install todo-app ./k8s/helm/todo-app
```

### 8. Verify Deployment
```bash
# Check all pods are running
kubectl get pods

# Get frontend public IP
kubectl get svc todo-app-frontend

# Test the application
curl http://[PUBLIC_IP]:8000/api/health
```

## Cost Management
```bash
# To stop cluster after demo (preserves configuration)
az aks stop --resource-group todo-app-rg --name todo-aks-cluster

# To restart cluster
az aks start --resource-group todo-app-rg --name todo-aks-cluster

# To delete all resources
az group delete --name todo-app-rg --yes
```

## Local Development Setup
```bash
# For local development with Dapr and Kafka
# Run Kafka locally
docker run -d --name kafka-local -p 9092:9092 bitnami/kafka:latest

# Initialize Dapr locally
dapr init

# Run services with Dapr
cd backend
dapr run --app-id backend --app-port 8000 -- uvicorn app.main:app

cd ../frontend
npm run dev
```

## Troubleshooting
- If pods are pending: Check resource limits, consider scaling up nodes
- If Kafka is not connecting: Verify service names and ports
- If Dapr is not working: Check component configurations
- If services are not connecting: Verify network policies and service discovery