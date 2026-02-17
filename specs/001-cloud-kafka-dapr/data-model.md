# Data Model: Cloud Deployment with Kafka & Dapr

## Task Entity
- **id**: uuid.UUID (primary key, auto-generated)
- **title**: str (required, max 200 chars)
- **description**: Optional[str] (optional, max 1000 chars)
- **completed**: bool (default: False)
- **due_date**: Optional[datetime] (optional)
- **priority**: TaskPriority enum (Low, Medium, High, Urgent; default: Medium)
- **tags**: List[str] (array of strings, default: empty array)
- **is_recurring**: bool (default: False)
- **recurrence_pattern**: Optional[str] (daily, weekly, monthly, weekdays)
- **user_id**: uuid.UUID (foreign key to users table)
- **created_at**: datetime (auto-generated)
- **updated_at**: datetime (auto-generated)

### Validation Rules
- title must be 1-200 characters
- priority must be one of the defined enum values
- tags must be strings with reasonable length limits
- due_date must be in the future if provided
- user_id must reference an existing user

### Indexes
- idx_tasks_user_id (user_id) - for user isolation
- idx_tasks_completed (completed) - for filtering
- idx_tasks_due_date (due_date) - for reminder scheduling
- idx_tasks_priority (priority) - for priority filtering
- idx_tasks_tags (GIN index on tags) - for tag-based filtering

## User Entity (existing)
- **id**: uuid.UUID (primary key, auto-generated)
- **email**: str (unique, validated)
- **password_hash**: str (encrypted password)
- **created_at**: datetime (auto-generated)
- **updated_at**: datetime (auto-generated)

## Event Schema
### Task Created Event
```json
{
  "event_type": "task.created",
  "task_id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "description": "string or null",
  "due_date": "ISO8601 datetime or null",
  "is_recurring": "boolean",
  "recurrence_pattern": "string or null",
  "priority": "string",
  "tags": "array of strings",
  "timestamp": "ISO8601 datetime"
}
```

### Task Completed Event
```json
{
  "event_type": "task.completed",
  "task_id": "uuid",
  "user_id": "uuid",
  "completed_at": "ISO8601 datetime",
  "timestamp": "ISO8601 datetime"
}
```

### Reminder Due Event
```json
{
  "event_type": "reminder.due",
  "task_id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "due_date": "ISO8601 datetime",
  "timestamp": "ISO8601 datetime"
}
```

### Task Deleted Event
```json
{
  "event_type": "task.deleted",
  "task_id": "uuid",
  "user_id": "uuid",
  "timestamp": "ISO8601 datetime"
}
```

## Kafka Topics
- **task-events**: For task lifecycle events (created, completed, deleted)
- **reminder-events**: For scheduled reminder notifications
- **task-updates**: For task updates and modifications

### Topic Configuration
- Partitions: 3 per topic
- Replication factor: 1 (for demo/B1s constraints)
- Retention: 7 days
- Cleanup policy: delete

## Dapr Components
### Kafka Pub/Sub Component
- Name: kafka-pubsub
- Type: pubsub.kafka
- Brokers: kafka.kafka.svc.cluster.local:9092
- Consumer Group: todo-app-group
- Auth Type: none (for demo)

### State Store Component
- Name: statestore
- Type: state.postgresql
- Connection String: from Kubernetes secret

### Secret Store Component
- Name: kubernetes-secrets
- Type: secretstores.kubernetes