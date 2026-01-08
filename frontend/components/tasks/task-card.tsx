"use client";

import { useState } from "react";
import { useUpdateTask, useToggleComplete, useDeleteTask } from "@/hooks/use-tasks";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Trash2, Edit2, X, Check, Circle } from "lucide-react";
import type { Task } from "@/types";

interface TaskCardProps {
  task: Task;
}

export function TaskCard({ task }: TaskCardProps) {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [showCompleteConfirm, setShowCompleteConfirm] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || "");

  const updateTask = useUpdateTask();
  const toggleComplete = useToggleComplete();
  const deleteTask = useDeleteTask();

  if (!user) return null;

  const isPending = toggleComplete.isPending || updateTask.isPending || deleteTask.isPending;

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
        },
      });
      setIsEditing(false);
    }
  };

  const handleCancelEdit = () => {
    setEditTitle(task.title);
    setEditDescription(task.description || "");
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
          <CardContent className="pb-2">
            <textarea
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              className="w-full text-sm text-muted-foreground bg-transparent border rounded p-2 focus:outline-none focus:border-primary resize-none"
              placeholder="Description (optional)"
              rows={2}
            />
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
                <p
                  className={cn(
                    "text-lg font-medium",
                    task.completed && "line-through text-muted-foreground"
                  )}
                >
                  {task.title}
                </p>
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
