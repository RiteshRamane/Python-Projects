import json
import os
from datetime import datetime
from enum import Enum


DATA_FILE = "tasks.json"


class Priority(Enum):
    """Enumeration for Task Priority Levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Status(Enum):
    """Enumeration for Task Status Levels."""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    DONE = "Done"


class Task:
    """Represents a single Task in the system."""
    _id_counter = 1 # Static variable to keep track of the next available ID

    def __init__(self, title, description="", priority=Priority.MEDIUM, due_date=None, task_id=None):
        """
        Initializes a new Task object.
        If no task_id is provided, it assigns a new unique ID using the counter.
        """
        self.id = task_id if task_id else Task._id_counter
        if not task_id:
            Task._id_counter += 1
            
        self.title = title
        self.description = description
        # Ensure priority is a Priority Enum object
        self.priority = priority if isinstance(priority, Priority) else Priority(priority)
        self.status = Status.PENDING
        self.due_date = due_date
        # Automatically set the creation timestamp
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    def to_dict(self):
        """Converts the Task object into a dictionary format for JSON storage."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value, 
            "status": self.status.value,    
            "due_date": self.due_date,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a Task object from a dictionary (used when loading from JSON)."""
        task = cls(
            title=data["title"],
            description=data.get("description", ""),
            priority=Priority(data.get("priority", "Medium")),
            due_date=data.get("due_date"),
            task_id=data["id"],
        )
        task.status = Status(data.get("status", "Pending"))
        task.created_at = data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M"))
        return task


class TaskManager:
    """Manages a collection of tasks and handles saving/loading to a file."""
    
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.tasks = []
        self.load() # Load existing tasks immediately upon initialization

    def load(self):
        """Reads tasks from the JSON file and converts them into Task objects."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    # Convert each dictionary in the JSON list back into a Task object
                    self.tasks = [Task.from_dict(t) for t in data]
                    
                    # Update the ID counter so new tasks get unique IDs
                    if self.tasks:
                        Task._id_counter = max(t.id for t in self.tasks) + 1
            except (json.JSONDecodeError, KeyError):
                # If file is corrupted or empty, start with an empty list
                self.tasks = []
        else:
            self.tasks = []

    def save(self):
        """Saves the current list of tasks to the JSON file."""
        with open(self.data_file, "w") as f:
            # Convert all Task objects to dictionaries before saving
            json_data = [t.to_dict() for t in self.tasks]
            json.dump(json_data, f, indent=2)

    def add_task(self, title, description="", priority=Priority.MEDIUM, due_date=None):
        """Creates a new task, adds it to the list, and saves the file."""
        task = Task(title, description, priority, due_date)
        self.tasks.append(task)
        self.save()
        return task

    def delete_task(self, task_id):
        """Removes a task with the matching ID from the list."""
        initial_count = len(self.tasks)
        # Re-create the list excluding the task we want to delete
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self.save()
        # Return True if a task was actually removed
        return len(self.tasks) < initial_count

    def update_status(self, task_id, status: Status):
        """Updates the status of a specific task."""
        for task in self.tasks:
            if task.id == task_id:
                task.status = status
                self.save()
                return True
        return False

    def update_task(self, task_id, title=None, description=None, priority=None, due_date=None):
        """Updates multiple properties of a specific task."""
        for task in self.tasks:
            if task.id == task_id:
                if title:
                    task.title = title
                if description is not None:
                    task.description = description
                if priority:
                    task.priority = priority if isinstance(priority, Priority) else Priority(priority)
                if due_date is not None:
                    task.due_date = due_date
                self.save()
                return True
        return False

    def get_all(self, status_filter=None, priority_filter=None):
        """Returns the list of tasks, optionally filtered by status or priority."""
        filtered_tasks = self.tasks
        if status_filter:
            filtered_tasks = [t for t in filtered_tasks if t.status.value == status_filter]
        if priority_filter:
            filtered_tasks = [t for t in filtered_tasks if t.priority.value == priority_filter]
        return filtered_tasks

    def get_stats(self):
        """Calculates basic statistics about the current tasks."""
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t.status == Status.DONE)
        in_progress = sum(1 for t in self.tasks if t.status == Status.IN_PROGRESS)
        pending = sum(1 for t in self.tasks if t.status == Status.PENDING)
        # Count tasks that are High Priority but not yet completed
        high_priority = sum(1 for t in self.tasks if t.priority == Priority.HIGH and t.status != Status.DONE)
        
        return {
            "total": total,
            "done": done,
            "in_progress": in_progress,
            "pending": pending,
            "high_priority": high_priority,
            "completion_rate": round((done / total * 100) if total else 0, 1),
        }
