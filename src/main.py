#!/usr/bin/env python3
"""
Todo Console App - Phase I

A simple command-line task manager built with Python 3 standard library only.
All data is stored in-memory and lost when the application exits.
"""

# ============================================================================
# Constants
# ============================================================================

MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000
MIN_ID = 1
MENU_OPTIONS = 6

# ============================================================================
# Global State
# ============================================================================

tasks = []
next_id = 1

# ============================================================================
# Helper Functions
# ============================================================================


def get_string_input(prompt, min_len=1, max_len=None):
    """
    Get a validated string input from the user.

    Args:
        prompt: The prompt to display to the user
        min_len: Minimum allowed length (default 1)
        max_len: Maximum allowed length (default None for unlimited)

    Returns:
        The validated string input (stripped of leading/trailing whitespace)

    Raises:
        ValueError: If input doesn't meet validation criteria
    """
    while True:
        user_input = input(prompt).strip()

        # Check minimum length
        if len(user_input) < min_len:
            if min_len == 1:
                print("Title cannot be empty. Please enter a title (1-200 characters).")
            else:
                print(f"Input must be at least {min_len} character(s).")
            continue

        # Check maximum length
        if max_len is not None and len(user_input) > max_len:
            print(f"Input exceeds maximum length of {max_len} characters. Please shorten your input.")
            continue

        return user_input


def get_int_input(prompt, min_val=None, max_val=None):
    """
    Get a validated integer input from the user.

    Args:
        prompt: The prompt to display to the user
        min_val: Minimum allowed value (default None for unlimited)
        max_val: Maximum allowed value (default None for unlimited)

    Returns:
        The validated integer input

    Raises:
        ValueError: If input is not a valid integer or doesn't meet validation criteria
    """
    while True:
        user_input = input(prompt).strip()

        # Check if input is numeric
        if not user_input.isdigit():
            print("Please enter a valid number.")
            continue

        value = int(user_input)

        # Check minimum value
        if min_val is not None and value < min_val:
            print(f"Please enter a number greater than or equal to {min_val}.")
            continue

        # Check maximum value
        if max_val is not None and value > max_val:
            print(f"Please enter a number less than or equal to {max_val}.")
            continue

        return value


def find_task(task_id):
    """
    Find a task by its ID.

    Args:
        task_id: The ID of the task to find

    Returns:
        The task dictionary if found, None otherwise
    """
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def format_status(completed):
    """
    Format the completion status for display.

    Args:
        completed: Boolean indicating if task is completed

    Returns:
        String "[Completed]" or "[Pending]"
    """
    return "[Completed]" if completed else "[Pending]"


# ============================================================================
# Operation Functions
# ============================================================================


def add_task():
    """
    Add a new task to the task list.

    Gets task title and optional description from user,
    creates a new task with auto-assigned ID, and adds
    it to the tasks list.
    """
    global next_id

    print("\n=== Add Task ===")
    title = get_string_input("Enter task title: ", 1, MAX_TITLE_LENGTH)
    description = get_string_input("Enter task description (optional): ", 0, MAX_DESCRIPTION_LENGTH)

    task = {
        "id": next_id,
        "title": title,
        "description": description,
        "completed": False
    }

    tasks.append(task)
    print(f"Task added successfully! (ID: {next_id})")

    next_id += 1


def view_tasks():
    """
    Display all tasks in the task list.

    Shows each task with its ID, status, title, and description.
    Handles empty task list gracefully.
    """
    print("\n=== Your Tasks ===")

    if not tasks:
        print("No tasks yet. Add some tasks!")
    else:
        for task in tasks:
            status = format_status(task["completed"])
            task_num = task["id"]
            title = task["title"]
            description = task["description"]

            # Only show description if it's not empty
            if description:
                print(f"{status} {task_num}. {title} - {description}")
            else:
                print(f"{status} {task_num}. {title}")

    print(f"\nTotal: {len(tasks)} task(s)")


def update_task():
    """
    Update an existing task's title and/or description.

    Gets task ID from user, finds the task, allows user to
    modify title and description (keeping current values if
    user presses Enter), and updates the task.
    """
    print("\n=== Update Task ===")

    task_id = get_int_input("Enter task ID: ", MIN_ID)

    task = find_task(task_id)
    if task is None:
        print(f"Task with ID {task_id} not found.")
        return

    print(f"\nCurrent: {task['title']} - {task['description']}")

    # Get new title (empty string keeps current)
    new_title = get_string_input(
        "Enter new title (press Enter to keep current): ",
        0, MAX_TITLE_LENGTH
    )
    if not new_title:
        new_title = task["title"]

    # Get new description (empty string keeps current)
    new_description = get_string_input(
        "Enter new description (press Enter to keep current): ",
        0, MAX_DESCRIPTION_LENGTH
    )
    if not new_description:
        new_description = task["description"]

    # Update the task
    task["title"] = new_title
    task["description"] = new_description

    print(f"Task {task_id} updated successfully!")


def delete_task():
    """
    Delete a task from the task list.

    Gets task ID from user, finds the task, shows task details,
    prompts for confirmation (y/n), and removes the task if confirmed.
    """
    print("\n=== Delete Task ===")

    task_id = get_int_input("Enter task ID: ", MIN_ID)

    task = find_task(task_id)
    if task is None:
        print(f"Task with ID {task_id} not found.")
        return

    # Show task details to be deleted
    status = format_status(task["completed"])
    print(f"\nTask to delete:")
    if task["description"]:
        print(f"  {status} {task['id']}. {task['title']} - {task['description']}")
    else:
        print(f"  {status} {task['id']}. {task['title']}")

    # Get confirmation
    confirm = input("\nAre you sure you want to delete this task? (y/n): ").strip().lower()

    if confirm == 'y':
        tasks.remove(task)
        print(f"Task {task_id} deleted successfully!")
    else:
        print("Task deletion cancelled.")


def toggle_complete():
    """
    Toggle the completion status of a task.

    Gets task ID from user, finds the task, toggles the
    completed status, and shows confirmation.
    """
    print("\n=== Toggle Complete ===")

    task_id = get_int_input("Enter task ID: ", MIN_ID)

    task = find_task(task_id)
    if task is None:
        print(f"Task with ID {task_id} not found.")
        return

    # Toggle the completion status
    task["completed"] = not task["completed"]

    status = format_status(task["completed"])
    print(f"Task {task_id} marked as {status}!")


# ============================================================================
# Menu System
# ============================================================================


def display_menu():
    """Display the main menu options."""
    print("\n=== Todo Console App ===")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Toggle Complete")
    print("6. Exit")


def main_menu():
    """
    Main menu loop that dispatches to operation functions.

    Continuously displays menu, gets user choice, and calls
    the appropriate operation function. Exits when user
    selects option 6.
    """
    while True:
        display_menu()
        choice = get_int_input("Enter your choice (1-6): ", 1, MENU_OPTIONS)

        if choice == 1:
            add_task()
        elif choice == 2:
            view_tasks()
        elif choice == 3:
            update_task()
        elif choice == 4:
            delete_task()
        elif choice == 5:
            toggle_complete()
        elif choice == 6:
            print("\nGoodbye! Thanks for using Todo Console App.")
            break


def main():
    """Entry point for the application."""
    print("Welcome to Todo Console App!")
    print("A simple command-line task manager.\n")
    main_menu()


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    main()
