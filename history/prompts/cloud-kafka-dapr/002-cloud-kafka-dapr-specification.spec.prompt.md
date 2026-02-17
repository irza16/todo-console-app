---
id: 002
title: Cloud Kafka Dapr Specification
stage: spec
date_iso: 2026-02-11
surface: agent
model: google/gemini-2.0-flash-exp:free
feature: cloud-kafka-dapr
branch: 001-cloud-kafka-dapr
user: irza
command: /sp.specify
labels:
  - specification
  - kafka
  - dapr
  - cloud-deployment
  - event-driven
links:
  SPEC: specs/001-cloud-kafka-dapr/spec.md
  TICKET: null
  ADR: null
  PR: null
files_yaml:
  - specs/001-cloud-kafka-dapr/spec.md
  - specs/001-cloud-kafka-dapr/checklists/requirements.md
tests_yaml:
  - specification creation
  - event-driven architecture
  - cloud deployment
  - dapr integration
---

# Cloud Kafka Dapr Specification

## User Input

```text
# Phase 5: Cloud Deployment with Kafka & Dapr - Specification

## Overview
This specification defines the complete requirements for deploying the Todo AI Chatbot to Azure Kubernetes Service (AKS) with event-driven architecture using Kafka and Dapr.

## Target Platform: Azure Cloud (AKS)

### Azure Services Stack
| Service | Purpose | Estimated Cost |
|---------|---------|----------------|
| AKS (Azure Kubernetes Service) | Managed K8s | $70/mo |
| ACR (Container Registry) | Docker images | $5/mo |
| Event Hubs OR Self-hosted Kafka | Event streaming | $11/mo OR Free |
| Azure Monitor | Logs & metrics | Free (5GB) |
| Load Balancer | Public IP | $5/mo |
| **TOTAL** | | **$20-90/mo** (within $100 credit) |

---

## User Stories

### Epic 1: Cloud Infrastructure

#### US-5.1: Create AKS Cluster
**Priority:** P0
**Estimated:** 30 min

**Acceptance Criteria:**
- AKS cluster with 2 nodes (Standard_B2s: 2 vCPU, 4GB RAM each)
- Kubernetes 1.28+
- Azure CNI networking
- Autoscaling enabled (min 2, max 5)
- Cluster accessible via kubectl

**Azure CLI Commands:**
```bash
az aks create \
  --resource-group todo-app-rg \
  --name todo-aks-cluster \
  --node-count 2 \
  --node-vm-size Standard_B2s \
  --enable-managed-identity \
  --enable-addons monitoring \
  --generate-ssh-keys

az aks get-credentials --resource-group todo-app-rg --name todo-aks-cluster
kubectl get nodes  # Should show 2 Ready nodes
```

---

#### US-5.2: Setup Azure Container Registry
**Priority:** P0
**Estimated:** 20 min

**Acceptance Criteria:**
- ACR Basic tier created ($5/mo)
- Integrated with AKS
- Can push/pull images

**Commands:**
```bash
az acr create --resource-group todo-app-rg --name todoappcr --sku Basic
az aks update --resource-group todo-app-rg --name todo-aks-cluster --attach-acr todoappcr

# Test
docker tag todo-frontend:latest todoappcr.azurecr.io/todo-frontend:v5.0
az acr login --name todoappcr
docker push todoappcr.azurecr.io/todo-frontend:v5.0
```

---

#### US-5.3: Install Dapr on AKS
**Priority:** P0
**Estimated:** 20 min

**Acceptance Criteria:**
- Dapr 1.12+ installed
- All Dapr system pods Running
- Dashboard accessible

**Commands:**
```bash
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
dapr init --kubernetes --wait
kubectl get pods -n dapr-system  # All Running
dapr dashboard -k -p 9999 &  # Opens http://localhost:9999
```

---

### Epic 2: Event Streaming

#### US-5.4: Deploy Kafka to AKS
**Priority:** P0
**Estimated:** 45 min

**Acceptance Criteria:**
- Kafka 3.6+ running in AKS (Bitnami Helm chart)
- 3 topics created: task-events, reminder-events, task-updates
- Accessible from all pods
- 7-day retention

**Commands:**
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install kafka bitnami/kafka \
  --namespace kafka --create-namespace \
  --set replicaCount=1 \
  --set persistence.size=10Gi \
  --set deleteTopicEnable=true

# Create topics
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

**Alternative: Azure Event Hubs** (costs $11/mo but fully managed)

---

#### US-5.5: Configure Dapr Pub/Sub for Kafka
**Priority:** P0
**Estimated:** 30 min

**Acceptance Criteria:**
- Dapr Kafka component created
- Component accessible to all services
- Connection tested

**File: `k8s/dapr-components/kafka-pubsub.yaml`:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka.kafka.svc.cluster.local:9092"
  - name: consumerGroup
    value: "todo-app-group"
  - name: authType
    value: "none"
```

