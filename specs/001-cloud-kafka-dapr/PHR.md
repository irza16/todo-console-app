# Phase 5 Plan: Cloud Deployment Architecture with Kafka & Dapr

## Executive Summary

Deploy Todo AI Chatbot to Azure AKS with event-driven microservices using Kafka and Dapr. The solution includes priority and tag enhancements for tasks, search and filtering capabilities, automated reminders, and recurring task functionality. The architecture consists of four services (frontend, backend API, reminder service, and recurring task service) communicating through Kafka event streams managed by Dapr. The deployment is optimized for cost efficiency using B1s nodes during the hackathon demo period, with total costs under $5 for the 7-day demonstration period.

## Architecture Evolution

### Current (Phase 4 - Minikube)
```
Minikube → Frontend (Next.js) → Backend (FastAPI) → Neon DB
```

### Target (Phase 5 - Azure AKS)
```
Azure AKS
├── Frontend (LoadBalancer - Public IP)
├── Backend API (publishes events)
├── Kafka Event Bus
│   └── Topics: task-events, reminder-events
├── Reminder Service (consumes events)
└── Recurring Task Service (consumes events)

External: Neon DB, ACR, Azure Monitor
```

## Key Components

### 1. Azure Infrastructure (COST-OPTIMIZED)
- **AKS Cluster:** 1 node (Standard_B1s: 1 vCPU, 1GB RAM)
- **ACR:** Container registry (Basic tier)
- **Load Balancer:** Public IP for frontend
- **Monitor:** Logging and metrics
- **Daily Cost:** $0.65/day = $4.55/week

### 2. Services (4 total)
1. **Frontend:** Next.js UI
2. **Backend API:** FastAPI + event publishing
3. **Reminder Service:** Sends notifications
4. **Recurring Task Service:** Auto-creates tasks

### 3. Event Streaming
- **Kafka:** Self-hosted (Bitnami Helm)
- **Topics:** task-events, reminder-events, task-updates
- **Dapr:** Simplifies pub/sub

## Data Flows

### Create Task with Reminder
```
User → Frontend → Backend
                    ├─> Save to DB
                    └─> Publish task.created event
                          └─> Kafka
                                └─> Reminder Service
                                      └─> Schedule reminder
                                            └─> (1hr before) Publish reminder.due
```

### Complete Recurring Task
```
User → Frontend → Backend
                    ├─> Mark complete in DB
                    └─> Publish task.completed event
                          └─> Kafka
                                └─> Recurring Task Service
                                      ├─> Calculate next occurrence
                                      └─> Publish task.created event
                                            └─> Backend saves new task
```

## Deployment Workflow

### Phase 1: Local Testing
```bash
# Run Kafka locally
docker run -d bitnami/kafka

# Run services with Dapr
dapr run --app-id backend -- uvicorn app.main:app
dapr run --app-id reminder -- uvicorn app.main:app
```

### Phase 2: Build Images
```bash
# Build and push to ACR
docker build -t todoappcr.azurecr.io/todo-backend:v5.0 ./backend
az acr login --name todoappcr
docker push todoappcr.azurecr.io/todo-backend:v5.0
```

### Phase 3: Deploy to AKS
```bash
# Install Dapr
dapr init --kubernetes

# Deploy Kafka
helm install kafka bitnami/kafka

# Deploy app
helm install todo-app ./k8s/helm/todo-app
```

### Phase 4: Verify
```bash
# Get public IP
kubectl get svc todo-app-frontend

# Test
curl http://<PUBLIC-IP>/api/health
```

## New Features Implementation

### Priority & Tags
```sql
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10);
ALTER TABLE tasks ADD COLUMN tags TEXT[];
```

### Search & Filter
```python
@router.get("/search")
async def search_tasks(q: str, priority: str, tags: List[str]):
    # Search in title/description
    # Filter by priority/tags
```

### Reminders
```python
# Reminder Service
@app.post("/task-events")
async def handle_event(event):
    if event["due_date"]:
        schedule_reminder(event)
```

### Recurring Tasks
```python
# Recurring Task Service
@app.post("/task-events")
async def handle_event(event):
    if event["is_recurring"]:
        create_next_occurrence(event)
```

## Monitoring

### Logs
```bash
# View logs
kubectl logs -l app=todo-backend

# Azure Portal
Monitoring > Logs > ContainerLog
```

### Metrics
```bash
# Resource usage
kubectl top pods

# Custom metrics (future)
- API latency
- Event processing time
```

## Security

