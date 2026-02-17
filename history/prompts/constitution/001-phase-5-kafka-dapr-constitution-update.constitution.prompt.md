---
id: 001
title: Phase 5 Kafka Dapr Constitution Update
stage: constitution
date_iso: 2026-02-11
surface: agent
model: google/gemini-2.0-flash-exp:free
feature: none
branch: phase-4-kubernetes
user: irza
command: /sp.constitution
labels:
  - constitution
  - kafka
  - dapr
  - cloud-deployment
  - event-driven
links:
  SPEC: null
  TICKET: null
  ADR: null
  PR: null
files_yaml:
  - .specify/memory/constitution.md
tests_yaml:
  - constitution update
  - event-driven architecture
  - dapr integration
  - cloud deployment
---

# Phase 5 Kafka Dapr Constitution Update

## User Input

```text
# Phase 5: Cloud Deployment with Kafka & Dapr - Constitution

## Purpose
Define the foundational principles, architectural decisions, and constraints for deploying the Todo AI Chatbot to production cloud infrastructure with event-driven architecture using Kafka and Dapr.

## Core Principles

### 1. Cloud-Native Production Readiness
- Application must run on real cloud infrastructure (OKE/GKE/AKS)
- Must handle production-level traffic and failures gracefully
- Zero-downtime deployments via rolling updates
- Auto-scaling based on load
- Production-grade monitoring and logging

### 2. Event-Driven Architecture
- Services communicate asynchronously via events
- Loose coupling between components
- Event sourcing for critical operations
- Eventual consistency is acceptable
- Events are immutable and append-only

### 3. Microservices Principles
- Single Responsibility: Each service does one thing well
- Independent Deployment: Services deploy independently
- Data Isolation: Each service owns its data
- API Contracts: Well-defined interfaces between services
- Failure Isolation: One service failure doesn't cascade

### 4. Cost Optimization
- Use free tiers wherever possible
- Auto-scale down to zero during idle periods (if supported)
- Optimize resource requests to minimize waste
- Use spot/preemptible instances where appropriate
- Monitor cloud costs actively

### 5. Security First
- Secrets managed via Kubernetes Secrets + Cloud Secret Manager
- Network policies restrict inter-service communication
- TLS for all external communication
- Pod Security Standards enforced
- No hardcoded credentials anywhere

## Technology Constraints

### Required Technologies

#### Cloud Infrastructure
- **Primary Options:**
  - Oracle Cloud (OKE) - Recommended for always-free tier
  - Google Cloud (GKE) - $300 credit for 90 days
  - Azure (AKS) - $200 credit for 30 days
- **Constraints:**
  - Must use managed Kubernetes service
  - No bare VMs or self-managed clusters
  - Must support LoadBalancer service type

#### Event Streaming
- **Primary Options:**
  - Redpanda Serverless (recommended - free tier)
  - Confluent Cloud (trial credits)
  - Self-hosted Kafka in Kubernetes (free but complex)
- **Constraints:**
  - Must be Kafka-compatible API
  - Support for at least 3 topics
  - Minimum 7-day retention

#### Distributed Application Runtime
- **Required:** Dapr 1.12+
- **Components:**
  - Pub/Sub (Kafka integration)
  - State Management (PostgreSQL)
  - Bindings (Cron for scheduled tasks)
  - Secrets (Kubernetes/Cloud integration)
  - Service Invocation (service-to-service calls)

#### Database
- **Continue Using:** Neon Serverless PostgreSQL (from Phase 2)
- **No Migration Needed:** Same database, new access patterns

### Forbidden Technologies
- Self-managed Kubernetes clusters (too complex)
- Non-managed databases (use Neon)
- Proprietary cloud services (stay cloud-agnostic where possible)
- Synchronous HTTP between all services (use events)

## Architecture Decisions

### AD-001: Three-Service Architecture
**Decision:** Split into Frontend, Backend API, and Event Processors
**Rationale:**
- Frontend: User interface (Next.js)
- Backend API: REST API + MCP tools (FastAPI)
- Event Processors: Async workers (Reminders, Recurring Tasks)
- Clear separation of concerns
- Independent scaling

### AD-002: Event-Driven Communication
**Decision:** Use Kafka for inter-service communication
**Rationale:**
- Decouples services (loose coupling)
- Enables async processing
- Natural fit for reminders and recurring tasks
- Scalable message delivery
- Event replay capability

### AD-003: Dapr Abstraction Layer
**Decision:** Use Dapr instead of direct Kafka/K8s API calls
**Rationale:**
- Simplifies microservices code
- Cloud-agnostic (swap providers easily)
- Handles retries, circuit breakers automatically
- Reduces boilerplate code
- Better developer experience

### AD-004: Cloud-Agnostic Deployment
**Decision:** Use Helm charts that work on any cloud
**Rationale:**
- Not locked to one cloud provider
- Same charts work on OKE, GKE, AKS
- Easy migration if needed
- Learn transferable skills

### AD-005: Managed Services Over Self-Hosted
**Decision:** Use managed Kubernetes, managed Kafka when possible
**Rationale:**
- Less operational overhead
- Better reliability
- Focus on application, not infrastructure
- Faster to production

### AD-006: GitOps for Deployments
**Decision:** Use GitHub Actions for CI/CD
**Rationale:**
- Automated deployments on git push
- Repeatable and auditable
- Infrastructure as code
- Easy rollbacks

## Service Breakdown

### Frontend Service
- **Technology:** Next.js (unchanged from Phase 4)
- **Responsibilities:**
  - User interface
  - Authentication UI
  - Task management UI
  - Chat interface
- **Scaling:** 2-5 replicas based on traffic
- **Communication:** REST API to backend

### Backend API Service
- **Technology:** FastAPI + MCP (unchanged from Phase 4)
- **Responsibilities:**
  - REST API endpoints
  - User authentication
  - Task CRUD operations
  - AI agent with MCP tools
  - Publish events to Kafka
- **Scaling:** 2-10 replicas based on traffic
- **Communication:**
  - Receives: HTTP from frontend
  - Publishes: Events to Kafka
  - Queries: Neon database

### Event Processor Services

#### Reminder Service
- **Technology:** Python FastAPI (new service)
- **Responsibilities:**
  - Subscribe to task-created events
  - Schedule reminders using Dapr Bindings (Cron)
  - Send notifications when due
  - Publish reminder-sent events
- **Scaling:** 1-3 replicas
- **Communication:**
  - Consumes: Kafka events
  - Publishes: Reminder events

#### Recurring Task Service
- **Technology:** Python FastAPI (new service)
- **Responsibilities:**
  - Subscribe to task-completed events
  - Check if task is recurring
  - Create next occurrence automatically
  - Publish task-created events
- **Scaling:** 1-2 replicas
- **Communication:**
  - Consumes: Kafka events
  - Publishes: Task-created events

## Event Schema

### Event: task.created
```json
{
  "event_type": "task.created",
  "task_id": "uuid",
  "user_id": "string",
  "title": "string",
  "description": "string",
  "due_date": "ISO8601 datetime or null",
  "is_recurring": "boolean",
  "recurrence_pattern": "string or null",
  "timestamp": "ISO8601 datetime"
}
```

### Event: task.completed
```json
{
  "event_type": "task.completed",
  "task_id": "uuid",
  "user_id": "string",
  "completed_at": "ISO8601 datetime",
  "timestamp": "ISO8601 datetime"
}
```

### Event: reminder.due
```json
{
  "event_type": "reminder.due",
  "task_id": "uuid",
  "user_id": "string",
  "title": "string",
  "due_date": "ISO8601 datetime",
  "timestamp": "ISO8601 datetime"
}
```

### Event: task.deleted
```json
{
  "event_type": "task.deleted",
  "task_id": "uuid",
  "user_id": "string",
  "timestamp": "ISO8601 datetime"
}
```

## Kafka Topics

| Topic | Purpose | Producers | Consumers | Retention |
|-------|---------|-----------|-----------|-----------|
| task-events | All task operations | Backend API | Reminder Service, Recurring Task Service | 7 days |
| reminder-events | Reminder notifications | Reminder Service | Notification Service (future) | 7 days |
| task-updates | Real-time sync | Backend API | Frontend (WebSocket service, future) | 1 day |

## Dapr Components

### Pub/Sub Component (Kafka)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-broker:9092"
  - name: consumerGroup
    value: "todo-service"
```

