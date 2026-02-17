# Research Findings: Cloud Deployment with Kafka & Dapr

## Decision: Azure AKS Configuration
**Rationale**: Using 1x Standard_B1s node for cost optimization during hackathon demo
**Alternatives considered**:
- 2x Standard_B2s nodes (higher cost, ~$1.32/day)
- 1x Standard_B2s node (moderate cost, ~$0.66/day)
- 2x Standard_B1s nodes (moderate cost, ~$0.66/day)

## Decision: Kafka Deployment Strategy
**Rationale**: Using Bitnami Kafka Helm chart for self-hosted Kafka on AKS instead of Azure Event Hubs to stay within free tier costs
**Alternatives considered**:
- Azure Event Hubs (managed, but costs ~$11/month)
- Confluent Cloud (managed, but costs extra)
- Self-hosted Kafka (chosen, free with Azure credits)

## Decision: Dapr Integration
**Rationale**: Using Dapr for simplified pub/sub messaging between services, state management, and secret management
**Alternatives considered**:
- Raw Kafka clients (more complex, requires more code)
- RabbitMQ (different ecosystem)
- Azure Service Bus (costs extra)

## Decision: Resource Allocation for B1s Nodes
**Rationale**: Optimized resource requests/limits to fit within 1 vCPU, 1GB RAM constraints:
- Frontend: 128Mi/100m (requests), 256Mi/250m (limits)
- Backend: 256Mi/200m (requests), 512Mi/500m (limits)
- Reminder Service: 64Mi/50m (requests), 128Mi/100m (limits)
- Recurring Task Service: 64Mi/50m (requests), 128Mi/100m (limits)
**Total**: 512Mi memory, 400m CPU requests - fits within B1s capacity

## Decision: Cost Optimization Strategy
**Rationale**: Implement demo-first approach with stop/delete strategy to minimize costs
**Alternatives considered**:
- Production-ready configuration (higher ongoing costs)
- Spot/preemptible instances (potential downtime during demo)
- Pay-as-you-go (higher cost per day)

## Decision: Event Schema Design
**Rationale**: Standardized event structure with consistent fields for all event types (task.created, task.completed, reminder.due, etc.)
**Alternatives considered**:
- Different schemas per event type (less consistency)
- Generic event structure (less type safety)

## Decision: Service Communication Pattern
**Rationale**: Async pub/sub via Kafka topics with Dapr simplifies decoupling and resilience
**Alternatives considered**:
- Direct HTTP calls (tight coupling, failure propagation)
- Message queues (different technology stack)
- gRPC (more complex for event-driven patterns)