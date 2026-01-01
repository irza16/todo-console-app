# Implementation Tasks: Todo Console App - Phase I

**Feature Branch**: `001-todo-console-app`
**Created**: 2025-12-07
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Data Model**: [data-model.md](data-model.md)
**Quickstart**: [quickstart.md](quickstart.md)

## Summary

This file contains all implementation tasks for the Todo Console App, organized by user story to enable independent implementation and testing. The MVP consists of User Story 1 (Add and View Tasks) combined with the menu infrastructure from User Story 5.

## Dependencies

### Story Completion Order

```
Phase 1: Setup (no dependencies)
    |
    v
Phase 2: Foundational (depends on Setup)
    |
    +--> User Story 5 (Menu) [Foundation for all other stories]
    |
    +--> User Story 1 (Add + View) [Depends on Menu]
    |
    +--> User Story 2 (Complete) [Depends on Menu + US1 for testing]
    |
    +--> User Story 3 (Update) [Depends on Menu + US1]
    |
    +--> User Story 4 (Delete) [Depends on Menu + US1]
    |
    v
Phase 7: Polish (depends on all User Stories complete)
```

### Parallel Execution Opportunities

- **US2, US3, US4 can be implemented in parallel** after US1 and Menu are complete
- Each operates on different functions with no shared state dependencies
- All three use the same `find_task()` helper

## Implementation Strategy

### MVP Scope (Phase 1 + Menu + US1)

The minimum viable product requires:
- Phase 1: Setup
- Phase 2: Foundational (globals, constants, helpers)
- Phase 3: User Story 5 (Menu infrastructure)
- Phase 4: User Story 1 (Add + View operations)

This delivers a working todo app where users can add and view tasks.

### Incremental Delivery

After MVP, add features in priority order:
1. User Story 2 (Complete) - Adds progress tracking
2. User Story 3 (Update) - Adds modification capability
3. User Story 4 (Delete) - Adds cleanup capability
4. Phase 7 (Polish) - Error handling and edge cases

---

## Phase 1: Setup

**Goal**: Initialize project structure and verify Python environment

**Independent Test**: Verify `src/` directory exists and Python 3.13+ is available

### Tasks

- [x] T001 Create src directory at repository root
- [x] T002 Verify Python 3.13+ is available (run `python --version`)

---

## Phase 2: Foundational

**Goal**: Establish global state, constants, and helper functions needed by all operations

**Independent Test**: Functions can be called with test inputs and return expected outputs

### Constants

- [x] T003 Define MAX_TITLE_LENGTH = 200 constant in src/main.py
- [x] T004 Define MAX_DESCRIPTION_LENGTH = 1000 constant in src/main.py
- [x] T005 Define MIN_ID = 1 constant in src/main.py
- [x] T006 Define MENU_OPTIONS = 6 constant in src/main.py

### Global State

- [x] T007 Create global `tasks = []` list in src/main.py
- [x] T008 Create global `next_id = 1` counter in src/main.py

### Helper Functions

- [x] T009 Implement `get_string_input(prompt, min_len=1, max_len=None)` in src/main.py
  - Prompts user with given prompt
  - Validates string length constraints
  - Returns validated string
  - Includes docstring

- [x] T010 Implement `get_int_input(prompt, min_val=None, max_val=None)` in src/main.py
  - Prompts user with given prompt
  - Validates input is numeric integer
  - Validates min/max constraints if provided
  - Returns validated integer
  - Includes docstring

- [x] T011 Implement `find_task(task_id)` in src/main.py
  - Searches tasks list for task with matching ID
  - Returns task dict if found, None if not found
  - Returns None for non-numeric or invalid IDs
  - Includes docstring

- [x] T012 Implement `format_status(completed)` in src/main.py
  - Returns "[Completed]" if completed=True
  - Returns "[Pending]" if completed=False
  - Includes docstring

---

## Phase 3: User Story 5 - Menu System (Foundation)

**Goal**: Create the menu infrastructure that enables all other user stories

**User Story**: As a user, I want a persistent menu that allows me to perform any operation repeatedly until I choose to exit

**Independent Test**: Menu displays, accepts input, loops properly, exits cleanly on option 6

### Menu Functions

- [x] T013 [US5] Implement `display_menu()` function in src/main.py
  - Prints menu header "=== Todo Console App ==="
  - Prints numbered options 1-6 (Add Task, View Tasks, Update Task, Delete Task, Toggle Complete, Exit)
  - Prints "Enter your choice (1-6):" prompt
  - Includes docstring

