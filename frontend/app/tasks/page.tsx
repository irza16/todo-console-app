"use client";

import { useAuth } from "@/hooks/use-auth";
import { TaskList } from "@/components/tasks/task-list";
import { Header } from "@/components/tasks/header";
import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function TasksPage() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8 max-w-2xl">
        <div className="mb-6">
          <h2 className="text-2xl font-bold">My Tasks</h2>
          <p className="text-muted-foreground">
            {user ? `Welcome back, ${user.name}!` : "Manage your tasks below"}
          </p>
        </div>
        <TaskList />
      </main>
    </div>
  );
}
