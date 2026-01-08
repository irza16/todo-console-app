# API Client Generator Skill

## Purpose
Create a type-safe API client for connecting Next.js frontend to FastAPI backend with automatic JWT token injection and error handling.

## When to Use
- Connecting frontend to backend API
- Need type-safe API calls
- Managing authentication tokens
- Handling API errors consistently

## Prerequisites
- Next.js project set up
- Backend API running
- Types defined in `types/index.ts`

## Instructions

### Step 1: Install Dependencies
See [client.md](client.md)

### Step 2: Create API Client Base
See [client.md](client.md)

### Step 3: Create API Methods
See [client.md](client.md)

### Step 4: Create React Query Hooks
See [hooks.md](hooks.md)

### Step 5: Setup React Query Provider
See [client.md](client.md)

## Client
See [client.md](client.md)

## Hooks
See [hooks.md](hooks.md)

## Error Handling
See [error-handling.md](error-handling.md)

## Validation Checklist
- [ ] Axios installed and configured
- [ ] React Query installed and provider setup
- [ ] API base URL configured in env
- [ ] Request interceptor adds auth token
- [ ] Response interceptor handles 401 errors
- [ ] API methods created for all endpoints
- [ ] React Query hooks created
- [ ] Toast notifications working
- [ ] Error handling implemented
- [ ] Types imported correctly

## Output Files
- `lib/api.ts` - Axios client
- `lib/api/tasks.ts` - Task API methods
- `lib/api/auth.ts` - Auth API methods
- `hooks/use-tasks.ts` - Task hooks
- `hooks/use-auth.ts` - Auth hooks
- `app/providers.tsx` - React Query provider

## Next Steps
After creating API client:
1. Build UI components that use these hooks
2. Add loading and error states
3. Implement optimistic updates
4. Add request caching strategies
