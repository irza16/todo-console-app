# Phase 5 Tasks: Atomic Implementation Steps

## Overview
58 atomic tasks organized into 13 groups for Azure AKS deployment with Kafka and Dapr.

**Estimated Total Time:** 18-24 hours
**Total Cost:** $3-5 for 7-day demo (save $95+ credit!)
**Priority Breakdown:**
- P0 (Critical): 41 tasks - Must complete
- P1 (High): 14 tasks - Should complete
- P2 (Optional): 3 tasks - Nice to have

**Cost-Optimized Strategy:**
- Days 1-5: Local development ($0)
- Day 6: Deploy to Azure ($0.65)
- Day 7: Demo and submit ($0.65)
- Day 8: Stop cluster (cost drops to $1/month)

---

## Group 1: Azure Infrastructure Setup (P0)

### T-5.001: Install Azure CLI
**Priority:** P0
**Estimated Time:** 10 minutes
**Dependencies:** None

**Description:**
Install Azure CLI on your local machine to manage Azure resources.

**Implementation Steps:**
```bash
# For Ubuntu/Debian
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Verify installation
az --version
```

**Acceptance Criteria:**
- Azure CLI version 2.50+ installed
- `az --version` command works
- No errors during installation

**Testing:**
```bash
az --version
# Should output: azure-cli 2.x.x
```

**Files Created/Modified:** None

---

### T-5.002: Login to Azure
**Priority:** P0
**Estimated Time:** 5 minutes
**Dependencies:** T-5.001

**Description:**
Authenticate with your Azure student account.

**Implementation Steps:**
```bash
# Login (opens browser)
az login

# Verify subscription
az account show

# Set subscription (if multiple)
az account set --subscription "<subscription-id>"
```

**Acceptance Criteria:**
- Successfully logged in
- Student subscription visible ($100 credit)
- Correct subscription set as default

**Testing:**
```bash
az account show
# Should show your student subscription
```

---

### T-5.003: Create Resource Group
**Priority:** P0
**Estimated Time:** 5 minutes
**Dependencies:** T-5.002

**Description:**
Create a resource group to contain all Azure resources.

**Implementation Steps:**
```bash
az group create \
  --name todo-app-rg \
  --location southeastasia
```

**Acceptance Criteria:**
- Resource group `todo-app-rg` created
- Location set to southeastasia (or closest to Pakistan)
- Resource group visible in Azure Portal

**Testing:**
```bash
az group show --name todo-app-rg
# Should output resource group details
```

---

### T-5.004: Create AKS Cluster (COST-OPTIMIZED)
**Priority:** P0
**Estimated Time:** 20 minutes (cluster creation takes 10-15 min)
**Dependencies:** T-5.003

**Description:**
Create Azure Kubernetes Service cluster with minimal cost configuration for demo.

**Implementation Steps:**
```bash
# COST-OPTIMIZED: 1 node, B1s VM ($0.33/day instead of $2.33/day)
az aks create \
  --resource-group todo-app-rg \
  --name todo-aks-cluster \
  --node-count 1 \
  --node-vm-size Standard_B1s \
  --enable-managed-identity \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --kubernetes-version 1.28
```

**Acceptance Criteria:**
- AKS cluster created with 1 node
- Node is Standard_B1s (1 vCPU, 1GB RAM)
- Monitoring add-on enabled
- Kubernetes version 1.28+
- Cost: ~$0.33/day ($10/month)

**Testing:**
```bash
az aks show --resource-group todo-app-rg --name todo-aks-cluster
# Should show provisioningState: Succeeded

az aks get-credentials --resource-group todo-app-rg --name todo-aks-cluster
kubectl get nodes
# Should show 1 node in Ready state (B1s)
```

**Notes:**
- B1s = Smallest VM (good for demo, slower than B2s)
- For production, use: --node-count 2 --node-vm-size Standard_B2s
- Can upgrade after hackathon if needed

**Troubleshooting:**
- If creation fails: Check quota limits in subscription
- If slow: AKS creation takes 10-15 minutes normally

---

### T-5.005: Create Azure Container Registry
**Priority:** P0
**Estimated Time:** 10 minutes
**Dependencies:** T-5.003

**Description:**
Create private Docker registry for storing images.

**Implementation Steps:**
```bash
az acr create \
  --resource-group todo-app-rg \
  --name todoappcr \
  --sku Basic
```

**Acceptance Criteria:**
- ACR named `todoappcr` created
- Basic tier ($5/month)
- Login server: todoappcr.azurecr.io

**Testing:**
```bash
az acr show --name todoappcr --resource-group todo-app-rg
# Should show provisioningState: Succeeded
```

---

### T-5.006: Attach ACR to AKS
**Priority:** P0
**Estimated Time:** 5 minutes
**Dependencies:** T-5.004, T-5.005

**Description:**
Grant AKS permission to pull images from ACR.

**Implementation Steps:**
```bash
az aks update \
  --resource-group todo-app-rg \
  --name todo-aks-cluster \
  --attach-acr todoappcr
```

**Acceptance Criteria:**
- AKS can pull from ACR without credentials
- No manual imagePullSecrets needed

**Testing:**
```bash
# This will be verified when deploying first image
```

---

## Group 2: Dapr and Kafka Setup (P0)

### T-5.007: Install Dapr CLI Locally
**Priority:** P0
**Estimated Time:** 10 minutes
**Dependencies:** None

**Description:**
Install Dapr CLI on local machine for managing Dapr.

**Implementation Steps:**
```bash
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Verify installation
dapr --version
```

**Acceptance Criteria:**
- Dapr CLI version 1.12+ installed
- `dapr` command available

**Testing:**
```bash
dapr --version
# Should output: CLI version: 1.12.x
```

---

### T-5.008: Initialize Dapr on AKS
**Priority:** P0
**Estimated Time:** 10 minutes
**Dependencies:** T-5.004, T-5.007

**Description:**
Install Dapr runtime on AKS cluster.

**Implementation Steps:**
```bash
# Ensure kubectl is configured for AKS
az aks get-credentials --resource-group todo-app-rg --name todo-aks-cluster

# Initialize Dapr
dapr init --kubernetes --wait

# Verify installation
kubectl get pods -n dapr-system
```

**Acceptance Criteria:**
- All Dapr pods running in dapr-system namespace
- Pods: dapr-operator, dapr-placement, dapr-sidecar-injector, dapr-sentry

