"use client";

import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { LogOut, User } from "lucide-react";

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="border-b bg-card">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-semibold">Todo App</h1>
          <nav className="ml-8 flex items-center space-x-6 text-sm font-medium">
            <a href="/tasks" className="transition-colors hover:text-foreground/80 text-foreground">
              Tasks
            </a>
            <a href="/chat" className="transition-colors hover:text-foreground/80 text-foreground">
              Chat Assistant
            </a>
          </nav>
        </div>

        {user && (
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <User className="h-4 w-4" />
              <span>{user.name}</span>
              <span className="text-xs">({user.email})</span>
            </div>
            <Button variant="outline" size="sm" onClick={logout}>
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        )}
      </div>
    </header>
  );
}
