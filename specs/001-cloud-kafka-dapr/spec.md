# Feature Specification: Cloud Deployment with Kafka & Dapr

**Feature Branch**: `001-cloud-kafka-dapr`
**Created**: 2026-02-11
**Status**: Draft
**Input**: User description: "# Phase 5: Cloud Deployment with Kafka & Dapr - Specification

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
- AKS cluster with 1 node (Standard_B1s: 1 vCPU, 1GB RAM) - demo config
- Kubernetes 1.28+
- Azure CNI networking
- Cluster accessible via kubectl
- Cost: ~$0.33/day

**Azure CLI Commands:**
```bash
# OPTIMIZED for demo/hackathon (minimal cost)
az aks create \
  --resource-group todo-app-rg \
  --name todo-aks-cluster \
  --node-count 1 \                    # 1 node instead of 2
  --node-vm-size Standard_B1s \       # Smallest: 1 vCPU, 1GB RAM
  --enable-managed-identity \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --kubernetes-version 1.28

# Note: This is minimal config for demo. For production, use:
# --node-count 2 --node-vm-size Standard_B2s
az aks get-credentials --resource-group todo-app-rg --name todo-aks-cluster
kubectl get nodes  # Should show 1 Ready node
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
  resources:
    requests:
      memory: "128Mi"  # Reduced for B1s
      cpu: "100m"      # Reduced for B1s
    limits:
      memory: "256Mi"  # Reduced for B1s
      cpu: "250m"      # Reduced for B1s

backend:
  dapr:
    enabled: true
    appId: todo-backend
    appPort: 8000
  resources:
    requests:
      memory: "256Mi"  # Reduced for B1s
      cpu: "200m"      # Reduced for B1s
    limits:
      memory: "512Mi"  # Reduced for B1s
      cpu: "500m"      # Reduced for B1s
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
| Frontend | Next.js | 3000 | 1 | 128Mi/100m |
| Backend | FastAPI | 8000 | 1 | 256Mi/200m |
| Reminder Service | Python | 8001 | 1 | 64Mi/50m |
| Recurring Task Service | Python | 8002 | 1 | 64Mi/50m |

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

## Deployment Strategy

### Parallel Deployments

**CLARIFY:** Phase 3 and Phase 5 run SEPARATELY

```
Phase 3 (Keep Running):
├── Frontend: todo-console-app-orcin.vercel.app
├── Backend: huggingface.co/spaces/your-space
└── Database: Neon PostgreSQL

Phase 5 (New Deployment):
├── Frontend: http://<azure-public-ip>
├── Backend: In AKS cluster
├── Services: In AKS cluster
└── Database: SAME Neon PostgreSQL (shared)
```

**Key Points:**
- Both deployments use the SAME database
- Both are independent and can run simultaneously
- Phase 3 = proof of completion
- Phase 5 = advanced cloud deployment
- Delete Phase 5 after hackathon, keep Phase 3 forever (free)

## Out of Scope
- Real-time WebSocket notifications
- Email/SMS alerts
- Multi-user collaboration
- Mobile app
- Service mesh
- Multi-region

## Environment Variables Management

### Secrets Strategy Across Deployments

**CLARIFY:** Same database, different deployments

```
## Environment Variables Across Deployments

### Shared (Same for all deployments):
```
DATABASE_URL="postgresql://..." # Neon DB (same)
JWT_SECRET="your-secret"         # Same secret
```

### Different (Per deployment):
```
# Phase 3 (Vercel)
NEXT_PUBLIC_API_URL="https://your-hf-space.hf.space"

# Phase 5 (Azure)
NEXT_PUBLIC_API_URL="http://<azure-public-ip>:8000"
```

### Setting in Azure
```
# Create Kubernetes secret
kubectl create secret generic todo-app-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=jwt-secret="$JWT_SECRET"

# Verify
kubectl get secret todo-app-secrets -o yaml
```