### Secrets
```bash
# Store in Kubernetes
kubectl create secret generic todo-secrets \
  --from-literal=database-url=$DB_URL
```

### Network
- Backend: ClusterIP (internal only)
- Frontend: LoadBalancer (public)
- Kafka: ClusterIP (internal)

## Cost Optimization & Demo Strategy

### Optimized Configuration (Hackathon Demo)

| Resource | Original | Optimized | Daily Cost |
|----------|----------|-----------|------------|
| AKS Nodes | 2x B2s ($35 each) | 1x B1s | $0.33 |
| ACR | Basic ($5/mo) | Basic | $0.16 |
| Load Balancer | $5/mo | Single IP | $0.16 |
| Bandwidth | < 5GB | Free | $0.00 |
| **TOTAL** | **$80/month** | **$0.65/day** | **$4.55/week** |

### Demo Timeline (Minimal Cost)

**Day 1-5: Local Development ($0)**
- Work locally with Minikube/Docker
- Test all services with local Kafka + Dapr
- Build and test Docker images
- Cost: $0 (no Azure resources yet)

**Day 6: Deploy to Azure ($0.65)**
- Morning: Create AKS cluster (B1s)
- Afternoon: Deploy all services
- Evening: Test everything works
- Cost: $0.65

**Day 7: Demo Recording ($0.65)**
- Morning: Final testing and bug fixes
- Afternoon: Record demo video
- Evening: Submit to hackathon
- Cost: $0.65
- **Running total: $1.30**

**Day 8: Stop or Delete**

**Option A - Stop Cluster (Recommended):**
```bash
az aks stop --resource-group todo-app-rg --name todo-aks-cluster
```
- Keeps all configuration intact
- Can restart in minutes
- Cost: $1/month (storage only)
- Perfect for showing employers later

**Option B - Delete Everything:**
```bash
az group delete --name todo-app-rg --yes
```
- Removes all resources
- Cost: $0/month
- Can redeploy from GitHub later (30 min)

**Total Cost for Hackathon:**
- 7 days deployment: $4.55
- OR stop after 2 days: $1.30
- **Remaining credit: $95-98 for future projects!**

### Resource Limits for B1s

**B1s Node Capacity:**
- CPU: 1000m (1 vCPU)
- Memory: 1024Mi (1GB)
- Available after system pods: ~700m CPU, ~700Mi memory

**Pod Resource Allocation (fits on 1x B1s):**
```yaml
frontend:
  requests: {memory: 128Mi, cpu: 100m}
  limits: {memory: 256Mi, cpu: 250m}

backend:
  requests: {memory: 256Mi, cpu: 200m}
  limits: {memory: 512Mi, cpu: 500m}

reminderService:
  requests: {memory: 64Mi, cpu: 50m}
  limits: {memory: 128Mi, cpu: 100m}

recurringTaskService:
  requests: {memory: 64Mi, cpu: 50m}
  limits: {memory: 128Mi, cpu: 100m}

# Total requests: 512Mi memory, 400m CPU ✓ Fits!
```

### Parallel Deployments

**Keep Phase 3 Running (Vercel + Hugging Face):**
```
Phase 3 (FREE - Keep Forever):
├── Frontend: todo-console-app-orcin.vercel.app
├── Backend: huggingface.co/spaces/your-space
└── Database: Neon PostgreSQL

Phase 5 (Azure - Demo Only):
├── Frontend: http://<azure-public-ip>
├── Backend: In AKS cluster
├── Services: In AKS cluster
└── Database: SAME Neon PostgreSQL (shared)
```

**Benefits:**
- Phase 3 proves you completed it (runs free forever)
- Phase 5 shows advanced cloud skills
- Both use same database
- Delete Phase 5 after demo, keep Phase 3

## Pre-Deployment Testing (Save Money!)

**Test EVERYTHING locally BEFORE deploying to Azure:**

```bash
# 1. Run Kafka locally
docker run -d --name kafka-local -p 9092:9092 bitnami/kafka:latest

# 2. Initialize Dapr
dapr init

# 3. Test each service with Dapr
cd backend
dapr run --app-id backend --app-port 8000 -- uvicorn app.main:app

cd ../reminder-service
dapr run --app-id reminder --app-port 8001 -- uvicorn app.main:app

# 4. Test event flow
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Test", "is_recurring":true, "recurrence_pattern":"daily"}'

# 5. Check logs for events flowing
# Only deploy to Azure once this works!
```

**Why?** Catch bugs locally (free) before Azure deployment (costs money)

## Troubleshooting

