# Quickstart: Todo Console App

## Running the Application

```bash
python src/main.py
```

That's it! No installation, no dependencies, no configuration required.

## System Requirements

- Python 3.13 or higher
- Terminal/console access
- No external packages needed

## Menu Options

```
=== Todo Console App ===
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Toggle Complete
6. Exit
```

## Usage Examples

### Adding a Task

```
Enter your choice (1-6): 1

=== Add Task ===
Enter task title: Buy groceries
Enter task description (optional): Milk, eggs, bread, butter

Task added successfully! (ID: 1)
```

### Viewing Tasks

```
Enter your choice (1-6): 2

=== Your Tasks ===
[Pending] 1. Buy groceries - Milk, eggs, bread, butter

Total: 1 task
```

### Marking a Task Complete

```
Enter your choice (1-6): 5

=== Toggle Complete ===
Enter task ID: 1

Task 1 marked as Completed!
```

### Updating a Task

```
Enter your choice (1-6): 3

=== Update Task ===
Enter task ID: 1

Current: Buy groceries - Milk, eggs, bread, butter

Enter new title (press Enter to keep current): Buy organic groceries
Enter new description (press Enter to keep current): Milk, eggs, bread, butter, cheese

Task 1 updated successfully!
```

### Deleting a Task

```
Enter your choice (1-6): 4

=== Delete Task ===
Enter task ID: 1

Task to delete:
  [Pending] 1. Buy groceries - Milk, eggs, bread, butter

Are you sure you want to delete this task? (y/n): y

Task 1 deleted successfully!
```

## Error Handling Examples

### Invalid Menu Choice

```
Enter your choice (1-6): 99

Invalid choice. Please enter a number between 1 and 6.
```

### Non-Numeric Task ID

```
Enter your choice (1-6): 5

=== Toggle Complete ===
Enter task ID: abc

Please enter a valid number.
```

### Invalid Task ID

```
Enter your choice (1-6): 5

=== Toggle Complete ===
Enter task ID: 999

Task with ID 999 not found.
```

### Empty Title

```
Enter your choice (1-6): 1

=== Add Task ===
Enter task title:
Title cannot be empty. Please enter a title (1-200 characters).

Enter task title: Valid title
```

## Notes

- All data is stored in memory and lost when the application exits
- Task IDs start at 1 and increment, never reused
- Maximum 200 characters for titles, 1000 for descriptions
- Confirmation is required before deleting a task