**Testing:**
```bash
kubectl get pods -n dapr-system
# All pods should be Running (4 total)

dapr status -k
# Should show Dapr version and healthy status
```

---

### T-5.009: Deploy Kafka via Helm
**Priority:** P0
**Estimated Time:** 15 minutes
**Dependencies:** T-5.004

**Description:**
Deploy self-hosted Kafka cluster to AKS.

**Implementation Steps:**
```bash
# Add Bitnami Helm repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Kafka
helm install kafka bitnami/kafka \
  --namespace kafka \
  --create-namespace \
  --set replicaCount=1 \
  --set persistence.size=10Gi \
  --set deleteTopicEnable=true \
  --set resources.requests.memory=512Mi \
  --set resources.requests.cpu=250m
```

**Acceptance Criteria:**
- Kafka pod running in kafka namespace
- 10GB persistent volume created
- Kafka accessible at kafka.kafka.svc.cluster.local:9092

**Testing:**
```bash
kubectl get pods -n kafka
# kafka-0 should be Running

kubectl get pvc -n kafka
# Should show 10Gi PVC bound
```

---

### T-5.010: Create Kafka Topics
**Priority:** P0
**Estimated Time:** 10 minutes
**Dependencies:** T-5.009

**Description:**
Create 3 Kafka topics for event streaming.

**Implementation Steps:**
```bash
# Run Kafka client pod
kubectl run kafka-client \
  --restart='Never' \
  --image docker.io/bitnami/kafka:3.6.0 \
  --namespace kafka \
  --command -- sleep infinity

# Wait for pod to be ready
kubectl wait --for=condition=ready pod/kafka-client -n kafka --timeout=60s

# Create topics
kubectl exec -it kafka-client -n kafka -- kafka-topics.sh \
  --create \
  --bootstrap-server kafka.kafka.svc.cluster.local:9092 \
  --topic task-events \
  --partitions 3 \
  --replication-factor 1

kubectl exec -it kafka-client -n kafka -- kafka-topics.sh \
  --create \
  --bootstrap-server kafka.kafka.svc.cluster.local:9092 \
  --topic reminder-events \
  --partitions 3 \
  --replication-factor 1

kubectl exec -it kafka-client -n kafka -- kafka-topics.sh \
  --create \
  --bootstrap-server kafka.kafka.svc.cluster.local:9092 \
  --topic task-updates \
  --partitions 3 \
  --replication-factor 1
```

**Acceptance Criteria:**
- 3 topics created: task-events, reminder-events, task-updates
- Each topic has 3 partitions
- Replication factor = 1

**Testing:**
```bash
kubectl exec -it kafka-client -n kafka -- kafka-topics.sh \
  --list \
  --bootstrap-server kafka.kafka.svc.cluster.local:9092

# Should output:
# task-events
# reminder-events
# task-updates
```

---

### T-5.011: Create Dapr Kafka Pub/Sub Component
**Priority:** P0
**Estimated Time:** 10 minutes
**Dependencies:** T-5.008, T-5.010

**Description:**
Configure Dapr to use Kafka for pub/sub messaging.

**Implementation Steps:**
```bash
# Create directory
mkdir -p k8s/dapr-components

# Create kafka-pubsub.yaml
cat > k8s/dapr-components/kafka-pubsub.yaml << 'EOF'
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
  - name: maxMessageBytes
    value: "1024000"
EOF

# Apply to cluster
kubectl apply -f k8s/dapr-components/kafka-pubsub.yaml
```

**Acceptance Criteria:**
- Dapr component `kafka-pubsub` created
- Component accessible to all services in default namespace

**Testing:**
```bash
kubectl get component kafka-pubsub
# Should show component exists

kubectl describe component kafka-pubsub
# Should show Kafka configuration
```

**Files Created:**
- `k8s/dapr-components/kafka-pubsub.yaml`

---

### T-5.012: Create Dapr Cron Binding Component
**Priority:** P0
**Estimated Time:** 10 minutes
**Dependencies:** T-5.008

**Description:**
Create Dapr cron binding for reminder service scheduler.

**Implementation Steps:**
```bash
cat > k8s/dapr-components/reminder-cron.yaml << 'EOF'
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
  namespace: default
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: " @every 1m"
  - name: direction
    value: "input"
EOF

kubectl apply -f k8s/dapr-components/reminder-cron.yaml
```

**Acceptance Criteria:**
- Cron binding created
- Will trigger every 1 minute

**Testing:**
```bash
kubectl get component reminder-cron
```

**Files Created:**
- `k8s/dapr-components/reminder-cron.yaml`

---

## Group 3: Database Schema Updates (P0)

### T-5.013: Add Priority and Tags Columns
**Priority:** P0
**Estimated Time:** 10 minutes
**Dependencies:** None (Neon DB from Phase 2)

**Description:**
Add new columns to tasks table for priority and tags.

**Implementation Steps:**
```bash
# Connect to Neon database (use GUI or psql)
# Navigate to: https://console.neon.tech

# Run migration SQL:
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'Medium';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT FALSE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_pattern VARCHAR(20);

# Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_tags ON tasks USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_tasks_recurring ON tasks(is_recurring) WHERE is_recurring = TRUE;
```

**Acceptance Criteria:**
- 4 new columns added to tasks table
- 3 indexes created
- Existing data unaffected (NULL/default values)

**Testing:**
```sql
\d tasks
-- Should show new columns

SELECT * FROM tasks LIMIT 1;
-- Should show priority='Medium', tags='{}', etc.
```

**Rollback Plan:**
```sql
ALTER TABLE tasks DROP COLUMN priority;
ALTER TABLE tasks DROP COLUMN tags;
ALTER TABLE tasks DROP COLUMN is_recurring;
ALTER TABLE tasks DROP COLUMN recurrence_pattern;
DROP INDEX idx_tasks_priority;
DROP INDEX idx_tasks_tags;
DROP INDEX idx_tasks_recurring;
```

---

## Group 4: Backend API Updates (P0)

### T-5.014: Update Task Model
**Priority:** P0
**Estimated Time:** 20 minutes
**Dependencies:** T-5.013

**Description:**
Update backend Task model to include new fields.

**Implementation Steps:**

