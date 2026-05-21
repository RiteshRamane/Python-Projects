from todo import TaskManager, Priority, Status


def print_banner():
    """Prints the application banner."""
    print("\n" + "=" * 50)
    print("             TASK MANAGEMENT SYSTEM")
    print("=" * 50)


def print_menu():
    """Prints the main menu options."""
    print("\nMAIN MENU:")
    print("  1. View All Tasks")
    print("  2. Add New Task")
    print("  3. Update Task Status")
    print("  4. Edit Existing Task")
    print("  5. Delete Task")
    print("  6. View Task Statistics")
    print("  7. Filter Tasks")
    print("  0. Exit")
    print("-" * 30)


def priority_badge(p):
    """Returns a professional label for the priority levels."""
    badges = {"High": "[High]", "Medium": "[Medium]", "Low": "[Low]"}
    return badges.get(p, p)


def status_badge(s):
    """Returns a professional label for the task status."""
    badges = {"Pending": "[Pending]", "In Progress": "[In Progress]", "Done": "[Completed]"}
    return badges.get(s, s)


def print_tasks(tasks):
    """Prints a formatted list of tasks."""
    if not tasks:
        print("\n  No tasks available.")
        return
    # Column headers
    print(f"\n{'ID':<5} {'Title':<28} {'Priority':<15} {'Status':<18} {'Due Date'}")
    print("-" * 80)
    for t in tasks:
        due = t.due_date or "---"
        print(f"{t.id:<5} {t.title[:27]:<28} {priority_badge(t.priority.value):<15} {status_badge(t.status.value):<18} {due}")
        if t.description:
            print(f"      Description: {t.description[:70]}")


def get_priority_input():
    """Prompts the user to select a priority level."""
    print("  Select Priority: 1) High  2) Medium  3) Low")
    choice = input("  Enter choice [1-3, default=2]: ").strip()
    return {1: Priority.HIGH, 3: Priority.LOW}.get(int(choice) if choice.isdigit() else 2, Priority.MEDIUM)


def get_status_input():
    """Prompts the user to select a task status."""
    print("  Select Status: 1) Pending  2) In Progress  3) Done")
    choice = input("  Enter choice [1-3]: ").strip()
    return {1: Status.PENDING, 2: Status.IN_PROGRESS, 3: Status.DONE}.get(int(choice) if choice.isdigit() else 1, Status.PENDING)


def main():
    """Main execution loop for the task manager."""
    manager = TaskManager()
    print_banner()
    print("  Welcome. Use the menu below to manage your tasks efficiently.")

    while True:
        print_menu()
        choice = input("Enter option number: ").strip()

        if choice == "1":
            tasks = manager.get_all()
            print(f"\nListing All Tasks ({len(tasks)} total):")
            print_tasks(tasks)

        elif choice == "2":
            print("\nADD NEW TASK")
            title = input("  Enter Task Title: ").strip()
            if not title:
                print("  Error: Title cannot be empty.")
                continue
            desc = input("  Enter Description (optional): ").strip()
            priority = get_priority_input()
            due = input("  Enter Due Date (YYYY-MM-DD, optional): ").strip() or None
            task = manager.add_task(title, desc, priority, due)
            print(f"  Success: Task #{task.id} '{task.title}' has been added.")

        elif choice == "3":
            print("\nUPDATE TASK STATUS")
            tasks = manager.get_all()
            print_tasks(tasks)
            try:
                tid = int(input("  Enter Task ID to update: ").strip())
                status = get_status_input()
                if manager.update_status(tid, status):
                    print(f"  Success: Status updated to '{status.value}'")
                else:
                    print("  Error: Task ID not found.")
            except ValueError:
                print("  Error: Invalid Task ID entered.")

        elif choice == "4":
            print("\nEDIT TASK DETAILS")
            tasks = manager.get_all()
            print_tasks(tasks)
            try:
                tid = int(input("  Enter Task ID to edit: ").strip())
                title = input("  Enter New Title (leave blank to keep current): ").strip() or None
                desc = input("  Enter New Description (leave blank to keep current): ").strip()
                priority_input = input("  Change Priority? (y/n): ").strip().lower()
                priority = get_priority_input() if priority_input == "y" else None
                due = input("  Enter New Due Date (YYYY-MM-DD, blank=keep, 'clear'=remove): ").strip()
                due = None if due == "" else ("" if due == "clear" else due)
                
                if manager.update_task(tid, title, desc if desc else None, priority, due):
                    print("  Success: Task details updated.")
                else:
                    print("  Error: Task ID not found.")
            except ValueError:
                print("  Error: Invalid Task ID entered.")

        elif choice == "5":
            print("\nDELETE TASK")
            tasks = manager.get_all()
            print_tasks(tasks)
            try:
                tid = int(input("  Enter Task ID to delete: ").strip())
                confirm = input(f"  Confirm deletion of Task #{tid}? (y/n): ").strip().lower()
                if confirm == "y":
                    if manager.delete_task(tid):
                        print("  Success: Task has been deleted.")
                    else:
                        print("  Error: Task ID not found.")
            except ValueError:
                print("  Error: Invalid Task ID entered.")

        elif choice == "6":
            stats = manager.get_stats()
            print("\nTASK STATISTICS SUMMARY")
            print(f"  Total Registered Tasks : {stats['total']}")
            print(f"  Completed Tasks        : {stats['done']}")
            print(f"  Tasks In Progress      : {stats['in_progress']}")
            print(f"  Pending Tasks          : {stats['pending']}")
            print(f"  High Priority Tasks    : {stats['high_priority']} (remaining)")
            print(f"  Completion Rate        : {stats['completion_rate']}%")

        elif choice == "7":
            print("\nFILTER TASKS")
            print("  Filter by: 1) Status  2) Priority  3) Both")
            f_choice = input("  Select filter option [1-3]: ").strip()
            status_f = priority_f = None
            if f_choice in ("1", "3"):
                status_f = get_status_input().value
            if f_choice in ("2", "3"):
                priority_f = get_priority_input().value
            tasks = manager.get_all(status_f, priority_f)
            print(f"\n  Search Results: {len(tasks)} task(s) found.")
            print_tasks(tasks)

        elif choice == "0":
            print("\nThank you for using the Task Management System. Goodbye.\n")
            break

        else:
            print("  Error: Invalid option. Please try again.")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
