"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { taskApi } from "@/lib/api";
import { useAuth } from "./use-auth";
import type { Task, TaskCreate, TaskUpdate } from "@/types";

export function useTasks() {
  const { user, isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ["tasks", user?.id],
    queryFn: () => {
      if (!user) throw new Error("Not authenticated");
      return taskApi.listTasks(user.id);
    },
    enabled: isAuthenticated && !!user,
  });
}

export function useTask(userId: number, taskId: number) {
  return useQuery({
    queryKey: ["task", userId, taskId],
    queryFn: () => taskApi.getTask(userId, taskId),
    enabled: !!userId && !!taskId,
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();
  const { user } = useAuth();

  return useMutation({
    mutationFn: (data: TaskCreate) => {
      if (!user) throw new Error("Not authenticated");
      return taskApi.createTask(user.id, data);
    },
    onSuccess: () => {
      if (user) {
        queryClient.invalidateQueries({ queryKey: ["tasks", user.id] });
      }
    },
  });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();
  const { user } = useAuth();

  return useMutation({
    mutationFn: ({ taskId, data }: { taskId: number; data: Partial<TaskUpdate> }) => {
      if (!user) throw new Error("Not authenticated");
      return taskApi.updateTask(user.id, taskId, data);
    },
    onSuccess: (_, variables) => {
      if (user) {
        queryClient.invalidateQueries({ queryKey: ["tasks", user.id] });
        queryClient.invalidateQueries({ queryKey: ["task", user.id, variables.taskId] });
      }
    },
  });
}

export function useToggleComplete() {
  const queryClient = useQueryClient();
  const { user } = useAuth();

  return useMutation({
    mutationFn: (taskId: number) => {
      if (!user) throw new Error("Not authenticated");
      return taskApi.toggleComplete(user.id, taskId);
    },
    onSuccess: (_, taskId) => {
      if (user) {
        queryClient.invalidateQueries({ queryKey: ["tasks", user.id] });
        queryClient.invalidateQueries({ queryKey: ["task", user.id, taskId] });
      }
    },
  });
}

export function useDeleteTask() {
  const queryClient = useQueryClient();
  const { user } = useAuth();

  return useMutation({
    mutationFn: (taskId: number) => {
      if (!user) throw new Error("Not authenticated");
      return taskApi.deleteTask(user.id, taskId);
    },
    onSuccess: (_, taskId) => {
      if (user) {
        queryClient.invalidateQueries({ queryKey: ["tasks", user.id] });
        queryClient.invalidateQueries({ queryKey: ["task", user.id, taskId] });
      }
    },
  });
}