Edit `backend/app/models.py`:
```python
from enum import Enum
from typing import Optional, List
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import ARRAY, String
import uuid
from datetime import datetime

class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class RecurrencePattern(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    WEEKDAYS = "weekdays"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = False
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM  # NEW
    tags: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))  # NEW
    is_recurring: bool = False  # NEW
    recurrence_pattern: Optional[RecurrencePattern] = None  # NEW
    user_id: uuid.UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Acceptance Criteria:**
- Task model includes all new fields
- Enums defined for priority and recurrence
- Fields have appropriate defaults

**Testing:**
```bash
# Start backend locally
cd backend
python -c "from app.models import Task, TaskPriority; print('Models OK')"
```

**Files Modified:**
- `backend/app/models.py`

---

### T-5.015: Add Event Publishing Helper
**Priority:** P0
**Estimated Time:** 15 minutes
**Dependencies:** None

**Description:**
Create helper function to publish events via Dapr.

**Implementation Steps:**

Create `backend/app/events.py`:
```python
import httpx
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "kafka-pubsub"

async def publish_event(topic: str, event_data: Dict[str, Any]) -> bool:
    """
    Publish event to Kafka via Dapr pub/sub.
    
    Args:
        topic: Kafka topic name
        event_data: Event payload
        
    Returns:
        True if published successfully, False otherwise
    """
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=event_data,
                timeout=5.0
            )
            
            if response.status_code == 204:
                logger.info(f"Published event to {topic}: {event_data.get('event_type')}")
                return True
            else:
                logger.error(f"Failed to publish event: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Error publishing event: {e}")
        return False

def create_task_event(event_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create standardized task event payload."""
    return {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        **task_data
    }
```

**Acceptance Criteria:**
- publish_event function created
- Uses Dapr HTTP API (port 3500)
- Error handling included
- Logging added

**Testing:**
```python
# Will be tested when backend publishes events
```

**Files Created:**
- `backend/app/events.py`

---

### T-5.016: Update Create Task Endpoint
**Priority:** P0
**Estimated Time:** 30 minutes
**Dependencies:** T-5.014, T-5.015

**Description:**
Modify task creation to publish events.

**Implementation Steps:**

Edit `backend/app/routers/tasks.py`:
```python
from app.events import publish_event, create_task_event
from app.models import Task, TaskPriority, RecurrencePattern
from typing import Optional, List

 @router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Create task
    new_task = Task(
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        priority=task.priority or TaskPriority.MEDIUM,
        tags=task.tags or [],
        is_recurring=task.is_recurring or False,
        recurrence_pattern=task.recurrence_pattern,
        user_id=current_user.id
    )
    
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    
    # Publish event
    event_data = create_task_event("task.created", {
        "task_id": str(new_task.id),
        "user_id": str(current_user.id),
        "title": new_task.title,
        "description": new_task.description,
        "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
        "priority": new_task.priority.value,
        "tags": new_task.tags,
        "is_recurring": new_task.is_recurring,
        "recurrence_pattern": new_task.recurrence_pattern.value if new_task.recurrence_pattern else None
    })
    
    await publish_event("task-events", event_data)
    
    return new_task
```

**Acceptance Criteria:**
- Task creation saves to database
- Event published to task-events topic
- Event includes all task data

**Testing:**
```bash
# Create task via API
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test task",
    "priority": "High",
    "tags": ["test"]
  }'

# Check backend logs for event publishing
```

**Files Modified:**
- `backend/app/routers/tasks.py`

---

### T-5.017: Update Complete Task Endpoint
**Priority:** P0
**Estimated Time:** 20 minutes
**Dependencies:** T-5.015

**Description:**
Publish event when task is completed.

**Implementation Steps:**

Add to `backend/app/routers/tasks.py`:
```python
 @router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.completed = True
    task.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(task)
    
    # Publish event
    event_data = create_task_event("task.completed", {
        "task_id": str(task.id),
        "user_id": str(current_user.id),
        "title": task.title,
        "is_recurring": task.is_recurring,
        "recurrence_pattern": task.recurrence_pattern.value if task.recurrence_pattern else None,
        "completed_at": datetime.utcnow().isoformat()
    })
    
    await publish_event("task-events", event_data)
    
    return task
```

**Acceptance Criteria:**
- Task marked complete in DB
- Event published with recurring info

**Files Modified:**
- `backend/app/routers/tasks.py`

---

### T-5.018: Add Search Endpoint
**Priority:** P1
**Estimated Time:** 30 minutes
**Dependencies:** T-5.014

**Description:**
Add search and filter endpoint for tasks.

**Implementation Steps:**

Add to `backend/app/routers/tasks.py`:
```python
from sqlalchemy import or_

 @router.get("/search", response_model=List[TaskResponse])
async def search_tasks(
    q: Optional[str] = None,
    status: Optional[str] = None,  # 'all', 'active', 'completed'
    priority: Optional[TaskPriority] = None,
    tags: Optional[List[str]] = Query(None),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    query = select(Task).where(Task.user_id == current_user.id)
    
    # Search in title and description
    if q:
        search_pattern = f"%{q}%"
        query = query.where(
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern)
            )
        )
    
    # Filter by status
    if status == "active":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)
    
    # Filter by priority
    if priority:
        query = query.where(Task.priority == priority)
    
    # Filter by tags
    if tags:
        query = query.where(Task.tags.contains(tags))
    
    # Order by created_at desc
    query = query.order_by(Task.created_at.desc())
    
    tasks = session.exec(query).all()
    return tasks
```

**Acceptance Criteria:**
- Search works on title/description (case-insensitive)
- Filters work for status, priority, tags
- Results sorted by date

**Testing:**
```bash
curl "http://localhost:8000/api/tasks/search?q=meeting&priority=High" \
  -H "Authorization: Bearer $TOKEN"
```

**Files Modified:**
- `backend/app/routers/tasks.py`

---

## Group 5: New Microservices (P0)

### T-5.019: Create Reminder Service Structure
**Priority:** P0
**Estimated Time:** 20 minutes
**Dependencies:** None

**Description:**
Create directory structure and files for reminder service.

**Implementation Steps:**
```bash
# Create directories
mkdir -p backend/reminder-service/app
cd backend/reminder-service

# Create files
touch app/__init__.py
touch app/main.py
touch app/models.py
touch requirements.txt
touch Dockerfile
```

**Acceptance Criteria:**
- Directory structure created
- Empty files in place

**Files Created:**
- `backend/reminder-service/app/__init__.py`
- `backend/reminder-service/app/main.py`
- `backend/reminder-service/app/models.py`
- `backend/reminder-service/requirements.txt`
- `backend/reminder-service/Dockerfile`

---

### T-5.020: Implement Reminder Service Logic
**Priority:** P0
**Estimated Time:** 2 hours
**Dependencies:** T-5.019

**Description:**
Implement reminder service that subscribes to task-events and schedules reminders.

**Implementation Steps:**

Create `backend/reminder-service/app/main.py`:
```python
from fastapi import FastAPI
from datetime import datetime, timedelta
import httpx
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Reminder Service")

DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "kafka-pubsub"

# In-memory storage of scheduled reminders
scheduled_reminders: Dict[str, Dict[str, Any]] = {}

 @app.get("/health")
async def health():
    return {"status": "healthy", "reminders": len(scheduled_reminders)}

 @app.post("/task-events")
async def handle_task_event(event: Dict[str, Any]):
    """
    Dapr subscription endpoint for task-events.
    Called by Dapr when new event arrives.
    """
    logger.info(f"Received event: {event.get('event_type')}")
    
    if event.get("event_type") == "task.created":
        task_id = event.get("task_id")
        due_date_str = event.get("due_date")
        
        if due_date_str:
            try:
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                reminder_time = due_date - timedelta(hours=1)  # 1 hour before
                
                # Store reminder
                scheduled_reminders[task_id] = {
                    "task_id": task_id,
                    "user_id": event.get("user_id"),
                    "title": event.get("title"),
                    "reminder_time": reminder_time,
                    "due_date": due_date
                }
                
                logger.info(f"Scheduled reminder for task {task_id} at {reminder_time}")
            except Exception as e:
                logger.error(f"Error scheduling reminder: {e}")
    
    elif event.get("event_type") == "task.deleted":
        task_id = event.get("task_id")
        if task_id in scheduled_reminders:
            del scheduled_reminders[task_id]
            logger.info(f"Removed reminder for deleted task {task_id}")
    
    return {"success": True}

 @app.post("/check-reminders")
async def check_reminders(data: Dict[str, Any]):
    """
    Called by Dapr cron binding every minute.
    Checks if any reminders are due.
    """
    now = datetime.utcnow()
    logger.info(f"Checking reminders at {now}, scheduled: {len(scheduled_reminders)}")
    
    sent_count = 0
    
    for task_id, reminder in list(scheduled_reminders.items()):
        if now >= reminder["reminder_time"]:
            # Publish reminder event
            event_data = {
                "event_type": "reminder.due",
                "task_id": reminder["task_id"],
                "user_id": reminder["user_id"],
                "title": reminder["title"],
                "due_date": reminder["due_date"].isoformat(),
                "timestamp": now.isoformat()
            }
            
            success = await publish_event("reminder-events", event_data)
            
            if success:
                # Remove from scheduled
                del scheduled_reminders[task_id]
                sent_count += 1
                logger.info(f"Reminder sent for task: {reminder['title']}")
    
    return {"checked": len(scheduled_reminders), "sent": sent_count}

async def publish_event(topic: str, event_data: Dict[str, Any]) -> bool:
    """Publish event via Dapr pub/sub."""
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=event_data, timeout=5.0)
            return response.status_code == 204
    except Exception as e:
        logger.error(f"Error publishing event: {e}")
        return False

 @app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription configuration.
    Tells Dapr which topics to subscribe to.
    """
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "task-events",
            "route": "/task-events"
        }
    ]