```bash
kubectl apply -f k8s/dapr-components/kafka-pubsub.yaml
kubectl get component kafka-pubsub
```

---

### Epic 3: Backend Enhancements

#### US-5.6: Add Event Publishing to Backend
**Priority:** P0
**Estimated:** 2 hours

**Acceptance Criteria:**
- Backend publishes `task.created` on POST /api/tasks
- Backend publishes `task.completed` on PATCH /api/tasks/{id}/complete
- Backend publishes `task.deleted` on DELETE /api/tasks/{id}
- Events include user_id, task_id, timestamp
- Uses Dapr pub/sub API

**Implementation in `backend/app/routers/tasks.py`:**
```python
import httpx

DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "kafka-pubsub"

async def publish_event(topic: str, data: dict):
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}"
    async with httpx.AsyncClient() as client:
        await client.post(url, json=data)

@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, current_user: User = Depends(get_current_user)):
    new_task = Task(**task.dict(), user_id=current_user.id)
    session.add(new_task)
    session.commit()

    await publish_event("task-events", {
        "event_type": "task.created",
        "task_id": str(new_task.id),
        "user_id": str(current_user.id),
        "title": new_task.title,
        "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
        "timestamp": datetime.utcnow().isoformat()
    })

    return new_task
```

---

#### US-5.7: Add Priority and Tags Fields
**Priority:** P1
**Estimated:** 1.5 hours

**Acceptance Criteria:**
- Task model has `priority` (Low/Medium/High/Urgent)
- Task model has `tags` (array of strings)
- Database migrated with new columns
- API accepts priority/tags
- API allows filtering by priority/tags

**Database Migration:**
```sql
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'Medium';
ALTER TABLE tasks ADD COLUMN tags TEXT[] DEFAULT '{}';
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);
```

**Backend Model:**
```python
from enum import Enum

class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class Task(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = False
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    user_id: uuid.UUID = Field(foreign_key="users.id")
```

---

#### US-5.8: Add Search and Filter Endpoints
**Priority:** P1
**Estimated:** 1 hour

**Acceptance Criteria:**
- GET /api/tasks/search?q=keyword
- Filter by status (all/active/completed)
- Filter by priority
- Filter by tags
- Results sorted by created_at desc

**Implementation:**
```python
@router.get("/search", response_model=List[TaskResponse])
async def search_tasks(
    q: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[TaskPriority] = None,
    tags: Optional[List[str]] = Query(None),
    current_user: User = Depends(get_current_user)
):
    query = select(Task).where(Task.user_id == current_user.id)

    if q:
        query = query.where(or_(
            Task.title.ilike(f"%{q}%"),
            Task.description.ilike(f"%{q}%")
        ))

    if status == "active":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    if priority:
        query = query.where(Task.priority == priority)

    if tags:
        query = query.where(Task.tags.contains(tags))

    query = query.order_by(Task.created_at.desc())
    tasks = session.exec(query).all()
    return tasks
```

---

### Epic 4: New Microservices

#### US-5.9: Create Reminder Service
**Priority:** P0
**Estimated:** 3 hours

**Acceptance Criteria:**
- New Python service `reminder-service`
- Subscribes to task-events topic
- Stores reminders for tasks with due_date
- Checks every minute via Dapr cron
- Publishes reminder.due event when time arrives

**Directory Structure:**
```
backend/reminder-service/
├── Dockerfile
├── app/
│   ├── main.py
│   └── models.py
├── requirements.txt
└── k8s/
    ├── deployment.yaml
    └── dapr-components/
        └── cron-binding.yaml
```

