"use client";

import { useState } from "react";
import { useUpdateTask, useToggleComplete, useDeleteTask } from "@/hooks/use-tasks";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Trash2, Edit2, X, Check, Circle } from "lucide-react";
import type { Task } from "@/types";
import { TagsInput } from "./TagsInput";

interface TaskCardProps {
  task: Task;
}

const normalizeTags = (tags: string | string[] | undefined): string[] => {
  if (!tags) return [];
  return typeof tags === 'string' ? tags.split(',').filter(Boolean) : tags;
};

export function TaskCard({ task }: TaskCardProps) {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [showCompleteConfirm, setShowCompleteConfirm] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || "");
  const [editPriority, setEditPriority] = useState(task.priority || "Medium");
  const [editTags, setEditTags] = useState<string[]>(normalizeTags(task.tags));
  const [editIsRecurring, setEditIsRecurring] = useState(task.is_recurring || false);
  const [editRecurrencePattern, setEditRecurrencePattern] = useState<'daily' | 'weekly' | 'monthly' | 'weekdays'>(task.recurrence_pattern || 'daily');

  const updateTask = useUpdateTask();
  const toggleComplete = useToggleComplete();
  const deleteTask = useDeleteTask();

  if (!user) return null;

  const isPending = toggleComplete.isPending || updateTask.isPending || deleteTask.isPending;

  // Debug log to see the actual task data
  console.log('Task data:', {
    id: task.id,
    title: task.title,
    priority: task.priority,
    tags: task.tags,
    is_recurring: task.is_recurring,
    recurrence_pattern: task.recurrence_pattern
  });

  const handleToggleComplete = () => {
    if (task.completed) {
      // Unmark complete - no confirmation needed
      toggleComplete.mutate(task.id);
    } else {
      // Mark complete - show confirmation
      setShowCompleteConfirm(true);
    }
  };

  const handleConfirmComplete = () => {
    toggleComplete.mutate(task.id);
    setShowCompleteConfirm(false);
  };

  const handleCancelComplete = () => {
    setShowCompleteConfirm(false);
  };

  const handleDelete = () => {
    if (confirm("Are you sure you want to delete this task?")) {
      deleteTask.mutate(task.id);
    }
  };

  const handleSaveEdit = () => {
    if (editTitle.trim()) {
      updateTask.mutate({
        taskId: task.id,
        data: {
          title: editTitle.trim(),
          description: editDescription.trim() || undefined,
          priority: editPriority,
          tags: editTags,
          is_recurring: editIsRecurring,
          recurrence_pattern: editIsRecurring ? editRecurrencePattern : null,
        },
      });
      setIsEditing(false);
    }
  };

  const handleCancelEdit = () => {
    setEditTitle(task.title);
    setEditDescription(task.description || "");
    setEditPriority(task.priority || "Medium");
    setEditTags(normalizeTags(task.tags));
    setEditIsRecurring(task.is_recurring || false);
    setEditRecurrencePattern((task.recurrence_pattern || 'daily') as 'daily' | 'weekly' | 'monthly' | 'weekdays');
    setIsEditing(false);
  };

  return (
    <Card className={cn("transition-all", task.completed && "bg-muted/50")}>
      {isEditing ? (
        <>
          <CardHeader className="pb-2">
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              className="w-full text-lg font-medium bg-transparent border-b focus:outline-none focus:border-primary"
              placeholder="Task title"
              autoFocus
            />
          </CardHeader>
          <CardContent className="pb-2 space-y-3">
            <textarea
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              className="w-full text-sm text-muted-foreground bg-transparent border rounded p-2 focus:outline-none focus:border-primary resize-none"
              placeholder="Description (optional)"
              rows={2}
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium text-muted-foreground mb-1 block">Priority</label>
                <select
                  value={editPriority}
                  onChange={(e) => setEditPriority(e.target.value as 'Low' | 'Medium' | 'High' | 'Urgent')}
                  className="w-full border rounded p-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 bg-background"
                >
                  <option value="Low">🟢 Low</option>
                  <option value="Medium">🟡 Medium</option>
                  <option value="High">🟠 High</option>
                  <option value="Urgent">🔴 Urgent</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium text-muted-foreground mb-1 block">Tags</label>
                <TagsInput
                  value={editTags}
                  onChange={setEditTags}
                />
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id={`recurring-${task.id}`}
                checked={editIsRecurring}
                onChange={(e) => setEditIsRecurring(e.target.checked)}
                className="rounded"
              />
              <label htmlFor={`recurring-${task.id}`} className="text-sm font-medium text-muted-foreground">
                Recurring Task
              </label>
            </div>

            {editIsRecurring && (
              <div>
                <label className="text-sm font-medium text-muted-foreground mb-1 block">Recurrence Pattern</label>
                <select
                  value={editRecurrencePattern || 'daily'}
                  onChange={(e) => setEditRecurrencePattern(e.target.value as 'daily' | 'weekly' | 'monthly' | 'weekdays')}
                  className="w-full border rounded p-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 bg-background"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="weekdays">Weekdays</option>
                </select>
              </div>
            )}
          </CardContent>
          <CardFooter className="flex justify-end gap-2">
            <Button variant="ghost" size="sm" onClick={handleCancelEdit}>
              <X className="h-4 w-4" />
            </Button>
            <Button variant="default" size="sm" onClick={handleSaveEdit} disabled={isPending}>
              <Check className="h-4 w-4" />
            </Button>
          </CardFooter>
        </>
      ) : showCompleteConfirm ? (
        <>
          <CardHeader className="pb-2">
            <div className="flex items-start gap-3">
              <Circle className="h-5 w-5 mt-0.5 text-muted-foreground" />
              <div className="flex-1">
                <p className="text-lg font-medium">{task.title}</p>
                {task.description && (
                  <p className="text-sm text-muted-foreground mt-1">{task.description}</p>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent className="pb-2">
            <p className="text-sm text-muted-foreground">
              Do you want to mark this task as done?
            </p>
          </CardContent>
          <CardFooter className="flex justify-end gap-2">
            <Button variant="ghost" size="sm" onClick={handleCancelComplete}>
              No, keep it
            </Button>
            <Button variant="default" size="sm" onClick={handleConfirmComplete} disabled={isPending}>
              {isPending ? (
                <>
                  <span className="animate-spin mr-2">⏳</span>
                  Saving...
                </>
              ) : (
                <>
                  <Check className="h-4 w-4 mr-2" />
                  Yes, mark done
                </>
              )}
            </Button>
          </CardFooter>
        </>
      ) : (
        <>
          <CardHeader className="pb-2">
            <div className="flex items-start gap-3">
              <button
                onClick={handleToggleComplete}
                disabled={isPending}
                className={cn(
                  "mt-0.5 h-5 w-5 rounded-full border-2 flex items-center justify-center transition-all",
                  task.completed
                    ? "bg-green-500 border-green-500"
                    : "border-muted-foreground hover:border-green-500"
                )}
              >
                {task.completed && <Check className="h-3 w-3 text-white" />}
              </button>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p
                    className={cn(
                      "text-lg font-medium",
                      task.completed && "line-through text-muted-foreground"
                    )}
                  >
                    {task.title}
                  </p>
                  {task.priority && (
                    <span className={cn(
                      "text-xs px-2 py-1 rounded-full",
                      task.priority === 'Low' && 'bg-green-100 text-green-800',
                      task.priority === 'Medium' && 'bg-yellow-100 text-yellow-800',
                      task.priority === 'High' && 'bg-orange-100 text-orange-800',
                      task.priority === 'Urgent' && 'bg-red-100 text-red-800'
                    )}>
                      {task.priority === 'Low' && '🟢 Low'}
                      {task.priority === 'Medium' && '🟡 Medium'}
                      {task.priority === 'High' && '🟠 High'}
                      {task.priority === 'Urgent' && '🔴 Urgent'}
                    </span>
                  )}
                  {task.is_recurring && task.recurrence_pattern && (
                    <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                      🔄 {task.recurrence_pattern}
                    </span>
                  )}
                </div>
                {task.description && (
                  <p
                    className={cn(
                      "text-sm text-muted-foreground mt-1",
                      task.completed && "line-through"
                    )}
                  >
                    {task.description}
                  </p>
                )}
                {task.tags && task.tags.length > 0 && (
  <div className="flex flex-wrap gap-1 mt-2">
    {(typeof task.tags === 'string' ? task.tags.split(',') : task.tags).map((tag, i) => (
      <span key={i} className="px-2 py-1 bg-gray-100 rounded-full text-xs">
        {tag}
      </span>
    ))}
  </div>
)}
              </div>
            </div>
          </CardHeader>
          <CardContent className="pb-2">
            <p className="text-xs text-muted-foreground">
              Created: {new Date(task.created_at).toLocaleDateString()}
            </p>
          </CardContent>
          <CardFooter className="flex justify-end gap-2 pt-0">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsEditing(true)}
              disabled={isPending}
            >
              <Edit2 className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleDelete}
              disabled={isPending}
              className="text-destructive hover:text-destructive"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </CardFooter>
        </>
      )}
    </Card>
  );
}
