# Kubernetes Deployment Architecture

```mermaid
graph TB
    subgraph "Minikube Cluster"
        direction TB
        FE[Frontend Pod<br/>Next.js App<br/>Port 3000]
        BE[Backend Pod<br/>FastAPI App<br/>Port 8000]
        SVC_FE[Frontend Service<br/>ClusterIP: 3000]
        SVC_BE[Backend Service<br/>ClusterIP: 8000]
        CM_FE[Frontend ConfigMap]
        CM_BE[Backend ConfigMap]
        SEC_BE[Backend Secret]
        
        FE -.-> CM_FE
        BE -.-> CM_BE
        BE -.-> SEC_BE
    end
    
    DB[(Neon PostgreSQL<br/>External)]
    
    User -->|HTTP| SVC_FE
    SVC_FE --> FE
    FE -->|API Calls| SVC_BE
    SVC_BE --> BE
    BE -->|Database Connection| DB
    
    style FE fill:#e1f5fe
    style BE fill:#f3e5f5
    style DB fill:#e8f5e8
```

## Component Descriptions

### Frontend Service
- **Pod**: Runs Next.js application in a container
- **Image**: todo-frontend:latest
- **Port**: 3000
- **Purpose**: Serves the user interface and handles user interactions

### Backend Service
- **Pod**: Runs FastAPI application in a container
- **Image**: todo-backend:latest
- **Port**: 8000
- **Purpose**: Provides REST API endpoints and connects to the database

### External Database
- **Provider**: Neon PostgreSQL (external to cluster)
- **Connection**: Via SSL using database URL from Kubernetes Secret
- **Purpose**: Stores application data (users, tasks, conversations)

### Configuration
- **ConfigMaps**: Store non-sensitive configuration values
- **Secrets**: Store sensitive data like database credentials and JWT secrets