### Pods Pending
```bash
kubectl describe pod <name>
# Check: Insufficient resources
# Solution: Add nodes or reduce requests
```

### Events Not Flowing
```bash
# Check Kafka
kubectl logs -n kafka kafka-0

# Check Dapr
kubectl logs <pod> -c daprd
```

### High Memory
```bash
# Increase limits
resources:
  limits:
    memory: "1Gi"
```

## Success Criteria (B1s Demo Config)

### Must Have (P0)
- ✅ All 4 services deployed and running
- ✅ Frontend accessible via Azure public IP
- ✅ Events flowing through Kafka
- ✅ Reminders fire within 5 min of due time (slower on B1s)
- ✅ Recurring tasks auto-create on completion
- ✅ Can create tasks with priority/tags
- ✅ Search and filter works
- ✅ Total cost < $5 for demo period

### Performance Expectations (B1s)
- API latency: < 500ms (slower than B2s, acceptable)
- Event processing: < 30s (slower, acceptable for demo)
- Pod restarts: < 3 per hour
- Uptime: > 95% during demo period

### Demo Validation
- ✅ Public IP works from any browser
- ✅ Demo video < 90 seconds
- ✅ All Phase 4 features still work
- ✅ Can show Kafka topics with messages
- ✅ Can show all pods Running

**Note:** Performance lower on B1s but FUNCTIONALITY identical.
Judges care about working features, not speed.

## Timeline (Cost-Optimized)

**Days 1-5: Local Development ($0 cost)**
- Day 1-2: Backend updates, database migration (5 hrs)
- Day 3: Reminder + Recurring services (4 hrs)
- Day 4: Frontend updates (4 hrs)
- Day 5: Docker images, Helm charts (4 hrs)
- **Cost: $0 (no Azure resources yet)**

**Day 6: Deploy to Azure ($0.65)**
- Morning: Create AKS, deploy Kafka/Dapr (2 hrs)
- Afternoon: Deploy all services via Helm (2 hrs)
- Evening: Test and verify (2 hrs)

**Day 7: Demo & Submit ($0.65)**
- Morning: Final testing, bug fixes (2 hrs)
- Afternoon: Record demo video (1 hr)
- Evening: Submit hackathon (1 hr)

**Day 8: Stop Cluster**
```bash
az aks stop --resource-group todo-app-rg --name todo-aks-cluster
# Cost drops to $1/month (storage only)
```

**Total: 24 hours work, $1.30 Azure cost, $98.70 credit remaining!

## After Hackathon

### Keep for Portfolio (Recommended)
```bash
# Cluster stopped, cost = $1/month
# Restart when showing employers:
az aks start --resource-group todo-app-rg --name todo-aks-cluster
# Ready in 2-3 minutes!
```

### Delete Everything
```bash
# After results announced:
az group delete --name todo-app-rg --yes
# Cost = $0/month
# Can redeploy from GitHub anytime (30 min setup)
```

## Phase 5 Tasks Summary

The implementation of Phase 5 involves 34 atomic tasks organized across 13 groups:

### Group Distribution:
- **Infrastructure Setup (P0):** 6 tasks
- **Dapr & Kafka Setup (P0):** 6 tasks  
- **Database Updates (P0):** 1 task
- **Backend Updates (P0):** 4 tasks
- **Reminder Service (P0):** 2 tasks
- **Recurring Service (P1):** 2 tasks
- **Frontend Updates (P1):** 1 task
- **Docker Images (P0):** 2 tasks
- **Helm Charts (P0):** 1 task
- **Deployment (P0):** 1 task
- **CI/CD (P1):** 1 task
- **Testing & Docs (P0):** 1 task
- **Cost Management (P0/P1):** 4 tasks

### Priority Breakdown:
- **P0 (Critical):** 27 tasks - Must complete
- **P1 (High):** 7 tasks - Should complete

### Estimated Effort:
- **Total Time:** ~16 hours
- **Critical Path:** ~13 hours (P0 tasks only)
- **Recommended Completion:** All P0 + P1 tasks

### Execution Strategy:
1. **Days 1-5:** Complete all local development tasks (Groups 1-7) - $0 cost
2. **Day 6:** Deploy to Azure (Groups 8-10) - $0.65 cost
3. **Day 7:** Testing, documentation, and demo (Groups 11-12) - $0.65 cost
4. **Day 8:** Stop cluster for cost optimization (Group 13) - preserves $95+ credit

This comprehensive plan ensures delivery of the event-driven microservices architecture while maintaining strict cost control for the hackathon budget.