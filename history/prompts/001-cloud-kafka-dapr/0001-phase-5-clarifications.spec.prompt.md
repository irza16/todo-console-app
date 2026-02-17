---
id: 0001
title: Phase-5-clarifications
stage: spec
date: 2026-02-11
surface: agent
model: google/gemini-2.0-flash-exp:free
feature: 001-cloud-kafka-dapr
branch: 001-cloud-kafka-dapr
user: irza
command: sp.clarify
labels: [spec,clarification,cost-optimization,azure,aks,kafka,dapr]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - /home/irza/projects/todo-console-app/specs/001-cloud-kafka-dapr/spec.md
tests:
  - null
---

## Prompt

# Phase 5 Specification Clarifications and Updates

## Purpose
This file contains updates and clarifications to the Phase 5 specification files (constitution, spec, plan, tasks) with focus on cost optimization and practical deployment strategy.

---

## 1. Cost Optimization Strategy

### Updates to Apply to ALL Spec Files

**REPLACE:** Original cost estimates of $80/month

**WITH:** Optimized cost strategy:

```
Cost Options:
1. Demo-Only (Recommended for Hackathon): $3-5 total for 7 days
2. Minimal VM (B1s): $20/month
3. Stopped Cluster: $1/month (storage only)
4. Full Production: $80/month

Recommended: Deploy → Demo → Stop → Keep $95 credit for future
```

**Specific Changes:**

### In Constitution (phase-5-constitution.md):

**Section: Cost Optimization (around line 100)**

ADD after existing cost section:
```markdown
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
```

### In Spec (phase-5-spec.md):

**Section: US-5.1: Create AKS Cluster**

REPLACE the Azure CLI command with:
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
```

**Update acceptance criteria:**
```
Acceptance Criteria:
- AKS cluster created with 1 node (demo config)
- Node is Standard_B1s (1 vCPU, 1GB RAM)
- Monitoring add-on enabled
- Kubernetes version 1.28+
- Cost: ~$0.33/day

Note: Will work for demo but may be slow. Can upgrade later.
```

### In Plan (phase-5-plan.md):

**ADD new section after "Cost Management":**

```markdown
## Demo Deployment Strategy (Hackathon Optimized)

### Timeline for Minimal Cost

**Day 1-5: Development and Testing (Local)**
- Work locally with Minikube/k3d
- Test all services with local Kafka + Dapr
- Build Docker images
- Cost: $0 (local only)

**Day 6: Deploy to Azure**
- Morning: Create AKS cluster (1x B1s node)
- Afternoon: Deploy all services
- Test everything works
- Cost: $0.65

**Day 7: Demo and Recording**
- Morning: Final testing
- Afternoon: Record demo video
- Evening: Submit hackathon
- Cost: $0.65
- **Total so far: $1.30**

**Day 8: Stop or Delete**

Option A - Stop Cluster (recommended):
```bash
az aks stop --resource-group todo-app-rg --name todo-aks-cluster
```
- Keeps all configuration
- Can restart anytime
- Cost: $1/month (storage only)

Option B - Delete Everything:
```bash
az group delete --name todo-app-rg --yes
```
- Removes all resources
- Cost: $0/month
- Can redeploy from GitHub later

**Total Cost:**
- 7 days deployment: $4.55
- Plus 1 month stopped: $1.00
- **Total: $5.55 from $100 credit**
- **Remaining: $94.45 for future projects!**

### Scaling Up After Hackathon (If Needed)

If you want to show employers or use for portfolio:

```bash
# Restart cluster
az aks start --resource-group todo-app-rg --name todo-aks-cluster

# Scale up to production config
az aks scale \
  --resource-group todo-app-rg \
  --name todo-aks-cluster \
  --node-count 2

az aks nodepool update \
  --resource-group todo-app-rg \
  --cluster-name todo-aks-cluster \
  --name nodepool1 \
  --node-vm-size Standard_B2s
```
```

---

## 2. Deployment Strategy Clarification

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

---

## 3. Resource Limits for B1s Nodes

### Pod Resource Adjustments

**UPDATE:** Reduce resource requests/limits for B1s compatibility

**In Helm values.yaml, REPLACE:**

```yaml
# OLD (for B2s nodes):
backend:
  resources:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "1Gi"
      cpu: "1000m"

# NEW (for B1s nodes):
backend:
  resources:
    requests:
      memory: "256Mi"  # Reduced
      cpu: "200m"      # Reduced
    limits:
      memory: "512Mi"  # Reduced
      cpu: "500m"      # Reduced