**Main Logic (`app/main.py`):**
```python
from fastapi import FastAPI
from datetime import datetime, timedelta
import httpx

app = FastAPI()
scheduled_reminders = {}

@app.post("/task-events")
async def handle_task_event(event: dict):
    if event["event_type"] == "task.created" and event.get("due_date"):
        due_date = datetime.fromisoformat(event["due_date"])
        reminder_time = due_date - timedelta(hours=1)
        scheduled_reminders[event["task_id"]] = {
            "task_id": event["task_id"],
            "user_id": event["user_id"],
            "title": event["title"],
            "reminder_time": reminder_time
        }
    return {"success": True}

@app.post("/check-reminders")
async def check_reminders(data: dict):
    now = datetime.utcnow()
    for task_id, reminder in list(scheduled_reminders.items()):
        if now >= reminder["reminder_time"]:
            await publish_event("reminder-events", {
                "event_type": "reminder.due",
                "task_id": reminder["task_id"],
                "user_id": reminder["user_id"],
                "title": reminder["title"],
                "timestamp": now.isoformat()
            })
            del scheduled_reminders[task_id]
    return {"checked": len(scheduled_reminders)}

@app.get("/dapr/subscribe")
async def subscribe():
    return [{
        "pubsubname": "kafka-pubsub",
        "topic": "task-events",
        "route": "/task-events"
    }]

async def publish_event(topic, data):
    url = f"http://localhost:3500/v1.0/publish/kafka-pubsub/{topic}"
    async with httpx.AsyncClient() as client:
        await client.post(url, json=data)
```

**Deployment with Dapr:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: reminder-service
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: reminder-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "reminder-service"
        dapr.io/app-port: "8001"
    spec:
      containers:
      - name: reminder-service
        image: todoappcr.azurecr.io/reminder-service:v5.0
        ports:
        - containerPort: 8001
```

---

#### US-5.10: Create Recurring Task Service
**Priority:** P1
**Estimated:** 2 hours

**Acceptance Criteria:**
- Subscribes to task.completed events
- Checks if task.is_recurring
- Calculates next occurrence based on pattern (daily/weekly/monthly)
- Creates new task
- Publishes task.created event

**Pattern Calculation:**
```python
from datetime import timedelta

def calculate_next_occurrence(completed_date, pattern):
    if pattern == "daily":
        return completed_date + timedelta(days=1)
    elif pattern == "weekly":
        return completed_date + timedelta(weeks=1)
    elif pattern == "monthly":
        return completed_date + timedelta(days=30)
    elif pattern == "weekdays":
        next_date = completed_date + timedelta(days=1)
        while next_date.weekday() >= 5:  # Skip weekends
            next_date += timedelta(days=1)
        return next_date
```

---

### Epic 5: Frontend UI Enhancements

#### US-5.11: Add Priority and Tags UI
**Priority:** P1
**Estimated:** 2 hours

**Acceptance Criteria:**
- Priority dropdown in task form
- Priority badges with colors (Low=green, Medium=yellow, High=orange, Urgent=red)
- Tag input with chips
- Filter by priority
- Filter by tags

**Components:**
```tsx
// Priority badge
const priorityColors = {
  Low: "bg-green-100 text-green-800",
  Medium: "bg-yellow-100 text-yellow-800",
  High: "bg-orange-100 text-orange-800",
  Urgent: "bg-red-100 text-red-800"
};

<span className={`px-2 py-1 rounded text-xs ${priorityColors[task.priority]}`}>
  {task.priority}
</span>

// Tag chips
{task.tags.map(tag => (
  <span key={tag} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">
    {tag}
  </span>
))}
```

---

#### US-5.12: Add Search and Filter UI
**Priority:** P1
**Estimated:** 1.5 hours

**Acceptance Criteria:**
- Search bar with debounced input
- Status filter dropdown
- Priority filter
- Tag multi-select
- Real-time results

```tsx
const [searchQuery, setSearchQuery] = useState("");
const [filters, setFilters] = useState({ status: "all", priority: null, tags: [] });

useEffect(() => {
  const debounce = setTimeout(() => {
    fetchTasks();
  }, 300);
  return () => clearTimeout(debounce);
}, [searchQuery, filters]);
```

---

### Epic 6: Deployment

#### US-5.13: Update Helm Charts for Azure
**Priority:** P0
**Estimated:** 2 hours

**Acceptance Criteria:**
- ACR image references
- LoadBalancer service for frontend
- Dapr annotations on all deployments
- Azure-specific resource limits

**values-azure.yaml:**
```yaml
images:
  registry: todoappcr.azurecr.io
  frontend:
    tag: v5.0
  backend:
    tag: v5.0

frontend:
  service:
    type: LoadBalancer  # Get public IP

