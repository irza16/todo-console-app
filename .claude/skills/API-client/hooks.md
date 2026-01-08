# React Query Hooks

## Task Hooks
`hooks/use-tasks.ts`:
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { taskApi } from '@/lib/api/tasks';
import { TaskCreate, TaskUpdate } from '@/types';
import { toast } from 'sonner'; // or your toast library

export function useTasks(userId: string) {
  return useQuery({
    queryKey: ['tasks', userId],
    queryFn: () => taskApi.getAll(userId),
    enabled: !!userId,
  });
}

export function useTask(userId: string, taskId: number) {
  return useQuery({
    queryKey: ['tasks', userId, taskId],
    queryFn: () => taskApi.getById(userId, taskId),
    enabled: !!userId && !!taskId,
  });
}

export function useCreateTask(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TaskCreate) => taskApi.create(userId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', userId] });
      toast.success('Task created successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to create task');
    },
  });
}

export function useUpdateTask(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ taskId, data }: { taskId: number; data: TaskUpdate }) =>
      taskApi.update(userId, taskId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', userId] });
      toast.success('Task updated successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to update task');
    },
  });
}

export function useDeleteTask(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: number) => taskApi.delete(userId, taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', userId] });
      toast.success('Task deleted successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to delete task');
    },
  });
}

export function useToggleComplete(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: number) => taskApi.toggleComplete(userId, taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', userId] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to update task');
    },
  });
}
```

## Auth Hooks
`hooks/use-auth.ts`:
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { authApi, LoginRequest, SignupRequest } from '@/lib/api/auth';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

export function useAuth() {
  return useQuery({
    queryKey: ['auth', 'user'],
    queryFn: authApi.me,
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useLogin() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auth', 'user'] });
      toast.success('Logged in successfully!');
      router.push('/tasks');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Login failed');
    },
  });
}

export function useSignup() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SignupRequest) => authApi.signup(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auth', 'user'] });
      toast.success('Account created successfully!');
      router.push('/tasks');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Signup failed');
    },
  });
}

export function useLogout() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      queryClient.clear();
      router.push('/login');
    },
  });
}
```

## Usage Examples

#### In a Component
```typescript
'use client';

import { useTasks, useCreateTask } from '@/hooks/use-tasks';
import { useAuth } from '@/hooks/use-auth';

export function TaskList() {
  const { data: user } = useAuth();
  const { data: tasks, isLoading, error } = useTasks(user?.id || '');
  const createTask = useCreateTask(user?.id || '');

  const handleCreate = () => {
    createTask.mutate({
      title: 'New Task',
      description: 'Task description',
    });
  };

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading tasks</div>;

  return (
    <div>
      <button onClick={handleCreate}>Create Task</button>
      {tasks?.map((task) => (
        <div key={task.id}>{task.title}</div>
      ))}
    </div>
  );
}
```

## Hook Best Practices
- Use enabled option for conditional queries
- Always invalidate related queries on mutations
- Provide optimistic updates where possible
- Handle loading and error states
- Use toast notifications for user feedback
- Keep hooks focused and reusable