frontend:
  resources:
    requests:
      memory: "128Mi"  # Reduced
      cpu: "100m"      # Reduced
    limits:
      memory: "256Mi"  # Reduced
      cpu: "250m"      # Reduced

reminderService:
  resources:
    requests:
      memory: "64Mi"   # Reduced
      cpu: "50m"       # Reduced
    limits:
      memory: "128Mi"  # Reduced
      cpu: "100m"      # Reduced

recurringTaskService:
  resources:
    requests:
      memory: "64Mi"   # Reduced
      cpu: "50m"       # Reduced
    limits:
      memory: "128Mi"  # Reduced
      cpu: "100m"      # Reduced
```

**B1s Node Capacity:**
- Total CPU: 1000m (1 vCPU)
- Total Memory: 1GB (1024Mi)
- After system pods: ~700m CPU, ~700Mi memory available

**Our pods total (with new limits):**
- CPU requests: 400m (fits!)
- Memory requests: 500Mi (fits!)

---

## 4. Testing Strategy Update

### Local Testing First (Save Money)

**ADD to Plan:**

```markdown
## Pre-Azure Testing Checklist

BEFORE deploying to Azure (costs money), test EVERYTHING locally:

### Step 1: Local Kafka + Dapr
```bash
# Run Kafka locally
docker run -d --name kafka-local \
  -p 9092:9092 \
  bitnami/kafka:latest

# Initialize Dapr
dapr init

# Test each service with Dapr
cd backend
dapr run --app-id backend --app-port 8000 -- uvicorn app.main:app

cd reminder-service
dapr run --app-id reminder --app-port 8001 -- uvicorn app.main:app

cd recurring-task-service
dapr run --app-id recurring --app-port 8002 -- uvicorn app.main:app
```

### Step 2: Test Event Flow Locally
```bash
# Create task → should trigger events
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Test", "is_recurring":true, "recurrence_pattern":"daily"}'

# Check logs - should see events flowing
# Only deploy to Azure once this works!
```

### Step 3: Test with Minikube (Optional)
```bash
# Test Helm charts locally first
minikube start
helm install todo-app ./k8s/helm/todo-app --dry-run

# Only proceed to Azure if Minikube deployment works
```

**Benefit:** Catch all bugs locally (free) before deploying to Azure (costs money)
```

---

## 5. New Tasks for Cost Management

### ADD to Tasks File

**Group 13: Cost Management (P0) - 3 new tasks**

**T-5.056: Set Up Billing Alerts**
**Priority:** P0
**Time:** 10 minutes
**Dependencies:** T-5.002

```bash
# Set alert at $50 (safety)
az monitor metrics alert create \
  --name cost-alert-50 \
  --resource-group todo-app-rg \
  --condition "total cost > 50" \
  --description "Alert at $50"

# Set alert at $10 (early warning)
az monitor metrics alert create \
  --name cost-alert-10 \
  --resource-group todo-app-rg \
  --condition "total cost > 10" \
  --description "Alert at $10"
```

**T-5.057: Stop AKS Cluster After Demo**
**Priority:** P0
**Time:** 5 minutes
**Dependencies:** T-5.052 (after demo recorded)

```bash
# Stop cluster (keeps config, no charges)
az aks stop --resource-group todo-app-rg --name todo-aks-cluster

# Verify stopped
az aks show --resource-group todo-app-rg --name todo-aks-cluster \
  --query "powerState.code"
# Should output: "Stopped"

# Check cost (should drop to ~$1/month)
az consumption usage list --resource-group todo-app-rg
```

**T-5.058: Delete Resources After Hackathon**
**Priority:** P1
**Time:** 5 minutes
**Dependencies:** T-5.057

```bash
# After hackathon results announced (optional)
az group delete --name todo-app-rg --yes --no-wait

# Verify deletion
az group exists --name todo-app-rg
# Should output: false

# Final cost: $0/month
```

---

## 6. Demo Video Recording Checklist

### What to Show in Demo (< 90 seconds)

**ADD to Documentation:**

```markdown
## Demo Video Script (90 seconds)

**0:00-0:15 (15s): Introduction**
"Hi, this is my Phase 5 submission - deploying Todo AI Chatbot to Azure Kubernetes with event-driven architecture."