### State Store Component (PostgreSQL)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "postgresql://..."
```

### Cron Binding (Reminder Scheduler)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: "@every 1m"
```

### Secret Store (Kubernetes Secrets)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
```

## Quality Standards

### Performance
- API response time: < 200ms (p95)
- Event processing latency: < 5 seconds
- Page load time: < 2 seconds
- Auto-scale trigger: CPU > 70%

### Reliability
- Service uptime: 99.5% (allow for learning/testing)
- Pod restart limit: Max 3 restarts per hour
- Failed event retry: 3 attempts with exponential backoff
- Circuit breaker: Open after 5 consecutive failures

### Scalability
- Horizontal Pod Autoscaler (HPA) for all services
- Min replicas: 1 (cost optimization)
- Max replicas: 10 (safety limit)
- Scale based on CPU and custom metrics

### Security
- All secrets in Kubernetes Secrets or Cloud Secret Manager
- Network policies restrict pod-to-pod communication
- TLS termination at load balancer
- Pod Security Standards: Restricted

### Observability
- Structured logging (JSON format)
- Log aggregation (CloudWatch/Stackdriver/Azure Monitor)
- Basic metrics (CPU, memory, request rate)
- Health check endpoints for all services

## Development Workflow

### Spec-Driven Process (Continued)
1. Write specification (WHAT to build)
2. Create architectural plan (HOW to build)
3. Break into atomic tasks (detailed steps)
4. Implement using Claude Code (NO manual coding)
5. Test locally on Minikube
6. Deploy to cloud
7. Validate and monitor

### Git Workflow
- Work on `phase-5-cloud` branch
- Commit after each major milestone
- Tag deployments: `v5.0-dev`, `v5.0-prod`
- Merge to main after Phase 5 completion

### Testing Strategy
- **Local Testing:** Minikube with Dapr + local Kafka
- **Staging:** Cloud Kubernetes with Redpanda Cloud
- **Validation:** Manual testing + smoke tests
- **Monitoring:** Watch logs and metrics for 24 hours

## Success Criteria

### Technical Validation
- ✅ All services deployed to cloud Kubernetes
- ✅ Kafka topics created and accessible
- ✅ Dapr sidecars running alongside all pods
- ✅ Event flow working (task creation → reminder)
- ✅ Recurring tasks auto-created
- ✅ Frontend accessible via public URL
- ✅ All Phase 4 features still working
- ✅ No errors in logs for 1 hour
- ✅ Auto-scaling triggers correctly

### Feature Validation
- ✅ Create task with due date → Reminder fires
- ✅ Mark recurring task complete → Next occurrence created
- ✅ Task priorities and tags working
- ✅ Search and filter functional
- ✅ All intermediate features implemented

### Operational Validation
- ✅ CI/CD pipeline deploys successfully
- ✅ Rollback works if deployment fails
- ✅ Logs accessible via cloud console
- ✅ Metrics visible in dashboard
- ✅ Cost under $5/month (or free tier)

### Documentation Validation
- ✅ Cloud setup instructions clear
- ✅ Kafka configuration documented
- ✅ Dapr setup explained
- ✅ Event flow diagrams included
- ✅ Troubleshooting guide comprehensive

## Non-Functional Requirements

### Performance
- API latency: < 200ms (95th percentile)
- Event processing: < 10 seconds end-to-end
- Frontend load: < 3 seconds (First Contentful Paint)

### Reliability
- Service availability: 99%+ (allow for maintenance)
- Data durability: 99.999% (using Neon + Kafka retention)
- Graceful degradation: App works without Kafka (in degraded mode)

### Scalability
- Support 100 concurrent users
- Process 1000 events/minute
- Scale from 3 pods to 30 pods in 5 minutes

### Security
- All traffic encrypted (TLS)
- Secrets rotated quarterly (best practice)
- No sensitive data in logs
- Pod-to-pod communication restricted

### Cost
- Total cloud cost: < $5/month (Oracle free tier)
- Or: Stay within free credits (GKE/AKS)
- Monitor daily spend
- Alerts if cost exceeds $10/month

## Constraints and Limitations

### Time Constraints
- Phase 5 due: January 18, 2026
- Estimated effort: 16-24 hours
- Must balance features with deadline

### Cloud Constraints
- Limited to one cloud provider (avoid complexity)
- Free tier limitations (CPU, memory, storage)
- Region restrictions (use closest region)
- Network egress costs (minimize external calls)

### Technical Constraints
- Neon database stays external (not in K8s)
- No custom Kubernetes operators
- No service mesh (too complex for Phase 5)
- Stick to managed services where possible

### Scope Constraints
- Focus on core event-driven features
- Skip advanced Dapr features (workflows, actors)
- No multi-region deployment
- No advanced monitoring (Prometheus, Grafana optional)

## Risk Mitigation

### Risk: Cloud costs spiral out of control
**Mitigation:**
- Set up billing alerts at $5, $10, $20
- Use free tiers exclusively
- Auto-scale down during idle
- Delete resources after hackathon

### Risk: Kafka connectivity issues
**Mitigation:**
- Test Kafka connection before full deployment
- Implement fallback mode (direct DB writes)
- Use Dapr retry policies
- Monitor Kafka consumer lag

### Risk: Complex debugging in cloud
**Mitigation:**
- Ensure logs are aggregated
- Add verbose logging for event flow
- Test everything locally first
- Document common issues

### Risk: CI/CD pipeline breaks
**Mitigation:**
- Test pipeline on branch first
- Manual deployment as backup
- Keep Phase 4 Helm charts as fallback
- Git tags for easy rollback

### Risk: Running out of time
**Mitigation:**
- Prioritize P0 features only
- Skip advanced features if needed
- Use working Phase 4 as baseline
- Submit partial if necessary

## References
- Phase 4 application (baseline)
- Hackathon Phase 5 requirements
- Dapr documentation (dapr.io)
- Kafka documentation (kafka.apache.org)
- Cloud provider documentation (Oracle/Google/Azure)
- Helm charts from Phase 4 (extend these)

## Acceptance Criteria Summary

Phase 5 is complete when:

1. ✅ Application deployed to cloud Kubernetes (OKE/GKE/AKS)
2. ✅ Kafka topics created and events flowing
3. ✅ Dapr sidecars running with all components
4. ✅ Reminder service creates notifications
5. ✅ Recurring tasks auto-created
6. ✅ Advanced features implemented (priorities, tags, search, filters)
7. ✅ CI/CD pipeline working
8. ✅ Application accessible via public URL
9. ✅ All logs aggregated and accessible
10. ✅ Demo video recorded and submitted
11. ✅ Documentation complete
12. ✅ Cost under budget (free tier or < $5/month)
```

## Response

Updated the project constitution to version 5.0.0 to incorporate Phase 5 requirements for cloud deployment with Kafka and Dapr. The new constitution includes:

- Event-Driven Architecture principle
- Microservices Principles with event-driven concepts
- Cost Optimization principle
- Updated technology stack with Kafka, Dapr, and cloud infrastructure
- Event schemas and topic definitions
- Dapr component configurations
- Quality standards for distributed systems
- Updated success criteria for Phase 5

The constitution maintains backward compatibility while adding new principles and requirements specific to the event-driven architecture, cloud deployment, and distributed system patterns using Kafka and Dapr.

## Outcome

Successfully updated the constitution to reflect Phase 5 requirements with event-driven architecture, Kafka integration, Dapr runtime, and cloud deployment patterns. The updated document provides clear guidance for implementing the distributed system architecture while maintaining all previous principles and requirements.