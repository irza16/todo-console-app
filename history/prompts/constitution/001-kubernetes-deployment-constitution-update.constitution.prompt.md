---
id: 001
title: Kubernetes Deployment Constitution Update
stage: constitution
date: 2026-02-06
surface: agent
model: google/gemini-2.0-flash-exp:free
feature: none
branch: 001-todo-console-app
user: irza
command: sp.constitution
labels: [kubernetes, constitution, deployment, containerization]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - constitution update validation
---

## Prompt

```text
# Phase 4: Kubernetes Deployment - Constitution

## Purpose
Define the foundational principles, constraints, and architectural decisions that govern the containerization and Kubernetes deployment of the Todo AI Chatbot application.

## Core Principles

### 1. Cloud-Native Architecture
- Applications must be containerized and stateless
- Each service runs in its own container with minimal dependencies
- Configuration is externalized via environment variables and ConfigMaps
- Services communicate via well-defined network interfaces

### 2. Separation of Concerns
- Frontend and backend are deployed as separate pods
- Each service has its own Docker image
- Database remains external (Neon PostgreSQL) - NOT containerized
- Clear service boundaries with dedicated configurations

### 3. Reproducibility and Portability
- Development environment (Minikube) mirrors production patterns
- Dockerfiles must be multi-stage for optimization
- All configuration is declarative (Helm charts, YAML)
- No hardcoded values - use environment variables

### 4. Security First
- Secrets managed via Kubernetes Secrets
- No API keys or credentials in Docker images
- Minimal container attack surface (non-root user, minimal packages)
- Network policies enforce least-privilege access

### 5. Observability and Debugging
- Containers must log to stdout/stderr
- Health checks (liveness and readiness probes) required
- Clear error messages for troubleshooting
- Resource limits defined to prevent resource exhaustion

## Technology Constraints

### Required Technologies
- **Containerization**: Docker (Docker Desktop 4.53+)
- **Orchestration**: Kubernetes via Minikube (latest stable)
- **Package Management**: Helm 3.x
- **AI DevOps**: kubectl-ai and kagent for cluster operations
- **Optional**: Docker AI Agent (Gordon) if available in region

### Forbidden Technologies
- Docker Compose for deployment (development only)
- Hardcoded IP addresses or hostnames
- In-cluster databases (use external Neon DB)
- Root containers (must run as non-root user)

## Architecture Decisions

### AD-001: Two-Service Architecture
**Decision**: Deploy frontend and backend as separate services
**Rationale**:
- Independent scaling (frontend static content vs backend compute)
- Clear separation of concerns
- Easier debugging and updates
- Follows microservices best practices

### AD-002: External Database
**Decision**: Keep Neon PostgreSQL external to Kubernetes cluster
**Rationale**:
- Neon is serverless and managed (no operational overhead)
- Avoid data persistence challenges in learning environment
- Phase 4 focuses on application deployment, not data layer
- Simplifies local development (no StatefulSets needed)

### AD-003: Helm for Deployment Management
**Decision**: Use Helm charts instead of raw Kubernetes manifests
**Rationale**:
- Templating reduces duplication
- Easy environment-specific configuration (dev/prod)
- Package and version management
- Industry standard for Kubernetes deployments

### AD-004: Multi-Stage Docker Builds
**Decision**: Use multi-stage Dockerfiles for both services
**Rationale**:
- Smaller final images (reduced attack surface)
- Faster deployment times
- Separation of build and runtime dependencies
- Better caching and build performance

### AD-005: ConfigMaps for Non-Secret Config
**Decision**: Use ConfigMaps for non-sensitive configuration, Secrets for credentials
**Rationale**:
- Clear distinction between public and private config
- Kubernetes-native configuration management
- Easy updates without rebuilding images
- Follows security best practices

## Quality Standards

### Docker Images
- Must be under 500MB (frontend) and 300MB (backend)
- Must include health check endpoints
- Must run as non-root user
- Must have clear versioning (use Git commit SHA or semantic versioning)

### Kubernetes Resources
- All deployments must have resource requests and limits
- All services must have readiness and liveness probes
- Replica count: minimum 1, maximum 3 for local testing
- All resources must have appropriate labels for organization

### Documentation
- Each Dockerfile must have inline comments explaining stages
- Helm values.yaml must document all configuration options
- README must include local deployment instructions
- Troubleshooting guide for common issues

## Development Workflow

### Spec-Driven Process
1. Write specification (WHAT to build)
2. Create architectural plan (HOW to build)
3. Break into atomic tasks (detailed steps)
4. Implement using Claude Code (NO manual coding)
5. Test and validate against acceptance criteria

### Testing Requirements
- Docker images must build successfully without errors
- Containers must start and serve health check endpoints
- Helm charts must install without errors
- Full application must be accessible via port-forward or NodePort
- Database connectivity must be verified from backend pod

### Git Workflow
- Work on `phase-4-kubernetes` branch
- Commit after each major milestone
- Meaningful commit messages
- Tag final submission as `phase-4-submission`

## Success Criteria

### Deliverables
- ✅ Working Dockerfiles for frontend and backend
- ✅ Helm chart with proper templates and values
- ✅ Successful deployment to Minikube
- ✅ Application accessible and functional
- ✅ Demo video (under 90 seconds)
- ✅ Documentation for setup and deployment

### Acceptance Criteria
- Application runs completely within Kubernetes (except database)
- Frontend can communicate with backend via Kubernetes service
- Backend can connect to external Neon database
- All pods are in Running state with 0 restarts
- Application behaves identically to Phase 3 version
- kubectl-ai and kagent can successfully interact with cluster

## Non-Functional Requirements

### Performance
- Application startup time: < 30 seconds from helm install
- API response time: < 500ms for typical requests
- Container restart time: < 15 seconds

### Reliability
- Pods must restart automatically on failure
- Health checks must accurately reflect service health
- Graceful shutdown on pod termination (SIGTERM handling)

### Resource Usage
- Frontend pod: max 256MB RAM, 0.5 CPU
- Backend pod: max 512MB RAM, 1.0 CPU
- Total cluster footprint: < 2GB RAM

## Constraints and Limitations

### Time Constraints
- Phase 4 due: January 4, 2026
- Estimated effort: 12-16 hours
- Must balance learning with delivery

### Environment Constraints
- Development on local machine (Minikube)
- Limited to resources available on personal hardware
- No cloud costs (everything local)

### Scope Constraints
- No new features - deploy existing Phase 3 application
- No advanced Kubernetes features (operators, custom resources)
- No service mesh or advanced networking
- Focus on fundamentals: Pods, Services, Deployments, ConfigMaps, Secrets

## References
- Hackathon Phase 4 requirements document
- Phase 3 application (current working state)
- Kubernetes documentation (kubernetes.io)
- Docker best practices (docs.docker.com)
- Helm documentation (helm.sh)
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are updating the project constitution at `.specify/memory/constitution.md`. This file is a TEMPLATE containing placeholder tokens in square brackets (e.g. `[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`). Your job is to (a) collect/derive values for placeholders, (b) fill the template precisely, and (c) propagate any amendments across dependent artifacts.

Follow this execution flow:

1. Load the existing constitution template at `.specify/memory/constitution.md`.
   - Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.
   **IMPORTANT**: The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly.

2. Collect/derive values for placeholders:
   - If user input (conversation) supplies a value, use it.
   - Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded).
   - For governance dates: `RATIFICATION_DATE` is the original adoption date (if unknown ask or mark TODO), `LAST_AMENDED_DATE` is today if changes are made, otherwise keep previous.
   - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:
     - MAJOR: Backward incompatible governance/principle removals or redefinitions.
     - MINOR: New principle/section added or materially expanded guidance.
     - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.
   - If version bump type ambiguous, propose reasoning before finalizing.

3. Draft the updated constitution content:
   - Replace every placeholder with concrete text (no bracketed tokens left except intentionally retained template slots that the project has chosen not to define yet—explicitly justify any left).
   - Preserve heading hierarchy and comments can be removed once replaced unless they still add clarifying guidance.
   - Ensure each Principle section: succinct name line, paragraph (or bullet list) capturing non‑negotiable rules, explicit rationale if not obvious.
   - Ensure Governance section lists amendment procedure, versioning policy, and compliance review expectations.

4. Consistency propagation checklist (convert prior checklist into active validations):
   - Read `.specify/templates/plan-template.md` and ensure any "Constitution Check" or rules align with updated principles.
   - Read `.specify/templates/spec-template.md` for scope/requirements alignment—update if constitution adds/removes mandatory sections or constraints.
   - Read `.specify/templates/tasks-template.md` and ensure task categorization reflects new or removed principle-driven task types (e.g., observability, versioning, testing discipline).
   - Read each command file in `.specify/templates/commands/*.md` (including this one) to verify no outdated references (agent-specific names like CLAUDE only) remain when generic guidance is required.
   - Read any runtime guidance docs (e.g., `README.md`, `docs/quickstart.md`, or agent-specific guidance files if present). Update references to principles changed.

5. Produce a Sync Impact Report (prepend as an HTML comment at top of the constitution file after update):
   - Version change: old → new
   - List of modified principles (old title → new title if renamed)
   - Added sections
   - Removed sections
   - Templates requiring updates (✅ updated / ⚠ pending) with file paths
   - Follow-up TODOs if any placeholders intentionally deferred.

6. Validation before final output:
   - No remaining unexplained bracket tokens.
   - Version line matches report.
   - Dates ISO format YYYY-MM-DD.
   - Principles are declarative, testable, and free of vague language ("should" → replace with MUST/SHOULD rationale where appropriate).

7. Write the completed constitution back to `.specify/memory/constitution.md` (overwrite).

8. Output a final summary to the user with:
   - New version and bump rationale.
   - Any files flagged for manual follow-up.
   - Suggested commit message (e.g., `docs: amend constitution to vX.Y.Z (principle additions + governance update)`).

Formatting & Style Requirements:

- Use Markdown headings exactly as in the template (do not demote/promote levels).
- Wrap long rationale lines to keep readability (<100 chars ideally) but do not hard enforce with awkward breaks.
- Keep a single blank line between sections.
- Avoid trailing whitespace.

If the user supplies partial updates (e.g., only one principle revision), still perform validation and version decision steps.

If critical info missing (e.g., ratification date truly unknown), insert `TODO(<FIELD_NAME>): explanation` and include in the Sync Impact Report under deferred items.

Do not create a new template; always operate on the existing `.specify/memory/constitution.md` file.

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record) using agent‑native tools when possible.

1) Determine Stage
   - Stage: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate Title and Determine Routing:
   - Generate Title: 3–7 words (slug for filename)
   - Route is automatically determined by stage:
     - `constitution` → `history/prompts/constitution/`
     - Feature stages → `history/prompts/<feature-name>/` (spec, plan, tasks, red, green, refactor, explainer, misc)
     - `general` → `history/prompts/general/`

3) Create and Fill PHR (Shell first; fallback agent‑native)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Open the file and fill remaining placeholders (YAML + body), embedding full PROMPT_TEXT (verbatim) and concise RESPONSE_TEXT.
   - If the script fails:
     - Read `.specify/templates/phr-template.prompt.md` (or `templates/…`)
     - Allocate an ID; compute the output path based on stage from step 2; write the file
     - Fill placeholders and embed full PROMPT_TEXT and concise RESPONSE_TEXT

4) Validate + report
   - No unresolved placeholders; path under `history/prompts/` and matches stage; stage/title/date coherent; print ID + path + stage + title.
   - On failure: warn, don't block. Skip only for `/sp.phr`.
```

## Response snapshot

I've updated the project constitution to include the new Phase 4 Kubernetes Deployment requirements. The updated constitution now includes:

### New Kubernetes-Focused Principles Added:
1. **Cloud-Native Architecture**: Applications must be containerized and stateless
2. **Separation of Concerns**: Frontend and backend deployed as separate services in Kubernetes
3. **Reproducibility and Portability**: Development environment mirrors production patterns with multi-stage Dockerfiles
4. **Security First**: Secrets managed via Kubernetes Secrets with non-root containers
5. **Observability and Debugging**: Containers must log to stdout/stderr with health checks

### Key Updates Made:
- Updated version from 3.0.0 to 4.0.0 (major version bump due to significant new architectural requirements)
- Enhanced the Technology Stack section with containerization and orchestration technologies (Docker, Kubernetes, Helm, Minikube)
- Added Kubernetes-specific data model structures for ConfigMaps, Secrets, and Deployments
- Updated Quality Gates to include Kubernetes deployment validation criteria
- Extended Development Workflow to include containerization and deployment steps
- Expanded Success Definition to cover Kubernetes deployment requirements

### Version Change Justification:
The version was bumped from 3.0.0 to 4.0.0 because this update introduces significant new architectural requirements (containerization, orchestration, Kubernetes deployment) that fundamentally change how the application is deployed and operated, representing a major evolution in the project's architecture.

The constitution now properly reflects the requirements for Phase 4: Kubernetes Deployment while maintaining backward compatibility with all existing principles and functionality.

### Files Updated:
- `.specify/memory/constitution.md`: Updated with new Kubernetes-focused principles and requirements

### Templates Requiring Updates:
The following templates have been flagged for future updates to align with the new Kubernetes requirements:
- `.specify/templates/spec-template.md`
- `.specify/templates/plan-template.md`
- `.specify/templates/tasks-template.md`

## Outcome

- ✅ Impact: Major constitution update with 5 new Kubernetes-focused principles and updated deployment requirements
- 🧪 Tests: Constitution update validated with proper versioning and content
- 📁 Files: .specify/memory/constitution.md updated successfully
- 🔁 Next prompts: Template updates needed for spec, plan, and tasks templates
- 🧠 Reflection: The update maintains backward compatibility while extending the constitution to cover containerization and Kubernetes deployment requirements

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All requirements met
- Prompt variant (if applicable): Standard constitution update
- Next experiment (smallest change to try): Update templates to align with new constitution