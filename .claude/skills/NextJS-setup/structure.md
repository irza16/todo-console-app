# Next.js Project Structure

## Initialize Next.js Project
```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"
```

Answer prompts:
- ✅ TypeScript
- ✅ ESLint
- ✅ Tailwind CSS
- ✅ App Router
- ❌ src/ directory
- ✅ Import alias (@/*)

## Project Structure
```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page
│   ├── (auth)/             # Auth group
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── signup/
│   │       └── page.tsx
│   ├── tasks/              # Tasks pages
│   │   ├── page.tsx
│   │   └── [id]/
│   │       └── page.tsx
│   └── api/                # API routes (optional)
│       └── auth/
│           └── route.ts
├── components/
│   ├── ui/                 # shadcn/ui components
│   ├── layout/
│   │   ├── header.tsx
│   │   ├── footer.tsx
│   │   └── sidebar.tsx
│   ├── tasks/
│   │   ├── task-list.tsx
│   │   ├── task-card.tsx
│   │   └── task-form.tsx
│   └── auth/
│       ├── login-form.tsx
│       └── signup-form.tsx
├── lib/
│   ├── api.ts              # API client
│   ├── auth.ts             # Auth helpers
│   └── utils.ts            # Utility functions
├── hooks/
│   ├── use-tasks.ts
│   └── use-auth.ts
├── types/
│   └── index.ts
├── public/
│   └── images/
├── .env.local
├── .env.example
├── next.config.mjs
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

## Root Layout
`app/layout.tsx`:
```typescript
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Todo App - Phase II",
  description: "Full-stack todo application built with Next.js and FastAPI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-background">
          {children}
        </div>
      </body>
    </html>
  );
}
```

## TypeScript Types
`types/index.ts`:
```typescript
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at?: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
}

export interface User {
  id: string;
  email: string;
  name: string;
}

export interface ApiError {
  message: string;
  detail?: string;
}
```

## Utility Functions
`lib/utils.ts`:
```typescript
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}
```

## Example Page
`app/page.tsx`:
```typescript
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <main className="container mx-auto px-4 py-16">
      <div className="max-w-2xl mx-auto text-center space-y-8">
        <h1 className="text-4xl font-bold tracking-tight">
          Welcome to Todo App
        </h1>
        <p className="text-xl text-muted-foreground">
          Manage your tasks efficiently with our modern todo application
        </p>

        <div className="flex gap-4 justify-center">
          <Button asChild size="lg">
            <Link href="/tasks">View Tasks</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/login">Login</Link>
          </Button>
        </div>

        <Card className="mt-12">
          <CardHeader>
            <CardTitle>Features</CardTitle>
            <CardDescription>
              Everything you need to stay organized
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4">
            <div className="flex items-start gap-4">
              <div className="rounded-lg bg-primary p-2 text-primary-foreground">
                ✓
              </div>
              <div className="text-left">
                <h3 className="font-semibold">Create & Manage Tasks</h3>
                <p className="text-sm text-muted-foreground">
                  Add, update, and delete tasks with ease
                </p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="rounded-lg bg-primary p-2 text-primary-foreground">
                ✓
              </div>
              <div className="text-left">
                <h3 className="font-semibold">Track Progress</h3>
                <p className="text-sm text-muted-foreground">
                  Mark tasks as complete and track your productivity
                </p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="rounded-lg bg-primary p-2 text-primary-foreground">
                ✓
              </div>
              <div className="text-left">
                <h3 className="font-semibold">Secure Authentication</h3>
                <p className="text-sm text-muted-foreground">
                  Your data is protected with modern authentication
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
```
