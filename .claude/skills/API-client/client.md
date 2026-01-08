# API Client

## Prerequisites
- Next.js project set up
- Backend API running
- Types defined in `types/index.ts`

## Install Dependencies
```bash
npm install axios
npm install @tanstack/react-query
```

## Create API Client Base
`lib/api.ts`:
```typescript
import axios, { AxiosError, AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config) => {
    // Get token from localStorage or cookie
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

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

export default apiClient;
```

## Create API Methods
`lib/api/tasks.ts`:
```typescript
import apiClient from '../api';
import { Task, TaskCreate, TaskUpdate } from '@/types';

export const taskApi = {
  // Get all tasks
  getAll: async (userId: string): Promise<Task[]> => {
    const response = await apiClient.get(`/api/${userId}/tasks`);
    return response.data;
  },

  // Get single task
  getById: async (userId: string, taskId: number): Promise<Task> => {
    const response = await apiClient.get(`/api/${userId}/tasks/${taskId}`);
    return response.data;
  },

  // Create task
  create: async (userId: string, data: TaskCreate): Promise<Task> => {
    const response = await apiClient.post(`/api/${userId}/tasks`, data);
    return response.data;
  },

  // Update task
  update: async (
    userId: string,
    taskId: number,
    data: TaskUpdate
  ): Promise<Task> => {
    const response = await apiClient.put(
      `/api/${userId}/tasks/${taskId}`,
      data
    );
    return response.data;
  },

  // Delete task
  delete: async (userId: string, taskId: number): Promise<void> => {
    await apiClient.delete(`/api/${userId}/tasks/${taskId}`);
  },

  // Toggle complete
  toggleComplete: async (
    userId: string,
    taskId: number
  ): Promise<Task> => {
    const response = await apiClient.patch(
      `/api/${userId}/tasks/${taskId}/complete`
    );
    return response.data;
  },
};
```

`lib/api/auth.ts`:
```typescript
import apiClient from '../api';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  name: string;
}

export interface AuthResponse {
  user: {
    id: string;
    email: string;
    name: string;
  };
  token: string;
}

export const authApi = {
  // Login
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post('/api/auth/login', data);
    // Store token
    if (response.data.token) {
      localStorage.setItem('auth_token', response.data.token);
    }
    return response.data;
  },

  // Signup
  signup: async (data: SignupRequest): Promise<AuthResponse> => {
    const response = await apiClient.post('/api/auth/signup', data);
    // Store token
    if (response.data.token) {
      localStorage.setItem('auth_token', response.data.token);
    }
    return response.data;
  },

  // Logout
  logout: async (): Promise<void> => {
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
  },

  // Get current user
  me: async () => {
    const response = await apiClient.get('/api/auth/me');
    return response.data;
  },
};
```

## Setup React Query Provider
`app/providers.tsx`:
```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

Update `app/layout.tsx`:
```typescript
import { Providers } from './providers';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
```
