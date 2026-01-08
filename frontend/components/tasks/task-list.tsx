"use client";

import { useTasks, useCreateTask } from "@/hooks/use-tasks";
import { useAuth } from "@/hooks/use-auth";
import { TaskCard } from "./task-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Loader2 } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

export function TaskList() {
  const { user, isLoading: authLoading } = useAuth();
  const { data: tasksData, isLoading: tasksLoading, error } = useTasks();
  const createTask = useCreateTask();
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [newTaskDescription, setNewTaskDescription] = useState("");

  if (authLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Please log in to view your tasks</p>
      </div>
    );
  }

  if (tasksLoading) {
    return (
      <div className="space-y-4">
        <div className="h-12 bg-muted animate-pulse rounded-lg" />
        <div className="h-24 bg-muted animate-pulse rounded-lg" />
        <div className="h-24 bg-muted animate-pulse rounded-lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive">Failed to load tasks</p>
        <p className="text-sm text-muted-foreground mt-2">
          Please try refreshing the page
        </p>
      </div>
    );
  }

  const handleCreateTask = (e: React.FormEvent) => {
    e.preventDefault();
    if (newTaskTitle.trim()) {
      createTask.mutate(
        {
          title: newTaskTitle.trim(),
          description: newTaskDescription.trim() || undefined,
        },
        {
          onSuccess: () => {
            setNewTaskTitle("");
            setNewTaskDescription("");
          },
        }
      );
    }
  };

  const tasks = tasksData?.tasks || [];

  return (
    <div className="space-y-6">
      {/* New Task Form */}
      <form onSubmit={handleCreateTask} className="bg-card border rounded-lg p-4">
        <div className="space-y-3">
          <Input
            placeholder="What needs to be done?"
            value={newTaskTitle}
            onChange={(e) => setNewTaskTitle(e.target.value)}
            disabled={createTask.isPending}
          />
          <Input
            placeholder="Description (optional)"
            value={newTaskDescription}
            onChange={(e) => setNewTaskDescription(e.target.value)}
            disabled={createTask.isPending}
          />
          <Button
            type="submit"
            disabled={!newTaskTitle.trim() || createTask.isPending}
            className="w-full"
          >
            {createTask.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Adding...
              </>
            ) : (
              <>
                <Plus className="mr-2 h-4 w-4" />
                Add Task
              </>
            )}
          </Button>
        </div>
      </form>

      {/* Tasks List */}
      <div className={cn("space-y-3", tasks.length === 0 && "text-center py-12")}>
        {tasks.length === 0 ? (
          <div className="text-muted-foreground">
            <p className="text-lg font-medium">No tasks yet</p>
            <p className="text-sm">Create your first task above!</p>
          </div>
        ) : (
          tasks.map((task) => <TaskCard key={task.id} task={task} />)
        )}
      </div>
    </div>
  );
}