- [x] T014 [US5] Implement `main_menu()` loop function in src/main.py
  - Calls display_menu() to show options
  - Gets user choice using get_int_input(1, 6)
  - Dispatches to appropriate operation function based on choice
  - Loops continuously until choice == 6
  - Returns None on exit
  - Handles invalid choices gracefully (error message, re-display menu)
  - Includes docstring

- [x] T015 [US5] Implement `main()` entry point in src/main.py
  - Calls main_menu() to start the application
  - Prints goodbye message on exit
  - Uses `if __name__ == "__main__":` guard
  - Includes docstring

---

## Phase 4: User Story 1 - Add and View Tasks

**Goal**: Implement core task creation and display functionality

**User Story**: As a user, I want to add new tasks with a title and optional description, then view my task list

**Independent Test**: Can add tasks and view them displayed correctly with status indicators

### Add Task Operation

- [x] T016 [US1] Implement `add_task()` operation function in src/main.py
  - Gets task title using get_string_input("Enter task title: ", 1, 200)
  - Gets optional description using get_string_input("Enter task description (optional): ", 0, 1000)
  - Creates task dict with id=next_id, title, description, completed=False
  - Appends task to tasks list
  - Increments next_id counter
  - Prints confirmation: "Task added successfully! (ID: {id})"
  - Includes docstring

### View Tasks Operation

- [x] T017 [US1] Implement `view_tasks()` operation function in src/main.py
  - Prints header "=== Your Tasks ==="
  - If tasks list is empty: prints "No tasks yet. Add some tasks!"
  - If tasks exist: iterates through tasks in ID order
    - Prints each task: "[Status] {id}. {title} - {description}"
    - Shows "[Pending]" or "[Completed]" via format_status()
  - Prints "Total: {count} task(s)"
  - Includes docstring

### User Story 1 Validation

- [x] T018 [US1] Test add_task() with valid title and description
- [x] T019 [US1] Test add_task() with valid title, empty description
- [x] T020 [US1] Test add_task() with empty title (should reject)
- [x] T021 [US1] Test add_task() with title > 200 chars (should reject)
- [x] T022 [US1] Test view_tasks() with empty list
- [x] T023 [US1] Test view_tasks() with single task
- [x] T024 [US1] Test view_tasks() with multiple tasks (verify ID ordering)

---

## Phase 5: User Story 2 - Complete and Uncomplete Tasks

**Goal**: Implement task status toggling functionality

**User Story**: As a user, I want to mark tasks as complete and also toggle them back to incomplete

**Independent Test**: Can toggle task status in both directions, see status change in view

### Toggle Complete Operation

- [x] T025 [US2] Implement `toggle_complete()` operation function in src/main.py
  - Gets task ID using get_int_input("Enter task ID: ")
  - Uses find_task() to locate task
  - If task not found: prints error "Task with ID {id} not found."
  - If task found: toggles completed boolean
  - Prints confirmation: "Task {id} marked as [Completed/Pending]!"
  - Includes docstring

### User Story 2 Validation

- [x] T026 [US2] Test toggle_complete() on pending task (becomes completed)
- [x] T027 [US2] Test toggle_complete() on completed task (becomes pending)
- [x] T028 [US2] Test toggle_complete() with invalid ID (shows error)
- [x] T029 [US2] Test toggle_complete() with non-numeric input (shows error)
- [x] T030 [US2] Verify status change appears in view_tasks() output

---

## Phase 6: User Story 3 - Update Task Details

**Goal**: Implement task modification functionality

**User Story**: As a user, I want to modify the title and description of existing tasks

**Independent Test**: Can update task title and/or description, changes appear in view

### Update Task Operation

- [x] T031 [US3] Implement `update_task()` operation function in src/main.py
  - Gets task ID using get_int_input("Enter task ID: ")
  - Uses find_task() to locate task
  - If task not found: prints error "Task with ID {id} not found."
  - If task found:
    - Shows current task details
    - Gets new title using get_string_input("Enter new title (press Enter to keep current): ", 0, 200)
    - Gets new description using get_string_input("Enter new description (press Enter to keep current): ", 0, 1000)
    - If user presses Enter (empty string), keeps current value
    - Updates task dict with new values (if provided)
    - Prints confirmation: "Task {id} updated successfully!"
  - Includes docstring

### User Story 3 Validation

- [x] T032 [US3] Test update_task() with new title only
- [x] T033 [US3] Test update_task() with new description only
- [x] T034 [US3] Test update_task() with both title and description
- [x] T035 [US3] Test update_task() keeping current values (Enter key)
- [x] T036 [US3] Test update_task() with empty title (should reject/cancel)
- [x] T037 [US3] Test update_task() with invalid ID (shows error)
- [x] T038 [US3] Verify changes appear in view_tasks() output

