#!/usr/bin/env python3
"""
To-Do List (CLI)
-----------------
A simple terminal app to manage your tasks.
Tasks are saved to a file so they persist between sessions.

Run it:
    python todo.py
"""

import json
import os
from datetime import datetime


# ─── File Storage ─────────────────────────────────────────────────────────────

# The file where tasks are saved (created automatically if it doesn't exist)
STORAGE_FILE = "tasks.json"


def load_tasks() -> list:
    """
    Load tasks from the JSON file.
    Returns an empty list if the file doesn't exist yet.
    """
    if not os.path.exists(STORAGE_FILE):
        return []

    with open(STORAGE_FILE, "r") as f:
        return json.load(f)


def save_tasks(tasks: list):
    """
    Save the current list of tasks to the JSON file.
    Overwrites the file every time a change is made.
    """
    with open(STORAGE_FILE, "w") as f:
        json.dump(tasks, f, indent=4)


# ─── Task Operations ──────────────────────────────────────────────────────────

def add_task(tasks: list, title: str):
    """
    Add a new task to the list.
    Each task is a dictionary with an id, title, status, and date added.
    """
    # Generate a unique ID based on the current max ID in the list
    task_id = (max(t["id"] for t in tasks) + 1) if tasks else 1

    # Build the task object
    task = {
        "id":     task_id,
        "title":  title,
        "done":   False,                                      # Not completed yet
        "added":  datetime.now().strftime("%Y-%m-%d %H:%M"), # Timestamp
    }

    tasks.append(task)
    save_tasks(tasks)
    print(f"\n  ✅  Task added: \"{title}\"\n")


def remove_task(tasks: list, task_id: int):
    """
    Remove a task by its ID.
    Prints an error if the ID doesn't exist.
    """
    # Find the task with the matching ID
    task = next((t for t in tasks if t["id"] == task_id), None)

    if not task:
        print(f"\n  ❌  No task found with ID {task_id}.\n")
        return

    tasks.remove(task)
    save_tasks(tasks)
    print(f"\n  🗑️   Removed: \"{task['title']}\"\n")


def mark_done(tasks: list, task_id: int):
    """
    Mark a task as completed by its ID.
    """
    task = next((t for t in tasks if t["id"] == task_id), None)

    if not task:
        print(f"\n  ❌  No task found with ID {task_id}.\n")
        return

    if task["done"]:
        print(f"\n  ℹ️   Task \"{task['title']}\" is already marked as done.\n")
        return

    task["done"] = True
    save_tasks(tasks)
    print(f"\n  ✔️   Marked as done: \"{task['title']}\"\n")


def clear_all(tasks: list):
    """
    Remove all tasks after user confirmation.
    """
    if not tasks:
        print("\n  ℹ️   No tasks to clear.\n")
        return

    confirm = input("  Are you sure you want to clear ALL tasks? (y/n): ").strip().lower()
    if confirm == "y":
        tasks.clear()
        save_tasks(tasks)
        print("\n  🗑️   All tasks cleared.\n")
    else:
        print("\n  Cancelled.\n")


# ─── Display Tasks ────────────────────────────────────────────────────────────

def view_tasks(tasks: list, filter_by: str = "all"):
    """
    Display tasks in the terminal as a formatted list.

    filter_by options:
      "all"     — show every task
      "pending" — show only incomplete tasks
      "done"    — show only completed tasks
    """
    print("\n" + "=" * 50)
    print(f"  📋  TO-DO LIST  ({filter_by.upper()})")
    print("=" * 50)

    if not tasks:
        print("  No tasks yet. Add one!\n")
        return

    # Filter tasks based on the selected view
    if filter_by == "pending":
        filtered = [t for t in tasks if not t["done"]]
    elif filter_by == "done":
        filtered = [t for t in tasks if t["done"]]
    else:
        filtered = tasks

    if not filtered:
        print(f"  No {filter_by} tasks.\n")
        return

    # Print each task
    for task in filtered:
        status = "✔️ " if task["done"] else "⬜"
        title  = task["title"]
        date   = task["added"]
        tid    = task["id"]

        # Strike-through style for completed tasks using brackets
        if task["done"]:
            title = f"[{title}]"

        print(f"  {status}  [{tid}]  {title}  ({date})")

    # Summary count
    done_count    = sum(1 for t in tasks if t["done"])
    pending_count = len(tasks) - done_count
    print("=" * 50)
    print(f"  Total: {len(tasks)}  |  Done: {done_count}  |  Pending: {pending_count}")
    print("=" * 50 + "\n")


# ─── Menu ─────────────────────────────────────────────────────────────────────

def show_menu():
    """Print the main menu options."""
    print("\n  MENU")
    print("  1.  View all tasks")
    print("  2.  View pending tasks")
    print("  3.  View completed tasks")
    print("  4.  Add a task")
    print("  5.  Mark task as done")
    print("  6.  Remove a task")
    print("  7.  Clear all tasks")
    print("  0.  Exit")


def get_task_id(prompt: str) -> int:
    """Prompt the user for a task ID and validate it's a number."""
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("  ⚠️  Please enter a valid task ID (number).\n")


# ─── Main Loop ────────────────────────────────────────────────────────────────

def main():
    # Load existing tasks from file when the app starts
    tasks = load_tasks()

    print("\n" + "=" * 50)
    print("        📝  TO-DO LIST APP (CLI)")
    print("=" * 50)
    print(f"  {len(tasks)} task(s) loaded from storage.")

    while True:
        show_menu()
        choice = input("\n  Choose an option (0-7): ").strip()

        if choice == "0":
            # Exit the app
            print("\n  👋  Goodbye! Your tasks are saved.\n")
            break

        elif choice == "1":
            # View all tasks
            view_tasks(tasks, filter_by="all")

        elif choice == "2":
            # View only pending tasks
            view_tasks(tasks, filter_by="pending")

        elif choice == "3":
            # View only completed tasks
            view_tasks(tasks, filter_by="done")

        elif choice == "4":
            # Add a new task
            title = input("\n  Enter task title: ").strip()
            if title:
                add_task(tasks, title)
            else:
                print("\n  ⚠️  Task title cannot be empty.\n")

        elif choice == "5":
            # Mark a task as done
            view_tasks(tasks, filter_by="pending")
            if any(not t["done"] for t in tasks):
                task_id = get_task_id("  Enter task ID to mark as done: ")
                mark_done(tasks, task_id)

        elif choice == "6":
            # Remove a task
            view_tasks(tasks, filter_by="all")
            if tasks:
                task_id = get_task_id("  Enter task ID to remove: ")
                remove_task(tasks, task_id)

        elif choice == "7":
            # Clear all tasks
            clear_all(tasks)

        else:
            print("\n  ⚠️  Invalid choice. Please enter a number between 0 and 7.\n")


if __name__ == "__main__":
    main()