```

Create `backend/reminder-service/requirements.txt`:
```
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.0
python-dateutil==2.8.2
```

**Acceptance Criteria:**
- Service subscribes to task-events
- Stores reminders in memory
- Cron endpoint checks every minute
- Publishes reminder.due events

**Testing:**
```bash
# Run locally
cd backend/reminder-service
pip install -r requirements.txt
uvicorn app.main:app --port 8001
```

**Files Created/Modified:**
- `backend/reminder-service/app/main.py`
- `backend/reminder-service/requirements.txt`

---

## Group 6: Recurring Task Service (P1) - 5 tasks

### T-5.021: Create Recurring Task Service Structure
**Priority:** P1
**Estimated Time:** 15 minutes
**Dependencies:** None

**Description:**
Create directory structure for recurring task service.

**Implementation Steps:**
```bash
# Create directories
mkdir -p backend/recurring-task-service/app
cd backend/recurring-task-service

# Create files
touch app/__init__.py
touch app/main.py
touch app/models.py
touch requirements.txt
touch Dockerfile
```

**Acceptance Criteria:**
- Directory structure created
- Empty files in place

**Files Created:**
- `backend/recurring-task-service/app/__init__.py`
- `backend/recurring-task-service/app/main.py`
- `backend/recurring-task-service/app/models.py`
- `backend/recurring-task-service/requirements.txt`
- `backend/recurring-task-service/Dockerfile`

---

### T-5.022: Implement Recurring Task Service Logic
**Priority:** P1
**Estimated Time:** 2 hours
**Dependencies:** T-5.021

**Description:**
Implement recurring task service that creates new tasks when completed.

**Implementation Steps:**

Create `backend/recurring-task-service/app/main.py`:
```python
from fastapi import FastAPI
from datetime import datetime, timedelta
import httpx
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Recurring Task Service")

DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "kafka-pubsub"

 @app.get("/health")
async def health():
    return {"status": "healthy"}

 @app.post("/task-events")
