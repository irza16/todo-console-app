# API Error Handling

## Error Handler
`lib/api/errors.ts`:
```typescript
import { AxiosError } from 'axios';

export function handleApiError(error: unknown) {
  if (error instanceof AxiosError) {
    return {
      message: error.response?.data?.message || 'An error occurred',
      status: error.response?.status,
    };
  }
  return {
    message: 'An unexpected error occurred',
    status: 500,
  };
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    return error.response?.data?.detail || error.response?.data?.message || 'An error occurred';
  }
  return error instanceof Error ? error.message : 'An unexpected error occurred';
}

export function isNetworkError(error: unknown): boolean {
  if (error instanceof AxiosError) {
    return !error.response && error.request;
  }
  return false;
}

export function isAuthError(error: unknown): boolean {
  if (error instanceof AxiosError) {
    return error.response?.status === 401;
  }
  return false;
}
```

## Error Boundaries
`components/error-boundary.tsx`:
```typescript
'use client';

import { Component, ReactNode } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center min-h-screen p-4">
          <Card className="max-w-md w-full">
            <CardHeader>
              <CardTitle>Something went wrong</CardTitle>
              <CardDescription>
                {this.state.error?.message || 'An unexpected error occurred'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                onClick={() => window.location.reload()}
                className="w-full"
              >
                Reload Page
              </Button>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}
```

## Response Interceptor for Errors
Already configured in `lib/api.ts` (see [client.md](client.md)):

```typescript
// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## Testing API Client
```typescript
// Test in browser console
import { taskApi } from '@/lib/api/tasks';

// Test connection
taskApi.getAll('user123')
  .then(tasks => console.log('Tasks:', tasks))
  .catch(error => console.error('Error:', error));
```

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

## Error Handling Best Practices
- Always handle network errors gracefully
- Show user-friendly error messages
- Log errors for debugging
- Implement retry logic for transient failures
- Use error boundaries to catch React errors
- Provide recovery options (retry, reload)
- Don't expose sensitive error details
