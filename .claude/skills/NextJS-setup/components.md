# Next.js Components

## Install shadcn/ui
```bash
npx shadcn@latest init
```

Answer prompts:
- Style: Default
- Base color: Slate
- CSS variables: Yes

Install commonly used components:
```bash
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
npx shadcn@latest add label
npx shadcn@latest add form
npx shadcn@latest add dialog
npx shadcn@latest add dropdown-menu
npx shadcn@latest add toast
```

## Common Components

### Loading Component
`components/ui/loading.tsx`:
```typescript
export function Loading() {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    </div>
  );
}
```

### Error Component
`components/ui/error.tsx`:
```typescript
interface ErrorProps {
  message: string;
  retry?: () => void;
}

export function Error({ message, retry }: ErrorProps) {
  return (
    <div className="p-8 text-center">
      <p className="text-destructive mb-4">{message}</p>
      {retry && (
        <Button onClick={retry} variant="outline">
          Try Again
        </Button>
      )}
    </div>
  );
}
```

## Component Best Practices
- Use server components by default
- Use client components only when necessary (interactivity, hooks)
- Keep components small and focused
- Use proper TypeScript types
- Follow shadcn/ui patterns for consistency
- Add error boundaries where needed
- Implement loading states for async operations

## Validation Checklist
- [ ] shadcn/ui components installed
- [ ] Component library configured
- [ ] Common utility components created
- [ ] Components properly typed with TypeScript
- [ ] Loading and error states implemented
