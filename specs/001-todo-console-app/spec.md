# Feature Specification: Todo Console App - Phase I

**Feature Branch**: `001-todo-console-app`
**Created**: 2025-12-07
**Status**: Draft
**Input**: User description: "/sp.specify

Project: Todo Console App - Phase I command-line task manager

Target audience: Hackathon judges evaluating spec-driven development proficiency

Focus: Demonstrating clear specifications generate working code without manual coding

Success criteria:
- User completes full task lifecycle (add → view → update → complete → delete) without crashes
- All 5 operations work correctly: add_task(), view_tasks(), update_task(), delete_task(), toggle_complete()
- Invalid inputs handled gracefully (empty titles, non-numeric IDs, invalid menu choices, out-of-range IDs)
- Menu loops continuously until user explicitly exits
- Task IDs auto-increment from 1 and never reuse deleted IDs
- All operations provide clear confirmation messages
- Code generated entirely by Claude Code from specifications (zero manual coding)
- Judges can run immediately: `python src/main.py` with no setup

Constraints:
- Language: Python 3.13+ standard library only (no pip packages)
- Storage: In-memory Python list (data lost on exit, no persistence)
- Interface: Terminal/console only with numbered menu (6 options)
- File structure: Single file at src/main.py
- Title: 1-200 characters (required, validated)
- Description: 0-1000 characters (optional)
- Timeline: Complete by December 7, 2025

Building:
- 5 core operations (add, view, update, delete, mark complete/incomplete)
- Menu system with continuous loop (display_menu, main_menu)
- Input validation helpers (get_int_input, get_string_input)
- Task lookup function (find_task by ID)
- Error handling for all user inputs
- Task data model: {id: int, title: str, description: str, completed: bool}
- Status display formatting ([Pending]/[Completed])
- Confirmation prompts for destructive actions (delete)

Not building:
- File persistence (JSON, CSV, pickle) → Phase II requirement
- Database storage (SQLite, PostgreSQL) → Phase II requirement
- Web interface or REST API → Phase II requirement
- User authentication/multi-user support → Phase II requirement
- Advanced features: priorities, tags, categories → Phase III+ requirement
- Search, filter, or sort functionality → Phase III+ requirement
- Due dates, reminders, or notifications → Phase III+ requirement
- Recurring tasks or task dependencies
- Subtasks or nested task hierarchies
- Task sharing or collaboration features
- Undo/redo functionality
- Import/export capabilities"

## User Scenarios & Testing

### User Story 1 - Add and View Tasks (Priority: P1)

As a user, I want to add new tasks with a title and optional description, then view my task list so I can track what I need to do.

**Why this priority**: This is the fundamental core of any task manager. Without the ability to add and view tasks, the application provides no value. This represents the minimum viable product.

**Independent Test**: Can be fully tested by adding tasks with various title lengths (including edge cases) and viewing the displayed list. Delivers value by allowing users to capture and review their tasks.

**Acceptance Scenarios**:

1. **Given** no tasks exist, **When** user adds a task with valid title "Buy groceries" and description "Milk, eggs, bread", **Then** the task is stored with ID 1, and the view option displays it as "[Pending] Buy groceries - Milk, eggs, bread"

2. **Given** three tasks exist with IDs 1-3, **When** user adds another task, **Then** the new task receives ID 4 (auto-increment from highest ID, never reuses deleted IDs)

3. **Given** the user has added tasks, **When** user selects view option, **Then** all tasks are displayed in ID order with status indicators

4. **Given** user attempts to add a task with empty title, **When** input validation runs, **Then** the task is not created and user is prompted to enter a valid title

5. **Given** user attempts to add a task with title exceeding 200 characters, **When** input validation runs, **Then** the task is not created and user is informed of the 200 character limit

---

### User Story 2 - Complete and Uncomplete Tasks (Priority: P1)

As a user, I want to mark tasks as complete and also toggle them back to incomplete so I can track my progress on individual tasks.

**Why this priority**: Task completion tracking is essential for productivity. Users need to see what they've accomplished and potentially revisit completed tasks.

**Independent Test**: Can be fully tested by adding a task, marking it complete, verifying status changes, then toggling it back to pending. Delivers value by giving users a sense of accomplishment and ability to reassess priorities.

**Acceptance Scenarios**:

1. **Given** a pending task exists, **When** user marks it complete, **Then** the task status changes from "[Pending]" to "[Completed]" and a confirmation message displays

2. **Given** a completed task exists, **When** user toggles it to incomplete, **Then** the task status changes from "[Completed]" to "[Pending]" and a confirmation message displays

3. **Given** user enters an invalid task ID when toggling completion, **When** the system searches for the task, **Then** an error message displays and no status change occurs

---

### User Story 3 - Update Task Details (Priority: P2)

As a user, I want to modify the title and description of existing tasks so I can correct mistakes or add more information as my needs change.

**Why this priority**: Task details often need refinement after creation. This enables users to keep their task list accurate and up-to-date without deleting and recreating tasks.

**Independent Test**: Can be fully tested by creating a task, updating its title and/or description, then verifying the changes are reflected in the view. Delivers value by maintaining task accuracy over time.

