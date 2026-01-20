# Research Findings: AI-Powered Todo Chatbot with MCP Architecture

## MCP SDK Installation and Configuration

### Decision: Use official MCP SDK with Python implementation
**Rationale**: The official MCP SDK provides standardized protocols for exposing tools to AI agents, ensuring compatibility with various AI platforms. The Python implementation integrates well with FastAPI and SQLModel.

**Alternatives considered**:
- Custom tool exposure protocols
- Direct API calls without MCP
- Third-party tool libraries

**Findings**:
- MCP SDK installation: `pip install mcp`
- Requires Python 3.8+ (compatible with our setup)
- Provides decorators for easy tool registration
- Supports JSON schema for parameter validation

## OpenAI Agents SDK Integration with MCP

### Decision: Use OpenAI Agents SDK with MCP tools as function tools
**Rationale**: OpenAI Agents SDK can consume MCP-exposed tools as function tools, allowing the agent to call MCP functions directly. This creates a clean separation between the AI logic and the database operations.

**Alternatives considered**:
- Direct database access from agent
- Custom API endpoints for agent
- WebSocket-based communication

**Findings**:
- OpenAI Agents SDK installation: `pip install openai`
- MCP tools can be registered as function tools in agent configuration
- Agent receives conversation history as context
- Tool calls are automatically tracked and returned to frontend

## ChatKit Domain Configuration Requirements

### Decision: Configure Vercel domain in OpenAI domain allowlist
**Rationale**: OpenAI ChatKit requires domains to be registered in the OpenAI dashboard for security. Vercel domains need to be added to the allowlist for ChatKit to function properly.

**Alternatives considered**:
- Custom chat interface instead of ChatKit
- Self-hosted chat solution
- Third-party chat widget

**Findings**:
- Need to register Vercel domain in OpenAI dashboard
- Obtain domain key for NEXT_PUBLIC_OPENAI_DOMAIN_KEY
- Domain verification required for production
- Localhost domains for development

## Dependency Compatibility Matrix

### Decision: Compatible dependency versions
**Rationale**: Ensuring all new dependencies work together prevents integration issues and reduces maintenance overhead.

**Findings**:
- MCP SDK: `mcp>=1.0.0` - Official Python implementation
- OpenAI SDK: `openai>=1.0.0` - Latest OpenAI Agents SDK
- FastAPI: `fastapi>=0.115.0` - Compatible with existing setup
- SQLModel: `sqlmodel>=0.0.0` - Compatible with existing setup
- Python: 3.13+ - Already in use

**Compatibility verification**:
- MCP SDK works with Python 3.13
- OpenAI SDK compatible with existing FastAPI setup
- No version conflicts with existing dependencies
- All packages support async/await patterns

## Additional Technical Findings

### Conversation State Management
**Finding**: MCP tools should be stateless, with all state stored in the database. The agent should receive conversation history as part of each request to maintain context.

**Implication**: Each MCP tool function should accept user_id and work independently, while the chat endpoint manages conversation history retrieval and storage.

### Security Considerations
**Finding**: MCP tools must validate user permissions for each operation, as they operate independently from the main authentication layer.

**Implication**: Each MCP tool must verify that the user_id parameter corresponds to the authenticated user making the request.

### Error Handling Patterns
**Finding**: MCP tools should return structured error responses that the agent can interpret and relay to the user in natural language.

**Implication**: Design consistent error response formats across all MCP tools for uniform error handling in the agent.