### Security Note
- NEVER commit secrets to Git
- Use Kubernetes Secrets in cluster
- Use Vercel Environment Variables for Phase 3
- Rotate secrets quarterly
```

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

This spec provides clear, actionable requirements for Phase 5. Next: Plan and Tasks documents."

## Clarifications

### Session 2026-02-11

- Q: What AKS node configuration should be used for the hackathon demo? → A: 1 node (Standard_B1s: 1 vCPU, 1GB RAM) for cost optimization (~$0.33/day)
- Q: How should resource allocations be adjusted for B1s nodes? → A: Reduced resource requests/limits to fit within B1s capacity constraints

## User Scenarios & Testing *(mandatory)*

<!-- IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance. Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them, you should still have a viable MVP (Minimum Viable Product) that delivers value. Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical. Think of each story as a standalone slice of functionality that can be: - Developed independently - Tested independently - Deployed independently - Demonstrated to users independently -->

### User Story 1 - Cloud Infrastructure Deployment (Priority: P1)

As a system administrator, I want to deploy the Todo AI Chatbot application to Azure Kubernetes Service (AKS) with event-driven architecture so that the application can scale automatically and handle distributed processing.

**Why this priority**: This is foundational - without the cloud infrastructure, none of the other features can be deployed or used.

**Independent Test**: Can be fully tested by verifying that AKS cluster is running, Dapr is installed, and Kafka is operational. Delivers the ability to run the application in a scalable cloud environment.

**Acceptance Scenarios**:

1. **Given** Azure subscription exists, **When** I deploy the AKS cluster, **Then** a functional Kubernetes cluster with 1 node (Standard_B1s) is created and accessible via kubectl
2. **Given** AKS cluster is running, **When** I install Dapr, **Then** all Dapr system pods are Running and the dashboard is accessible

---

### User Story 2 - Event-Driven Task Management (Priority: P1)

As a user, I want to create tasks that trigger automated behaviors (reminders, recurring tasks) so that I can manage my schedule without manual intervention.

**Why this priority**: This is the core value proposition of the event-driven architecture - tasks automatically generate events that trigger downstream actions.

**Independent Test**: Can be fully tested by creating a task with a due date and verifying that reminder events are published. Delivers the core event-driven automation functionality.

**Acceptance Scenarios**:

1. **Given** a user creates a task with a due date, **When** the task is saved, **Then** a task.created event is published to the task-events topic
2. **Given** a user completes a recurring task, **When** the completion occurs, **Then** a new task is automatically created based on the recurrence pattern

---

### User Story 3 - Enhanced Task Management with Priority and Tags (Priority: P2)

As a user, I want to assign priority levels and tags to my tasks so that I can better organize and filter my tasks based on importance and category.

**Why this priority**: This enhances the core task management experience and provides better organization capabilities for users.

**Independent Test**: Can be fully tested by creating tasks with priority and tags, and verifying they can be filtered and searched. Delivers improved task organization and discoverability.

**Acceptance Scenarios**:

1. **Given** a user creates a task with priority and tags, **When** the task is saved, **Then** the priority and tags are stored and can be retrieved
2. **Given** multiple tasks with different priorities and tags exist, **When** the user applies filters, **Then** only matching tasks are displayed

---

### User Story 4 - Task Search and Filtering (Priority: P2)

As a user, I want to search and filter my tasks by various criteria so that I can quickly find the tasks I need.

**Why this priority**: This significantly improves the usability of the application when users have many tasks.

**Independent Test**: Can be fully tested by performing searches and applying filters to verify that the correct subset of tasks is returned. Delivers improved task discovery and navigation.

**Acceptance Scenarios**:

1. **Given** multiple tasks exist, **When** a user searches by keyword, **Then** only tasks matching the keyword in title or description are returned
2. **Given** tasks with various statuses and priorities exist, **When** a user applies filters, **Then** only tasks matching all filter criteria are returned

---

### User Story 5 - Automated Reminder System (Priority: P1)

As a user, I want to receive automated reminders for tasks with due dates so that I don't miss important deadlines.

**Why this priority**: This is a core value-add feature that makes the application more useful by proactively notifying users.

**Independent Test**: Can be fully tested by creating tasks with due dates and verifying that reminder notifications are triggered at the appropriate time. Delivers proactive task management assistance.

**Acceptance Scenarios**:

1. **Given** a task with a due date is created, **When** the due date approaches, **Then** a reminder notification is sent to the user
2. **Given** multiple tasks with due dates exist, **When** their reminder times arrive, **Then** each receives a notification at the appropriate time

---

### User Story 6 - Recurring Task Automation (Priority: P2)

As a user, I want to create recurring tasks that automatically generate new instances so that I don't need to manually recreate repetitive tasks.

**Why this priority**: This reduces manual work for users who have repetitive tasks and adds significant automation value.

**Independent Test**: Can be fully tested by creating recurring tasks and verifying that new instances are automatically created when previous ones are completed. Delivers task automation for repetitive work.

**Acceptance Scenarios**:

1. **Given** a recurring task is marked as completed, **When** the completion occurs, **Then** a new instance of the task is automatically created based on the recurrence pattern
2. **Given** different recurrence patterns exist (daily, weekly, monthly), **When** tasks are completed, **Then** new instances are created according to the specified pattern

---

### Edge Cases

- What happens when the Kafka cluster is temporarily unavailable during task creation?
- How does the system handle malformed event payloads from the event stream?
- What happens when the reminder service experiences downtime during scheduled reminder times?
- How does the system handle users with thousands of tasks when performing search and filter operations?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST deploy to Azure Kubernetes Service with auto-scaling enabled
- **FR-002**: System MUST integrate with Dapr for event-driven communication between services
- **FR-003**: System MUST publish task-related events (created, completed, deleted) to Kafka topics
- **FR-004**: System MUST store task priority levels (Low, Medium, High, Urgent) and tags
- **FR-005**: System MUST provide search functionality to find tasks by keyword in title or description
- **FR-006**: System MUST allow filtering tasks by status, priority, and tags
- **FR-007**: System MUST automatically generate reminder notifications for tasks with due dates
- **FR-008**: System MUST automatically create new instances of recurring tasks when completed
- **FR-009**: System MUST persist all task data in a reliable database with proper user isolation
- **FR-010**: System MUST support continuous deployment via GitHub Actions pipeline

### Key Entities

- **Task**: Represents a user's task with title, description, completion status, due date, priority level, tags, and user ownership
- **Event**: Represents system events (task.created, task.completed, task.deleted, reminder.due) that trigger automated actions
- **User**: Represents an authenticated user with isolated data access and personal task management
- **Reminder**: Represents scheduled notifications for upcoming task due dates
- **Recurring Task**: A special type of task that automatically generates new instances based on a recurrence pattern

## Cost Optimization Strategy

### Hackathon Demo Strategy (Minimal Cost)

**Recommended Approach:**
1. Deploy with smallest viable configuration
2. Run for 3-7 days during demo period
3. Record demo video and submit
4. Stop or delete cluster after hackathon
5. Preserve $95+ of $100 Azure credit

**Minimal Configuration:**
- 1 node instead of 2-3
- Standard_B1s VM (1 vCPU, 1GB RAM) instead of B2s
- Basic ACR tier (keep)
- Self-hosted Kafka (not Event Hubs)
- Delete after demo OR stop cluster

**Cost Breakdown:**
```
Resource              | Daily Cost | 7-Day Cost
---------------------|------------|------------
AKS (1x B1s node)    | $0.33      | $2.31
ACR Basic            | $0.16      | $1.12
Load Balancer        | $0.16      | $1.12
Bandwidth (<5GB)     | $0.00      | $0.00
TOTAL                | $0.65/day  | $4.55/week
```

**After Demo:**
Option A: Stop cluster - $1/month (storage only)
Option B: Delete everything - $0/month

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Application successfully deploys to AKS with all services running and accessible via public endpoint
- **SC-002**: Event-driven architecture processes task events without loss or duplication (demo scale)
- **SC-003**: Users can create tasks with priority and tags, and filter/search returns results in under 2 seconds
- **SC-004**: Reminder notifications are delivered within 5 minutes of scheduled time for 95% of reminders (adjusted for B1s)
- **SC-005**: Recurring tasks automatically generate new instances with 99% reliability
- **SC-006**: System supports demo usage with average response time under 500ms (B1s performance)
- **SC-007**: Continuous deployment pipeline successfully deploys changes with zero downtime
- **SC-008**: Demo operational costs remain under $5 for 7-day hackathon period (B1s optimization)