**Acceptance Scenarios**:

1. **Given** a task with title "Buy milk" exists, **When** user updates the title to "Buy almond milk", **Then** the task title changes and confirmation message displays

2. **Given** a task with no description exists, **When** user adds a description, **Then** the description is stored and displays with the task

3. **Given** user attempts to update a task with an empty title, **When** input validation runs, **Then** the update is cancelled and original title remains

4. **Given** user attempts to update a non-existent task ID, **When** the system searches for the task, **Then** an error message displays

---

### User Story 4 - Delete Tasks (Priority: P2)

As a user, I want to remove tasks that are no longer relevant so I can keep my task list focused on active items.

**Why this priority**: Removing obsolete tasks keeps the list manageable and reduces cognitive load. Combined with confirmation prompts, this prevents accidental deletion while enabling intentional cleanup.

**Independent Test**: Can be fully tested by adding tasks, deleting one with confirmation, then verifying it's removed from view. Delivers value by allowing users to maintain a clean, relevant task list.

**Acceptance Scenarios**:

1. **Given** a task with ID 2 exists among other tasks, **When** user deletes task 2, **Then** the task is removed, IDs 1 and 3 remain unchanged, and confirmation message displays

2. **Given** user attempts to delete a task, **When** confirmation prompt appears and user confirms, **Then** the task is permanently removed from the task list

3. **Given** user attempts to delete a task, **When** confirmation prompt appears and user declines, **Then** the task remains unchanged and operation is cancelled

4. **Given** user attempts to delete a non-existent task ID, **When** the system searches for the task, **Then** an error message displays and no deletion occurs

---

### User Story 5 - Continuous Menu Interaction (Priority: P1)

As a user, I want a persistent menu that allows me to perform any operation repeatedly until I choose to exit, so I can manage my tasks efficiently in a single session.

**Why this priority**: The menu is the primary user interface. Continuous looping enables a natural workflow where users can add, view, update, and complete multiple tasks in one session without restarting the application.

**Independent Test**: Can be fully tested by performing a sequence of operations (add, view, complete, update, delete) in a single session and verifying the menu remains responsive throughout. Delivers value by providing a seamless, intuitive user experience.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** user selects option 6 (Exit), **Then** the application terminates gracefully with a goodbye message

2. **Given** the application is running, **When** user enters an invalid menu option (letters, symbols, numbers outside 1-6), **Then** an error message displays and the menu re-displays without crashing

3. **Given** the application is running, **When** user performs any sequence of valid operations, **Then** each operation completes successfully and the menu remains available

---

### Edge Cases

- What happens when user enters non-numeric input for task ID when a number is expected?
- What happens when user enters a task ID that is out of range (negative, zero, or exceeds highest ID)?
- What happens when the user provides a description exceeding 1000 characters?
- What happens when user enters only whitespace for title?
- What happens when trying to view tasks when none exist?

## Requirements

### Functional Requirements

- **FR-001**: System MUST allow users to add new tasks with a title (1-200 characters, required) and optional description (0-1000 characters)
- **FR-002**: System MUST assign each new task a unique auto-incrementing ID starting from 1, never reusing IDs from deleted tasks
- **FR-003**: System MUST display all tasks in ID order with status indicators ([Pending] or [Completed]) and show title and description when available
- **FR-004**: System MUST allow users to toggle task completion status between pending and completed
- **FR-005**: System MUST allow users to update task title and/or description for existing tasks
- **FR-006**: System MUST require user confirmation before deleting a task
- **FR-007**: System MUST validate all user inputs: non-empty title, title max 200 chars, description max 1000 chars, numeric IDs, valid ID range
- **FR-008**: System MUST display clear, user-friendly error messages for invalid inputs without crashing
- **FR-009**: System MUST display confirmation messages for all successful operations
- **FR-010**: System MUST provide a numbered menu with 6 options and loop continuously until user selects exit

### Key Entities

- **Task**: Represents a single todo item with the following attributes:
  - `id`: Unique positive integer identifier, auto-assigned, never reused
  - `title`: String between 1-200 characters, required
  - `description`: String between 0-1000 characters, optional (empty string when not provided)
  - `completed`: Boolean indicating task status (false for pending, true for completed)

- **Task List**: In-memory collection of Task entities stored as a Python list, lost when application exits

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can complete the full task lifecycle (add → view → update → complete → delete) without any crashes or unhandled exceptions
- **SC-002**: All 5 core operations (add, view, update, delete, toggle complete) work correctly as demonstrated by successful execution of each operation
- **SC-003**: Invalid inputs are handled gracefully with clear error messages and no application crashes (empty titles, non-numeric IDs, invalid menu choices, out-of-range IDs)
- **SC-004**: Task IDs auto-increment from 1 and never reuse deleted IDs, verified by adding tasks, deleting some, adding more, and confirming ID sequence
- **SC-005**: Menu loops continuously until user explicitly exits, verified by performing multiple operations in a single session
- **SC-006**: All operations provide clear confirmation messages (success confirmations, error messages, deletion confirmations)
- **SC-007**: Application runs immediately with no setup required beyond Python 3.13+ interpreter
