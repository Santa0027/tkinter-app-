import os
import json
import threading
import time
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

TASKS_FILE = "backup_tasks.json"

class BackupTask:
    def __init__(self, name, source, destination, interval, status="Stopped"):
        self.name = name
        self.source = source
        self.destination = destination
        self.interval = interval
        self.status = status
        self.thread = None
        self.running = False

    def to_dict(self):
        return {
            "name": self.name,
            "source": self.source,
            "destination": self.destination,
            "interval": self.interval,
            "status": self.status
        }

    def start(self):
        if not self.running:
            self.running = True
            self.status = "Running"
            self.thread = threading.Thread(target=self.run_backup, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        self.status = "Stopped"

    def run_backup(self):
        while self.running:
            self.perform_backup()
            time.sleep(self.interval)

    def perform_backup(self):
        for root, dirs, files in os.walk(self.source):
            rel_path = os.path.relpath(root, self.source)
            dest_path = os.path.join(self.destination, rel_path)
            os.makedirs(dest_path, exist_ok=True)

            for file in files:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest_path, file)
                if not os.path.exists(dest_file) or os.path.getmtime(src_file) > os.path.getmtime(dest_file):
                    shutil.copy2(src_file, dest_file)

class BackupSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Backup Scheduler")

        self.tasks = []
        self.load_tasks()

        self.tree = ttk.Treeview(root, columns=("Name", "Source", "Destination", "Interval", "Status"), show='headings')
        for col in ("Name", "Source", "Destination", "Interval", "Status"):
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Task", command=self.add_task).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Edit Task", command=self.edit_task).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete Task", command=self.delete_task).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Start Task", command=self.start_task).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Stop Task", command=self.stop_task).grid(row=0, column=4, padx=5)

        self.refresh_tree()

    def add_task(self):
        self.task_form()

    def edit_task(self):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            task = self.tasks[index]
            self.task_form(task, index)

    def delete_task(self):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            self.tasks[index].stop()
            del self.tasks[index]
            self.save_tasks()
            self.refresh_tree()

    def start_task(self):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            task = self.tasks[index]
            task.start()
            self.refresh_tree()

    def stop_task(self):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            task = self.tasks[index]
            task.stop()
            self.refresh_tree()

    def refresh_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for task in self.tasks:
            self.tree.insert('', tk.END, values=(task.name, task.source, task.destination, f"{task.interval}s", task.status))

    def task_form(self, task=None, index=None):
        form = tk.Toplevel(self.root)
        form.title("Task Form")

        tk.Label(form, text="Task Name").grid(row=0, column=0)
        name_entry = tk.Entry(form)
        name_entry.grid(row=0, column=1)

        tk.Label(form, text="Source Folder").grid(row=1, column=0)
        source_entry = tk.Entry(form)
        source_entry.grid(row=1, column=1)
        tk.Button(form, text="Browse", command=lambda: source_entry.insert(0, filedialog.askdirectory())).grid(row=1, column=2)

        tk.Label(form, text="Destination Folder").grid(row=2, column=0)
        dest_entry = tk.Entry(form)
        dest_entry.grid(row=2, column=1)
        tk.Button(form, text="Browse", command=lambda: dest_entry.insert(0, filedialog.askdirectory())).grid(row=2, column=2)

        tk.Label(form, text="Interval (s)").grid(row=3, column=0)
        interval_entry = tk.Entry(form)
        interval_entry.grid(row=3, column=1)

        if task:
            name_entry.insert(0, task.name)
            source_entry.insert(0, task.source)
            dest_entry.insert(0, task.destination)
            interval_entry.insert(0, str(task.interval))

        def save():
            name = name_entry.get()
            source = source_entry.get()
            destination = dest_entry.get()
            try:
                interval = int(interval_entry.get())
                new_task = BackupTask(name, source, destination, interval)
                if task:
                    self.tasks[index].stop()
                    self.tasks[index] = new_task
                else:
                    self.tasks.append(new_task)
                self.save_tasks()
                self.refresh_tree()
                form.destroy()
            except ValueError:
                messagebox.showerror("Error", "Interval must be an integer")

        tk.Button(form, text="Save", command=save).grid(row=4, column=0, columnspan=2)

    def load_tasks(self):
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r') as f:
                data = json.load(f)
                for item in data:
                    task = BackupTask(**item)
                    self.tasks.append(task)

    def save_tasks(self):
        with open(TASKS_FILE, 'w') as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = BackupSchedulerApp(root)
    root.mainloop()
