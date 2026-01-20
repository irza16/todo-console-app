# ADR-0001: MCP Architecture with OpenAI Integration

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-20
- **Feature:** AI-Powered Todo Chatbot
- **Context:** Need to implement a conversational AI assistant that allows users to manage their todo tasks through natural language interactions. The system must integrate with existing architecture while supporting advanced AI capabilities and maintaining security and scalability.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Implement an MCP (Model Context Protocol) architecture with OpenAI integration to enable conversational AI task management:

- **MCP Server**: Official MCP SDK exposing 5 stateless task management tools (add_task, list_tasks, complete_task, update_task, delete_task)
- **AI Framework**: OpenAI Agents SDK for natural language processing and tool orchestration
- **Frontend Interface**: OpenAI ChatKit for natural language interaction
- **Data Architecture**: Conversation and Message entities in Neon PostgreSQL with proper user isolation
- **Integration Pattern**: MCP tools as function tools for OpenAI Agents, stateless operations with database persistence

## Consequences

### Positive

- Enables natural language interface for todo management, improving user experience
- MCP architecture provides standardized protocol for exposing tools to AI agents
- Statelessness ensures scalability and resilience with no in-memory conversation state
- Maintains backward compatibility with existing REST API
- Clear separation of concerns between AI logic and business operations
- Leverages existing OpenAI ecosystem for reliable natural language processing

### Negative

- Adds complexity with additional service layers (MCP server, agent layer)
- Potential vendor lock-in to OpenAI ecosystem and MCP protocol
- Increased dependency management complexity
- Additional costs for OpenAI API usage
- Learning curve for MCP protocol implementation
- Requires careful security considerations for AI tool access control

## Alternatives Considered

Alternative A: Direct API integration without MCP
- Approach: Connect OpenAI directly to existing REST endpoints
- Why rejected: Would bypass standardized MCP protocol, limiting extensibility and creating tight coupling between AI and backend implementation

Alternative B: Custom AI agent implementation
- Approach: Build custom natural language processor instead of using OpenAI Agents SDK
- Why rejected: Would require significant development time, lack enterprise-grade reliability, and miss out on OpenAI's advanced capabilities

Alternative C: WebSocket-based real-time communication
- Approach: Implement real-time bidirectional communication instead of stateless HTTP
- Why rejected: Would complicate state management, add infrastructure complexity, and make scaling more difficult

Alternative D: Serverless function architecture
- Approach: Use serverless functions for AI processing instead of dedicated MCP server
- Why rejected: Would have higher latency for AI operations and less efficient for persistent tool availability

## References

- Feature Spec: specs/1-ai-todo-chatbot/spec.md
- Implementation Plan: specs/1-ai-todo-chatbot/plan.md
- Related ADRs: none
- Evaluator Evidence: history/prompts/ai-todo-chatbot/3-complete-ai-todo-chatbot-implementation-plan.plan.prompt.md