**0:15-0:30 (15s): Show Architecture**
[Screen: Architecture diagram]
"I deployed 4 microservices: Frontend, Backend API, Reminder Service, and Recurring Task Service, communicating via Kafka events."

**0:30-0:45 (15s): Show Azure Portal**
[Screen: Azure Portal showing AKS cluster]
"Running on Azure Kubernetes Service with Dapr for distributed application runtime."

**0:45-1:00 (15s): Show Application**
[Screen: Open browser to http://<public-ip>]
"Application is publicly accessible. Here I'll create a recurring task with high priority and tags."

**1:00-1:15 (15s): Demo Features**
[Screen: Create task, mark complete, show new task auto-created]
"When I complete this recurring task, the Recurring Task Service automatically creates the next occurrence via Kafka events."

**1:15-1:30 (15s): Show Logs/Monitoring**
[Screen: kubectl logs or Azure Monitor]
"All services are running, events flowing through Kafka, and monitored via Azure Monitor."

**1:30 (End)**
"Thank you! Code and deployment instructions are on GitHub."

[Show GitHub repo URL on screen]
```

---

## 7. Troubleshooting Updates

### Common Issues with B1s Nodes

**ADD to Troubleshooting section:**

```markdown
## B1s Node Limitations

### Issue: Pods Pending Due to Insufficient Resources

**Symptoms:**
```bash
kubectl get pods
# NAME                     READY   STATUS    RESTARTS
# backend-xxx              0/1     Pending   0
```

**Cause:** B1s has only 1 vCPU, 1GB RAM. Not enough for all pods.

**Solutions:**

Option 1 - Reduce replicas (quick fix):
```yaml
# In values.yaml
frontend:
  replicaCount: 1  # Instead of 2
backend:
  replicaCount: 1  # Instead of 2
```

Option 2 - Scale to 2 nodes (costs more):
```bash
az aks scale --resource-group todo-app-rg \
  --name todo-aks-cluster --node-count 2
# Cost doubles to ~$20/month
```

Option 3 - Upgrade node size (costs more):
```bash
# Create new nodepool with B2s
az aks nodepool add \
  --cluster-name todo-aks-cluster \
  --resource-group todo-app-rg \
  --name nodepool2 \
  --node-vm-size Standard_B2s \
  --node-count 1

# Migrate pods to new pool
# Delete old pool
az aks nodepool delete --name nodepool1 ...
```

### Issue: Kafka Fails to Start (OOM)

**Symptoms:** Kafka pod keeps restarting

**Cause:** Kafka needs ~512MB minimum

**Solution:** Reduce Kafka resources or increase node size
```yaml
# For B1s, use minimal Kafka config
helm install kafka bitnami/kafka \
  --set resources.requests.memory=256Mi \
  --set resources.limits.memory=512Mi
```

### Issue: Application Slow

**Expected:** B1s is smallest VM, will be slower than B2s

**For Demo:** This is fine! Judges understand resource constraints.

**For Production:** Upgrade to B2s or higher.
```

---

## 8. GitHub Repository Organization

### Branch Strategy Clarification

**ADD to Documentation:**

```markdown
## Git Branch Strategy

### Repository Structure
```
main (Phase 3 - Vercel + Hugging Face)
├── phase-4-kubernetes (Minikube deployment)
└── phase-5-cloud (Azure AKS deployment)
```

### Working on Phase 5
```bash
# Start from Phase 4 branch
git checkout phase-4-kubernetes

# Create Phase 5 branch
git checkout -b phase-5-cloud

# Work on Phase 5
# ... make changes ...

# Commit regularly
git add .
git commit -m "feat: add reminder service"

# Push to GitHub
git push origin phase-5-cloud
```

### After Hackathon

**Keep all branches:**
- `main`: Original Phase 3 (free, runs forever)
- `phase-4-kubernetes`: Minikube deployment
- `phase-5-cloud`: Azure deployment (stopped/deleted)

**For Portfolio:**
Show employers all 3 branches as progression:
1. "Started with Vercel deployment"
2. "Learned Kubernetes with Minikube"
3. "Deployed to production Azure cloud"
```

---

## 9. Environment Variables Management

### Secrets Strategy Across Deployments

**CLARIFY:** Same database, different deployments

```markdown
## Environment Variables Across Deployments

### Shared (Same for all deployments):
```bash
DATABASE_URL="postgresql://..." # Neon DB (same)
JWT_SECRET="your-secret"         # Same secret
```

### Different (Per deployment):
```bash
# Phase 3 (Vercel)
NEXT_PUBLIC_API_URL="https://your-hf-space.hf.space"

# Phase 5 (Azure)
NEXT_PUBLIC_API_URL="http://<azure-public-ip>:8000"
```

### Setting in Azure
```bash
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

## 10. Success Metrics Update

### Realistic Metrics for B1s Deployment

**UPDATE in all spec files:**

```markdown
## Success Metrics (B1s Demo Configuration)

### Technical Metrics
| Metric | Target (B1s) | Measurement |
|--------|--------------|-------------|
| API Latency (p95) | < 500ms | Azure Monitor (slower than B2s) |
| Event Processing | < 30s | Log timestamps (slower) |
| Pod Restart Rate | < 3/hour | kubectl get pods |
| Service Uptime | > 95% | Demo period only |
| Resource Utilization | 70-90% | kubectl top (higher on B1s) |

### Feature Metrics
| Feature | Success Criteria |
|---------|------------------|
| Create Task | Works with priority/tags |
| Search | Returns results in < 2s |
| Reminders | Fire within 5 min of due time (slower) |
| Recurring Tasks | Auto-create within 1 min |
| Public Access | Website loads via Azure IP |

### Demo Metrics (Most Important)
- [ ] Can access via public IP
- [ ] Can create task with priority and tags
- [ ] Can search and filter tasks
- [ ] Recurring task auto-creates when completed
- [ ] All services showing in kubectl get pods
- [ ] Kafka topics exist and have messages
- [ ] Demo video < 90 seconds
- [ ] Costs < $5 for demo period

**Note:** Performance is lower on B1s but FUNCTIONALITY is identical.
Judges care about working features, not speed.
```

---

## Summary of All Changes

### Files to Update:

1. **phase-5-constitution.md**
   - Add cost optimization section
   - Add demo strategy

2. **phase-5-spec.md**
   - Update US-5.1 (AKS creation) to B1s
   - Add cost estimates to each US
   - Update resource requirements

3. **phase-5-plan.md**
   - Add demo deployment timeline
   - Add stop/delete instructions
   - Update resource limits for B1s
   - Add local testing strategy

4. **phase-5-tasks.md**
   - Update T-5.004 (AKS creation command)
   - Add T-5.056 (billing alerts)
   - Add T-5.057 (stop cluster)
   - Add T-5.058 (delete resources)
   - Update all Helm chart tasks with reduced resources

### Key Changes:
- ✅ 1 node (B1s) instead of 2 nodes (B2s)
- ✅ Reduced resource requests/limits
- ✅ Stop cluster after demo
- ✅ Total cost: $3-5 for hackathon
- ✅ Keep $95+ credit for future

---

**Apply these clarifications to create final, optimized Phase 5 specs!**

## Response snapshot

I've successfully applied the clarifications to the Phase 5 specification file, focusing on cost optimization and practical deployment strategy for the hackathon. Key changes made:

1. Updated AKS cluster creation to use 1 node (Standard_B1s) instead of 2 nodes (Standard_B2s) for cost optimization (~$0.33/day vs ~$0.66/day)
2. Adjusted resource allocations for all services to fit within B1s constraints:
   - Frontend: 128Mi/100m (was 256Mi/250m)
   - Backend: 256Mi/200m (was 512Mi/500m)
   - Reminder Service: 64Mi/50m (was 256Mi/250m)
   - Recurring Task Service: 64Mi/50m (was 256Mi/250m)
3. Added clarifications section documenting the decisions made
4. Updated acceptance criteria in User Story 1 to reflect single node configuration
5. Modified Helm chart values to include reduced resource requests/limits
6. Added cost optimization strategy section with hackathon demo approach
7. Included deployment strategy section clarifying parallel deployments
8. Added environment variables management section

These changes align with the cost optimization strategy mentioned in the user's clarifications document, keeping the total cost under $5 for the 7-day hackathon period while maintaining all core functionality.

## Outcome

- ✅ Impact: Applied cost optimization changes to reduce Azure expenses for hackathon demo
- 🧪 Tests: null
- 📁 Files: Updated /home/irza/projects/todo-console-app/specs/001-cloud-kafka-dapr/spec.md
- 🔁 Next prompts: Proceed to implementation planning
- 🧠 Reflection: Cost optimization successfully balanced with functional requirements

## Evaluation notes (flywheel)

- Failure modes observed: null
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null