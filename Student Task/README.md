# Task Management System

A comprehensive Python-based task management project featuring both a command-line interface (CLI) and a web-based dashboard.

---

## File Structure

| File | Description |
|------|-------------|
| `todo.py` | Core library containing the Task and TaskManager classes. |
| `main.py` | Command-line interface for managing tasks. |
| `dashboard.html` | Web-based interface for visual task management. |
| `tasks.json` | Data storage file for CLI tasks (automatically generated). |

---

## Instructions for Use

### 1. Web Dashboard
Open `dashboard.html` in any modern web browser.
- No installation or server required.
- Data is stored locally in the browser's persistent storage.
- Manage tasks visually with the intuitive interface.

### 2. Command-Line Interface (CLI)
Run the following command in your terminal:
```bash
python main.py
```
- Use the menu-driven system to manage tasks.
- Data is saved to the local `tasks.json` file.

---

## Key Features

### Web Dashboard
- Real-time statistics: Total tasks, Completed, In Progress, and High Priority.
- Visual completion progress indicator.
- Professional and clean user interface design.
- Filtering options based on task status or priority.
- Full task management capabilities (Add, Edit, Delete).
- Status toggling and deadline highlighting.

### Command-Line Interface
- Formatted task display with priority and status indicators.
- Comprehensive task creation: Title, Description, Priority, and Due Date.
- Dynamic status updates.
- Task modification and deletion with confirmation prompts.
- Detailed statistical summaries.
- Advanced filtering by status or priority.

---

## Technical Requirements
- Python 3.8 or higher (required for CLI operations).
- No external Python libraries required (uses standard library only).
- A modern web browser for the dashboard interface.