backend:
  dapr:
    enabled: true
    appId: todo-backend
    appPort: 8000
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

---

#### US-5.14: Setup CI/CD with GitHub Actions
**Priority:** P1
**Estimated:** 2 hours

**Acceptance Criteria:**
- Workflow triggers on push to phase-5-cloud
- Builds Docker images
- Pushes to ACR
- Deploys to AKS
- Runs smoke test

**.github/workflows/deploy-azure.yml:**
```yaml
name: Deploy to AKS

on:
  push:
    branches: [phase-5-cloud]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}

    - name: Build and push images
      run: |
        az acr login --name todoappcr
        cd frontend && docker build -t todoappcr.azurecr.io/todo-frontend:${{ github.sha }} .
        docker push todoappcr.azurecr.io/todo-frontend:${{ github.sha }}
        # ... repeat for other services

    - name: Deploy with Helm
      run: |
        az aks get-credentials --resource-group todo-app-rg --name todo-aks-cluster
        helm upgrade --install todo-app ./k8s/helm/todo-app \
          --set images.frontend.tag=${{ github.sha }} \
          --wait
```

---

#### US-5.15: Setup Monitoring
**Priority:** P2
**Estimated:** 1 hour

**Acceptance Criteria:**
- Azure Monitor enabled
- Logs in Log Analytics
- Basic metrics dashboard

```bash
az aks enable-addons --resource-group todo-app-rg \
  --name todo-aks-cluster --addons monitoring
```

---

## Technical Requirements

### Services
| Service | Tech | Port | Replicas | Resources |
|---------|------|------|----------|-----------|
| Frontend | Next.js | 3000 | 2 | 256Mi/250m |
| Backend | FastAPI | 8000 | 2 | 512Mi/500m |
| Reminder Service | Python | 8001 | 1 | 256Mi/250m |
| Recurring Task Service | Python | 8002 | 1 | 256Mi/250m |

### Kafka Topics
- task-events (3 partitions, 7-day retention)
- reminder-events (3 partitions, 7-day retention)
- task-updates (3 partitions, 1-day retention)

### Dapr Components
- kafka-pubsub (pubsub.kafka)
- reminder-cron (bindings.cron)
- kubernetes-secrets (secretstores.kubernetes)

---

## Success Criteria

### Must Have (P0)
- ✅ AKS cluster running
- ✅ All 4 services deployed
- ✅ Kafka operational
- ✅ Events flowing
- ✅ Reminders working
- ✅ Frontend has public IP
- ✅ All Phase 4 features working

### Should Have (P1)
- ✅ Priority and tags
- ✅ Search and filter
- ✅ Recurring tasks
- ✅ CI/CD pipeline
- ✅ Documentation

### Nice to Have (P2)
- ⚠️ Monitoring dashboard
- ⚠️ Advanced logging
- ⚠️ Cost optimization

---

## Out of Scope
- Real-time WebSocket notifications
- Email/SMS alerts
- Multi-user collaboration
- Mobile app
- Service mesh
- Multi-region

---

## Estimated Timeline
- Infrastructure setup: 2-3 hours
- Backend updates: 4-6 hours
- New services: 4-6 hours
- Frontend updates: 3-4 hours
- Deployment: 3-4 hours
- Testing & docs: 2-3 hours
**Total: 18-26 hours** over 5-7 days

---

This spec provides clear, actionable requirements for Phase 5. Next: Plan and Tasks documents.
```

## Response

Created a comprehensive feature specification for cloud deployment with Kafka and Dapr. The specification includes:

1. User scenarios covering cloud infrastructure deployment, event-driven task management, enhanced task features with priority and tags, search and filtering, automated reminders, and recurring task automation
2. Functional requirements for all aspects of the system including deployment, event processing, task management, and automation
3. Success criteria with measurable outcomes for deployment, performance, reliability, and cost optimization
4. Identification of key entities including tasks, events, users, reminders, and recurring tasks
5. Edge cases addressing potential failure scenarios and scalability considerations

The specification follows the template structure and is ready for the planning phase. A quality checklist was also created to validate that all requirements are met and the specification is ready for implementation planning.

## Outcome

Successfully created a comprehensive specification for the cloud deployment with Kafka and Dapr feature. The specification is complete, testable, and ready for the planning phase. All requirements from the template have been addressed, and the document provides clear direction for implementing the event-driven architecture on Azure Kubernetes Service.