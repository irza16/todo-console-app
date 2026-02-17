"use client";

import { useTasks, useCreateTask } from "@/hooks/use-tasks";
import { useAuth } from "@/hooks/use-auth";
import { TaskCard } from "./task-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Loader2 } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { PrioritySelector } from "./PrioritySelector";
import { TagsInput } from "./TagsInput";

export function TaskList() {
  const { user, isLoading: authLoading } = useAuth();
  const { data: tasksData, isLoading: tasksLoading, error } = useTasks();
  const createTask = useCreateTask();
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [newTaskDescription, setNewTaskDescription] = useState("");
  const [newTaskPriority, setNewTaskPriority] = useState<"Low" | "Medium" | "High" | "Urgent">("Medium");
  const [newTaskTags, setNewTaskTags] = useState<string[]>([]);
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurrencePattern, setRecurrencePattern] = useState<'daily' | 'weekly' | 'monthly' | 'weekdays'>('daily');
  const [searchQuery, setSearchQuery] = useState("");
  const [filterPriority, setFilterPriority] = useState<string | null>(null);

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
          priority: newTaskPriority,
          tags: newTaskTags.length > 0 ? newTaskTags.join(',') : undefined,
          is_recurring: isRecurring,
          recurrence_pattern: isRecurring ? recurrencePattern : null,
        },
        {
          onSuccess: () => {
            setNewTaskTitle("");
            setNewTaskDescription("");
            setNewTaskPriority("Medium");
            setNewTaskTags([]);
            setIsRecurring(false);
            setRecurrencePattern('daily');
          },
        }
      );
    }
  };

  const tasks = tasksData?.tasks || [];

  // Filter and search tasks
  const filteredTasks = tasks.filter(task => {
    // Apply search filter
    const matchesSearch = !searchQuery ||
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (task.description && task.description.toLowerCase().includes(searchQuery.toLowerCase()));

    // Apply priority filter
    const matchesPriority = !filterPriority || task.priority === filterPriority;

    return matchesSearch && matchesPriority;
  });

  return (
    <div className="space-y-6">
      {/* Search and Filter Bar */}
      <div className="bg-card border rounded-lg p-4 space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <Input
            placeholder="Search tasks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1"
          />
        </div>

        <div className="flex flex-wrap gap-2">
          <Button
            variant={filterPriority === null ? "default" : "outline"}
            size="sm"
            onClick={() => setFilterPriority(null)}
          >
            All
          </Button>
          <Button
            variant={filterPriority === "Urgent" ? "default" : "outline"}
            size="sm"
            onClick={() => setFilterPriority("Urgent")}
            className="bg-red-500 hover:bg-red-600 text-white"
          >
            🔴 Urgent
          </Button>
          <Button
            variant={filterPriority === "High" ? "default" : "outline"}
            size="sm"
            onClick={() => setFilterPriority("High")}
            className="bg-orange-500 hover:bg-orange-600 text-white"
          >
            🟠 High
          </Button>
          <Button
            variant={filterPriority === "Medium" ? "default" : "outline"}
            size="sm"
            onClick={() => setFilterPriority("Medium")}
            className="bg-yellow-500 hover:bg-yellow-600 text-white"
          >
            🟡 Medium
          </Button>
          <Button
            variant={filterPriority === "Low" ? "default" : "outline"}
            size="sm"
            onClick={() => setFilterPriority("Low")}
            className="bg-green-500 hover:bg-green-600 text-white"
          >
            🟢 Low
          </Button>
        </div>
      </div>

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

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium text-muted-foreground mb-1 block">Priority</label>
              <PrioritySelector
                value={newTaskPriority}
                onChange={setNewTaskPriority}
              />
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground mb-1 block">Tags</label>
              <TagsInput
                value={newTaskTags}
                onChange={setNewTaskTags}
              />
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="isRecurring"
              checked={isRecurring}
              onChange={(e) => setIsRecurring(e.target.checked)}
              className="rounded"
            />
            <label htmlFor="isRecurring" className="text-sm font-medium text-muted-foreground">
              Recurring Task
            </label>
          </div>

          {isRecurring && (
            <div>
              <label className="text-sm font-medium text-muted-foreground mb-1 block">Recurrence Pattern</label>
              <select
                value={recurrencePattern}
                onChange={(e) => setRecurrencePattern(e.target.value as 'daily' | 'weekly' | 'monthly' | 'weekdays')}
                className="w-full border rounded p-2 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 bg-background"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="weekdays">Weekdays</option>
              </select>
            </div>
          )}

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
      <div className={cn("space-y-3", filteredTasks.length === 0 && "text-center py-12")}>
        {filteredTasks.length === 0 ? (
          <div className="text-muted-foreground">
            <p className="text-lg font-medium">
              {tasks.length === 0 ? "No tasks yet" : "No tasks match your filters"}
            </p>
            <p className="text-sm">
              {tasks.length === 0 ? "Create your first task above!" : "Try adjusting your search or filter."}
            </p>
          </div>
        ) : (
          filteredTasks.map((task) => <TaskCard key={task.id} task={task} />)
        )}
      </div>
    </div>
  );
}