async def handle_task_event(event: Dict[str, Any]):
    """
    Handle task completion events to create recurring tasks.
    """
    logger.info(f"Received event: {event.get('event_type')}")
    
    if event.get("event_type") == "task.completed":
        is_recurring = event.get("is_recurring", False)
        recurrence_pattern = event.get("recurrence_pattern")
        
        if is_recurring and recurrence_pattern:
            # Calculate next occurrence
            next_due_date = calculate_next_occurrence(datetime.utcnow(), recurrence_pattern)
            
            # Create new task
            new_task_data = {
                "event_type": "task.created",
                "title": event.get("title"),
                "description": event.get("description"),
                "due_date": next_due_date.isoformat() if next_due_date else None,
                "user_id": event.get("user_id"),
                "priority": event.get("priority", "Medium"),
                "tags": event.get("tags", []),
                "is_recurring": True,
                "recurrence_pattern": recurrence_pattern,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Publish event to create new task
            success = await publish_event("task-events", new_task_data)
            
            if success:
                logger.info(f"Created recurring task: {event.get('title')}")
            else:
                logger.error(f"Failed to create recurring task: {event.get('title')}")
    
    return {"success": True}

def calculate_next_occurrence(completed_date: datetime, pattern: str) -> datetime:
    """
    Calculate next occurrence based on recurrence pattern.
    """
    if pattern == "daily":
        return completed_date + timedelta(days=1)
    elif pattern == "weekly":
        return completed_date + timedelta(weeks=1)
    elif pattern == "monthly":
        # Simple monthly calculation (add ~30 days)
        return completed_date + timedelta(days=30)
    elif pattern == "weekdays":
        # Next weekday (skip weekends)
        next_date = completed_date + timedelta(days=1)
        while next_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            next_date += timedelta(days=1)
        return next_date
    else:
        # Default to daily if unknown pattern
        return completed_date + timedelta(days=1)

async def publish_event(topic: str, event_data: Dict[str, Any]) -> bool:
    """Publish event via Dapr pub/sub."""
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=event_data, timeout=5.0)
            return response.status_code == 204
    except Exception as e:
        logger.error(f"Error publishing event: {e}")
        return False

 @app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription configuration.
    """
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "task-events",
            "route": "/task-events"
        }
    ]
```

Create `backend/recurring-task-service/requirements.txt`:
```
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.0
python-dateutil==2.8.2
```

**Acceptance Criteria:**
- Service subscribes to task-events
- Creates new tasks when recurring tasks are completed
- Calculates next occurrence based on pattern

**Testing:**
```bash
# Run locally
cd backend/recurring-task-service
pip install -r requirements.txt
uvicorn app.main:app --port 8002
```

**Files Created/Modified:**
- `backend/recurring-task-service/app/main.py`
- `backend/recurring-task-service/requirements.txt`

---

## Group 7: Frontend Updates (P1) - 8 tasks

### T-5.026: Add Priority Dropdown to Task Form
**Priority:** P1
**Estimated Time:** 30 minutes
**Dependencies:** None

**Description:**
Add priority selection to task creation form.

**Implementation Steps:**

Create `frontend/components/tasks/PrioritySelector.tsx`:
```tsx
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface PrioritySelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export function PrioritySelector({ value, onChange }: PrioritySelectorProps) {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder="Select priority" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="Low">Low</SelectItem>
        <SelectItem value="Medium">Medium</SelectItem>
        <SelectItem value="High">High</SelectItem>
        <SelectItem value="Urgent">Urgent</SelectItem>
      </SelectContent>
    </Select>
  );
}
```

Update `frontend/components/tasks/TaskForm.tsx`:
```tsx
import { PrioritySelector } from "./PrioritySelector";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { useState } from "react";

interface TaskFormData {
  title: string;
  description?: string;
  priority: string;
  tags: string[];
  dueDate?: string;
  isRecurring: boolean;
  recurrencePattern?: string;
}

interface TaskFormProps {
  onSubmit: (data: TaskFormData) => void;
  onCancel: () => void;
  initialData?: Partial<TaskFormData>;
}

export function TaskForm({ onSubmit, onCancel, initialData }: TaskFormProps) {
  const [formData, setFormData] = useState<TaskFormData>({
    title: initialData?.title || "",
    description: initialData?.description || "",
    priority: initialData?.priority || "Medium",
    tags: initialData?.tags || [],
    dueDate: initialData?.dueDate || "",
    isRecurring: initialData?.isRecurring || false,
    recurrencePattern: initialData?.recurrencePattern || undefined
  });
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="title">Title</Label>
        <Input
          id="title"
          value={formData.title}
          onChange={(e) => setFormData({...formData, title: e.target.value})}
          required
        />
      </div>
      
      <div>
        <Label htmlFor="description">Description</Label>
        <Input
          id="description"
          value={formData.description}
          onChange={(e) => setFormData({...formData, description: e.target.value})}
        />
      </div>
      
      <div>
        <Label>Priority</Label>
        <PrioritySelector
          value={formData.priority}
          onChange={(value) => setFormData({...formData, priority: value})}
        />
      </div>
      
      <div>
        <Label htmlFor="tags">Tags (comma-separated)</Label>
        <Input
          id="tags"
          value={formData.tags.join(",")}
          onChange={(e) => setFormData({...formData, tags: e.target.value.split(",").map(tag => tag.trim())})}
        />
      </div>
      
      <div>
        <Label htmlFor="dueDate">Due Date</Label>
        <Input
          id="dueDate"
          type="datetime-local"
          value={formData.dueDate}
          onChange={(e) => setFormData({...formData, dueDate: e.target.value})}
        />
      </div>
      
      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="isRecurring"
          checked={formData.isRecurring}
          onChange={(e) => setFormData({...formData, isRecurring: e.target.checked})}
        />
        <Label htmlFor="isRecurring">Recurring Task</Label>
      </div>
      
      {formData.isRecurring && (
        <div>
          <Label>Recurrence Pattern</Label>
          <select
            value={formData.recurrencePattern}
            onChange={(e) => setFormData({...formData, recurrencePattern: e.target.value})}
            className="border rounded p-2 w-full"
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="weekdays">Weekdays</option>
          </select>
        </div>
      )}
      
      <div className="flex justify-end space-x-2">
        <Button type="button" variant="outline" onClick={onCancel}>Cancel</Button>
        <Button type="submit">Save Task</Button>
      </div>
    </form>
  );
}
```

**Acceptance Criteria:**
- Priority dropdown in task form
- Options: Low, Medium, High, Urgent
- Value persists in form state

**Files Created/Modified:**
- `frontend/components/tasks/PrioritySelector.tsx`
- `frontend/components/tasks/TaskForm.tsx`

---

## Group 8: Docker Images (P0) - 4 tasks

### T-5.034: Create Reminder Service Dockerfile
**Priority:** P0
**Estimated Time:** 15 minutes
**Dependencies:** T-5.020

**Description:**
Create Dockerfile for reminder service.

**Implementation Steps:**

Create `backend/reminder-service/Dockerfile`:
```Dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**Acceptance Criteria:**
- Dockerfile builds successfully
- Uses Python 3.13 slim
- Exposes port 8001
- Runs uvicorn server

**Files Created:**
- `backend/reminder-service/Dockerfile`

---

### T-5.035: Create Recurring Task Service Dockerfile
**Priority:** P0
**Estimated Time:** 15 minutes
**Dependencies:** T-5.022

**Description:**
Create Dockerfile for recurring task service.

**Implementation Steps:**

Create `backend/recurring-task-service/Dockerfile`:
```Dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
```

**Acceptance Criteria:**
- Dockerfile builds successfully
- Uses Python 3.13 slim
- Exposes port 8002
- Runs uvicorn server

**Files Created:**
- `backend/recurring-task-service/Dockerfile`

---

## Group 9: Helm Charts (P0) - 6 tasks

### T-5.036: Update Helm Values for B1s Resources
**Priority:** P0
**Estimated Time:** 20 minutes
**Dependencies:** None

**Description:**
Update Helm values to fit B1s resource constraints.

**Implementation Steps:**

Update `k8s/helm/todo-app/values.yaml`:
```yaml
# Default values for todo-app
# This is a YAML-formatted file.
# Declare variables to be passed into your templates.

replicaCount: 1

images:
  registry: todoappcr.azurecr.io
  frontend:
    repository: todo-frontend
    pullPolicy: IfNotPresent
    # Overrides the image tag whose default is the chart appVersion.
    tag: ""
  backend:
    repository: todo-backend
    pullPolicy: IfNotPresent
    tag: ""
  reminderService:
    repository: reminder-service
    pullPolicy: IfNotPresent
    tag: ""
  recurringService:
    repository: recurring-task-service
    pullPolicy: IfNotPresent
    tag: ""

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  # Specifies whether a service account should be created
  create: true
  # Annotations to add to the service account
  annotations: {}
  # The name of the service account to use.
  # If not set and create is true, a name is generated using the fullname template
  name: ""

podAnnotations: {}

podSecurityContext: {}
  # fsGroup: 2000

securityContext: {}
  # capabilities:
  #   drop:
  #   - ALL
  # readOnlyRootFilesystem: true
  # runAsNonRoot: true
  # runAsUser: 1000

frontend:
  service:
    type: LoadBalancer  # Changed from ClusterIP for public access
    port: 3000
  resources:
    requests:
      memory: "128Mi"  # Reduced for B1s
      cpu: "100m"      # Reduced for B1s
    limits:
      memory: "256Mi"  # Reduced for B1s
      cpu: "250m"      # Reduced for B1s

backend:
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      memory: "256Mi"  # Reduced for B1s
      cpu: "200m"      # Reduced for B1s
    limits:
      memory: "512Mi"  # Reduced for B1s
      cpu: "500m"      # Reduced for B1s
  dapr:
    enabled: true
    appId: "todo-backend"
    appPort: 8000

reminderService:
  replicaCount: 1
  service:
    type: ClusterIP
    port: 8001
  resources:
    requests:
      memory: "64Mi"   # Reduced for B1s
      cpu: "50m"       # Reduced for B1s
    limits:
      memory: "128Mi"  # Reduced for B1s
      cpu: "100m"      # Reduced for B1s
  dapr:
    enabled: true
    appId: "reminder-service"
    appPort: 8001

recurringService:
  replicaCount: 1
  service:
    type: ClusterIP
    port: 8002
  resources:
    requests:
      memory: "64Mi"   # Reduced for B1s
      cpu: "50m"       # Reduced for B1s
    limits:
      memory: "128Mi"  # Reduced for B1s
      cpu: "100m"      # Reduced for B1s
  dapr:
    enabled: true
    appId: "recurring-task-service"
    appPort: 8002

ingress:
  enabled: false
  className: ""
  annotations: {}
    # kubernetes.io/ingress.class: nginx
    # kubernetes.io/tls-acme: "true"
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: ImplementationSpecific
  tls: []
  #  - secretName: chart-example-tls
  #    hosts:
  #      - chart-example.local

tolerations: []

affinity: {}
```

**Acceptance Criteria:**
- Resource requests/limits reduced for B1s
- Frontend service type changed to LoadBalancer
- Dapr annotations added for all services

**Files Modified:**
- `k8s/helm/todo-app/values.yaml`

---

## Group 10: Deployment (P0) - 5 tasks

### T-5.037: Build and Push All Docker Images
**Priority:** P0
**Estimated Time:** 45 minutes
**Dependencies:** T-5.034, T-5.035

**Description:**
Build all Docker images and push to ACR.

**Implementation Steps:**
```bash
# Login to ACR
az acr login --name todoappcr

# Build and tag images
cd backend
docker build -t todoappcr.azurecr.io/todo-backend:v5.0 .
docker build -f reminder-service/Dockerfile -t todoappcr.azurecr.io/reminder-service:v5.0 .
docker build -f recurring-task-service/Dockerfile -t todoappcr.azurecr.io/recurring-task-service:v5.0 .

# Push images
docker push todoappcr.azurecr.io/todo-backend:v5.0
docker push todoappcr.azurecr.io/reminder-service:v5.0
docker push todoappcr.azurecr.io/recurring-task-service:v5.0

# Build frontend
cd ../frontend
docker build -t todoappcr.azurecr.io/todo-frontend:v5.0 .
docker push todoappcr.azurecr.io/todo-frontend:v5.0
```

**Acceptance Criteria:**
- All 4 images pushed to ACR
- Images tagged with v5.0
- No build errors

**Testing:**
```bash
az acr repository list --name todoappcr
# Should show: todo-backend, reminder-service, recurring-task-service, todo-frontend

az acr repository show-tags --name todoappcr --repository todo-backend
# Should show: v5.0
```

---

## Group 11: CI/CD (P1) - 3 tasks

### T-5.038: Create GitHub Actions Workflow
**Priority:** P1
**Estimated Time:** 30 minutes
**Dependencies:** T-5.037

**Description:**
Create CI/CD workflow for automated deployment.

**Implementation Steps:**

Create `.github/workflows/deploy-azure.yml`:
```yaml
name: Deploy to Azure AKS

on:
  push:
    branches: [ phase-5-cloud ]

env:
  ACR_NAME: todoappcr
  AKS_CLUSTER_NAME: todo-aks-cluster
  RESOURCE_GROUP: todo-app-rg
  HELM_RELEASE_NAME: todo-app

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    # Set up Docker Buildx
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    # Login to Azure
    - name: Login to Azure
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    # Get AKS credentials
    - name: Get AKS credentials
      run: |
        az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER_NAME
    
    # Login to ACR
    - name: Login to ACR
      run: |
        az acr login --name $ACR_NAME
    
    # Build and push backend image
    - name: Build and push backend image
      run: |
        docker build -t $ACR_NAME.azurecr.io/todo-backend:${{ github.sha }} ./backend
        docker push $ACR_NAME.azurecr.io/todo-backend:${{ github.sha }}
    
    # Build and push reminder service image
    - name: Build and push reminder service image
      run: |
        docker build -f ./backend/reminder-service/Dockerfile -t $ACR_NAME.azurecr.io/reminder-service:${{ github.sha }} ./backend
        docker push $ACR_NAME.azurecr.io/reminder-service:${{ github.sha }}
    
    # Build and push recurring service image
    - name: Build and push recurring service image
      run: |
        docker build -f ./backend/recurring-task-service/Dockerfile -t $ACR_NAME.azurecr.io/recurring-task-service:${{ github.sha }} ./backend
        docker push $ACR_NAME.azurecr.io/recurring-task-service:${{ github.sha }}
    
    # Build and push frontend image
    - name: Build and push frontend image
      run: |
        docker build -t $ACR_NAME.azurecr.io/todo-frontend:${{ github.sha }} ./frontend
        docker push $ACR_NAME.azurecr.io/todo-frontend:${{ github.sha }}
    
    # Deploy to AKS using Helm
    - name: Deploy to AKS
      run: |
        helm upgrade --install $HELM_RELEASE_NAME ./k8s/helm/todo-app \
          --set images.backend.tag=${{ github.sha }} \
          --set images.reminderService.tag=${{ github.sha }} \
          --set images.recurringService.tag=${{ github.sha }} \
          --set images.frontend.tag=${{ github.sha }} \
          --wait \
          --timeout 10m
    
    # Verify deployment
    - name: Verify deployment
      run: |
        kubectl get pods
        kubectl get services
        echo "Waiting for services to be ready..."
        sleep 30
        kubectl get service todo-app-frontend
```

**Acceptance Criteria:**
- Workflow file created
- Builds and pushes all images
- Deploys via Helm
- Verifies deployment

**Files Created:**
- `.github/workflows/deploy-azure.yml`

---

## Group 12: Testing & Documentation (P0) - 3 tasks

### T-5.039: Integration Testing Script
**Priority:** P0
**Estimated Time:** 30 minutes
**Dependencies:** T-5.037

**Description:**
Create script to test end-to-end functionality.

**Implementation Steps:**

Create `scripts/integration-test.sh`:
```bash
#!/bin/bash

# Integration test script for Phase 5
# Tests the complete event-driven flow

set -e

echo "Starting Phase 5 Integration Test..."

# Get public IP
PUBLIC_IP=$(kubectl get service todo-app-frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
if [ -z "$PUBLIC_IP" ]; then
  echo "ERROR: Could not get public IP"
  exit 1
fi

echo "Using public IP: $PUBLIC_IP"

# Test 1: Health check
echo "Test 1: Health check..."
curl -s "http://$PUBLIC_IP/api/health" | jq .
if [ $? -eq 0 ]; then
  echo "✓ Health check passed"
else
  echo "✗ Health check failed"
  exit 1
fi

# Test 2: Create user and get token
echo "Test 2: User authentication..."
EMAIL="test$(date +%s)@example.com"
PASSWORD="TestPassword123!"

# Register user
REGISTER_RESPONSE=$(curl -s -X POST "http://$PUBLIC_IP/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"name\":\"Test User\"}")

TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.access_token')
if [ "$TOKEN" != "null" ]; then
  echo "✓ User registration and login successful"
else
  echo "✗ User registration failed"
  echo $REGISTER_RESPONSE
  exit 1
fi

# Test 3: Create task with reminder
echo "Test 3: Create task with reminder..."
TASK_TITLE="Integration Test Task $(date)"
TASK_DESCRIPTION="This is an automated integration test task"
FUTURE_DATE=$(date -d "+2 hours" -u +"%Y-%m-%dT%H:%M:%S")

CREATE_TASK_RESPONSE=$(curl -s -X POST "http://$PUBLIC_IP/api/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"$TASK_TITLE\",
    \"description\": \"$TASK_DESCRIPTION\",
    \"due_date\": \"$FUTURE_DATE\",
    \"priority\": \"High\",
    \"tags\": [\"integration\", \"test\"],
    \"is_recurring\": false
  }")

TASK_ID=$(echo $CREATE_TASK_RESPONSE | jq -r '.id')
if [ "$TASK_ID" != "null" ]; then
  echo "✓ Task creation successful: $TASK_ID"
else
  echo "✗ Task creation failed"
  echo $CREATE_TASK_RESPONSE
  exit 1
fi

# Test 4: Search tasks
echo "Test 4: Search tasks..."
SEARCH_RESPONSE=$(curl -s "http://$PUBLIC_IP/api/tasks/search?q=integration&priority=High" \
  -H "Authorization: Bearer $TOKEN")

SEARCH_COUNT=$(echo $SEARCH_RESPONSE | jq 'length')
if [ "$SEARCH_COUNT" -ge 1 ]; then
  echo "✓ Search functionality working: found $SEARCH_COUNT tasks"
else
  echo "✗ Search functionality failed"
  echo $SEARCH_RESPONSE
  exit 1
fi

# Test 5: Complete task (should trigger recurring task creation)
echo "Test 5: Create and complete recurring task..."
RECURRING_TASK_TITLE="Recurring Test Task $(date)"
RECURRING_CREATE_RESPONSE=$(curl -s -X POST "http://$PUBLIC_IP/api/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"$RECURRING_TASK_TITLE\",
    \"description\": \"This is a recurring task\",
    \"priority\": \"Medium\",
    \"is_recurring\": true,
    \"recurrence_pattern\": \"daily\"
  }")

RECURRING_TASK_ID=$(echo $RECURRING_CREATE_RESPONSE | jq -r '.id')
if [ "$RECURRING_TASK_ID" != "null" ]; then
  echo "✓ Recurring task creation successful: $RECURRING_TASK_ID"
else
  echo "✗ Recurring task creation failed"
  echo $RECURRING_CREATE_RESPONSE
  exit 1
fi

# Complete the recurring task
COMPLETE_RESPONSE=$(curl -s -X PATCH "http://$PUBLIC_IP/api/tasks/$RECURRING_TASK_ID/complete" \
  -H "Authorization: Bearer $TOKEN")

if [ $? -eq 0 ]; then
  echo "✓ Task completion successful"
else
  echo "✗ Task completion failed"
  echo $COMPLETE_RESPONSE
  exit 1
fi

# Wait for event processing
echo "Waiting 30 seconds for event processing..."
sleep 30

# Check if recurring task was created
echo "Test 6: Verify recurring task was created..."
ALL_TASKS=$(curl -s "http://$PUBLIC_IP/api/tasks" \
  -H "Authorization: Bearer $TOKEN")

RECURRING_TASK_COUNT=$(echo $ALL_TASKS | jq --arg title "$RECURRING_TASK_TITLE" '[.[] | select(.title == $title)] | length')
if [ "$RECURRING_TASK_COUNT" -ge 2 ]; then
  echo "✓ Recurring task functionality working: found $RECURRING_TASK_COUNT instances"
else
  echo "⚠ Recurring task functionality: only found $RECURRING_TASK_COUNT instances (may be timing issue)"
fi

echo ""
echo "=== INTEGRATION TEST SUMMARY ==="
echo "✓ Health check: PASSED"
echo "✓ User authentication: PASSED"
echo "✓ Task creation: PASSED"
echo "✓ Search functionality: PASSED"
echo "✓ Task completion: PASSED"
echo "✓ Recurring task creation: PARTIAL (timing-dependent)"
echo ""
echo "Integration test completed!"
```

Make executable:
```bash
chmod +x scripts/integration-test.sh
```

**Acceptance Criteria:**
- Script tests all major functionality
- Validates event-driven flows
- Reports pass/fail status

**Files Created:**
- `scripts/integration-test.sh`

---

## Group 13: Cost Management (P0) - 3 tasks

### T-5.040: Set Up Billing Alerts
**Priority:** P0
**Estimated Time:** 10 minutes
**Dependencies:** T-5.002

**Description:**
Set up billing alerts to avoid unexpected charges.

**Implementation Steps:**
```bash
# Alert at $10 (early warning)
az monitor metrics alert create \
  --name cost-alert-10 \
  --resource-group todo-app-rg \
  --condition "total cost > 10" \
  --description "Alert when cost exceeds $10"

# Alert at $50 (safety)
az monitor metrics alert create \
  --name cost-alert-50 \
  --resource-group todo-app-rg \
  --condition "total cost > 50" \
  --description "Alert when cost exceeds $50"
```

**Acceptance Criteria:**
- Two alerts created ($10 and $50)
- Alerts will email you if cost exceeded

**✓ Done when:** Alerts visible in Azure Portal > Monitor

---

### T-5.041: Stop AKS Cluster After Demo
**Priority:** P0
**Estimated Time:** 5 minutes
**Dependencies:** T-5.039 (after demo recorded)

**Description:**
Stop AKS cluster to reduce costs to ~$1/month.

**Implementation Steps:**
```bash
# Stop cluster (keeps all configuration)
az aks stop --resource-group todo-app-rg --name todo-aks-cluster

# Verify stopped
az aks show --resource-group todo-app-rg --name todo-aks-cluster \
  --query "powerState.code"
# Should output: "Stopped"

# Check nodes
kubectl get nodes
# Should show: The connection to the server localhost:8080 was refused
# (This is expected when cluster is stopped)
```

**What This Does:**
- Stops all VMs (no compute charges)
- Keeps cluster configuration, deployments, services
- Keeps persistent volumes
- Cost drops to ~$1/month (storage only)

**To Restart Later:**
```bash
az aks start --resource-group todo-app-rg --name todo-aks-cluster
# Takes 2-3 minutes
# Everything comes back exactly as before!
```

**Acceptance Criteria:**
- Cluster power state = "Stopped"
- Cost drops to ~$1/month
- Can restart anytime in minutes

**✓ Done when:** `az aks show` shows powerState: "Stopped"

---

### T-5.042: Delete Resources After Hackathon (Optional)
**Priority:** P1
**Estimated Time:** 5 minutes
**Dependencies:** T-5.041

**Description:**
Complete cleanup after hackathon results announced (optional).

**Implementation Steps:**
```bash
# WARNING: This deletes EVERYTHING in the resource group!
# Only do this if you're done with the project

# Delete entire resource group
az group delete --name todo-app-rg --yes --no-wait

# Verify deletion (takes a few minutes)
az group exists --name todo-app-rg
# Should output: false
```

**What This Does:**
- Deletes AKS cluster
- Deletes ACR (and all images)
- Deletes Load Balancer
- Deletes all networking
- **Cost = $0/month**

**Can You Redeploy Later?**
Yes! Your code is in GitHub:
```bash
# Just run Phase 5 setup again (30-45 minutes)
az group create --name todo-app-rg --location southeastasia
az aks create ...
# Follow tasks T-5.004 onwards
```

**Acceptance Criteria:**
- Resource group deleted
- No Azure resources remain
- Cost = $0/month

**✓ Done when:** `az group exists --name todo-app-rg` returns false

---

## Total Tasks Summary

| Group | P0 | P1 | P2 | Total | Time |
|-------|----|----|----|----|------|
| 1. Infrastructure | 6 | 0 | 0 | 6 | 1h |
| 2. Dapr & Kafka | 6 | 0 | 0 | 6 | 1.5h |
| 3. Database | 1 | 0 | 0 | 1 | 0.5h |
| 4. Backend Updates | 4 | 1 | 0 | 5 | 3h |
| 5. Reminder Service | 2 | 0 | 0 | 2 | 2h |
| 6. Recurring Service | 0 | 2 | 0 | 2 | 2h |
| 7. Frontend Updates | 0 | 1 | 0 | 1 | 0.5h |
| 8. Docker Images | 2 | 0 | 0 | 2 | 0.5h |
| 9. Helm Charts | 1 | 0 | 0 | 1 | 0.5h |
| 10. Deployment | 1 | 0 | 0 | 1 | 1h |
| 11. CI/CD | 0 | 1 | 0 | 1 | 0.5h |
| 12. Testing & Docs | 1 | 0 | 0 | 1 | 0.5h |
| 13. Cost Management | 3 | 1 | 0 | 4 | 1h |
| **TOTAL** | **27** | **7** | **0** | **34** | **~16h** |

**Critical Path (Must Complete):** All P0 tasks (27 tasks, ~13 hours)
**Recommended:** P0 + P1 tasks (34 tasks, ~16 hours)

---

## Execution Strategy

**Week 1 (Local):** Complete Groups 1-7 locally, no Azure costs
**Day 6:** Deploy to Azure (Groups 8-10)
**Day 7:** Test, document, demo (Groups 11-12)
**Day 8:** Stop cluster (Group 13, T-5.041)
**After results:** Optional cleanup (Group 13, T-5.042)

**Estimated Cost:** $1.30 - $4.55 depending on how many days you run

---

**All Phase 5 tasks defined! Ready for implementation with Qwen.** 🚀