---

## Phase 7: User Story 4 - Delete Tasks

**Goal**: Implement task removal with confirmation

**User Story**: As a user, I want to remove tasks that are no longer relevant

**Independent Test**: Can delete tasks with confirmation, deleted task no longer appears in view

### Delete Task Operation

- [x] T039 [US4] Implement `delete_task()` operation function in src/main.py
  - Gets task ID using get_int_input("Enter task ID: ")
  - Uses find_task() to locate task
  - If task not found: prints error "Task with ID {id} not found."
  - If task found:
    - Shows task details to be deleted
    - Prompts for confirmation: "Are you sure you want to delete this task? (y/n): "
    - Gets confirmation using input() (accept y/Y or n/N)
    - If confirmed (y/Y): removes task from tasks list, prints "Task {id} deleted successfully!"
    - If not confirmed: prints "Task deletion cancelled."
  - Includes docstring

### User Story 4 Validation

- [x] T040 [US4] Test delete_task() with confirmation (y)
- [x] T041 [US4] Test delete_task() with confirmation decline (n)
- [x] T042 [US4] Test delete_task() with invalid ID (shows error)
- [x] T043 [US4] Test delete_task() with non-numeric input (shows error)
- [x] T044 [US4] Verify deleted task no longer appears in view_tasks()
- [x] T045 [US4] Verify remaining tasks keep their IDs (no renumbering)

---

## Phase 8: Polish and Cross-Cutting Concerns

**Goal**: Ensure all edge cases are handled and code quality meets standards

**Independent Test**: All success criteria from specification are met

### Error Handling

- [x] T046 Handle non-numeric input for menu choice (letters, symbols)
- [x] T047 Handle menu choice outside 1-6 range (0, 7, negative, large numbers)
- [x] T048 Handle whitespace-only title input (should reject)
- [x] T049 Handle description exceeding 1000 characters (should reject)
- [x] T050 Handle task operations on empty list gracefully
- [x] T051 Handle edge case IDs (0, negative, very large numbers)

### Code Quality

- [x] T052 Ensure all functions have proper docstrings
- [x] T053 Ensure all variable names follow snake_case convention
- [x] T054 Ensure all constant names follow UPPER_CASE convention
- [x] T055 Ensure consistent formatting throughout src/main.py
- [x] T056 Add inline comments for complex logic

### User Experience

- [x] T057 Verify all confirmation messages are clear and user-friendly
- [x] T058 Verify all error messages are actionable
- [x] T059 Verify consistent use of separators (===, ---) in output
- [x] T060 Verify empty description handling (doesn't show trailing "-")

---

## Task Summary

| Category | Count |
|----------|-------|
| Phase 1: Setup | 2 |
| Phase 2: Foundational | 9 |
| Phase 3: User Story 5 (Menu) | 3 |
| Phase 4: User Story 1 (Add + View) | 9 |
| Phase 5: User Story 2 (Complete) | 6 |
| Phase 6: User Story 3 (Update) | 8 |
| Phase 7: User Story 4 (Delete) | 7 |
| Phase 8: Polish | 15 |
| **Total Tasks** | **60** |
| **Completed** | **60** |
| **Remaining** | **0** |

### Task Count by User Story

| User Story | Tasks | Priority | Status |
|------------|-------|----------|--------|
| US1: Add + View Tasks | T016-T024 | P1 | COMPLETE |
| US2: Complete Tasks | T025-T030 | P1 | COMPLETE |
| US3: Update Tasks | T031-T038 | P2 | COMPLETE |
| US4: Delete Tasks | T039-T045 | P2 | COMPLETE |
| US5: Menu System | T013-T015 | P1 (Foundation) | COMPLETE |

### Implementation Complete

All 60 tasks have been completed. The application is ready for testing.

---

## Verification Checklist

Before considering implementation complete, verify:

- [x] Application runs with `python src/main.py`
- [x] Menu displays and loops until option 6 is selected
- [x] Can add tasks with valid title and optional description
- [x] View displays all tasks in ID order with status indicators
- [x] Can mark tasks complete and toggle them back to pending
- [x] Can update task title and/or description
- [x] Can delete tasks with confirmation
- [x] All invalid inputs handled gracefully (no crashes)
- [x] Task IDs auto-increment and never reuse deleted IDs
- [x] All operations provide clear confirmation messages
- [x] All functions have docstrings
- [x] Code follows snake_case naming convention
