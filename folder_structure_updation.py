import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import re

root = tk.Tk()
root.title("Folder Structure Generator")
root.geometry("900x600")

selected_path = tk.StringVar()

# ---------------- UI COMPONENTS ---------------- #

def browse_folder():
    path = filedialog.askdirectory()
    if path:
        selected_path.set(path)
        load_existing_folder_structure(path)

def load_existing_folder_structure(base_path):
    structure_lines = ["File Structure ."]

    def walk_dir(current_path, indent=1):
        try:
            items = sorted(os.listdir(current_path))
            for item in items:
                full_path = os.path.join(current_path, item)
                if os.path.isdir(full_path):
                    structure_lines.append("    " * indent + item)
                    walk_dir(full_path, indent + 1)
        except PermissionError:
            # Skip directories we can't access
            pass

    walk_dir(base_path)
    folder_text.delete("1.0", tk.END)
    folder_text.insert(tk.END, "\n".join(structure_lines))
    extract_folder_names()

browse_frame = ttk.Frame(root)
browse_frame.pack(pady=10)

ttk.Label(browse_frame, text="Select Base Folder:").pack(side=tk.LEFT)
ttk.Entry(browse_frame, textvariable=selected_path, width=60, state='readonly').pack(side=tk.LEFT, padx=5)
ttk.Button(browse_frame, text="Browse", command=browse_folder).pack(side=tk.LEFT)



# Middle frame for folder structure
structure_frame = ttk.LabelFrame(root, text="Folder Structure", padding=5)
structure_frame.pack(pady=1, padx=1, fill=tk.BOTH, expand=True)

# Inner frame to hold both the Text widget and buttons side-by-side
content_frame = tk.Frame(structure_frame)
content_frame.pack(fill=tk.BOTH, expand=True)

# Text widget on the left
folder_text = tk.Text(content_frame, height=20, width=50)
folder_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
folder_text.insert(tk.END, "File Structure .")

def disable_typing(event):
    return "break"

folder_text.bind("<Key>", disable_typing)
folder_text.bind("<Control-v>", disable_typing)
folder_text.bind("<Button-3>", disable_typing)

# Button frame on the right
button_frame = tk.Frame(content_frame)
button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=30)





# Subfolder addition frame
custom_subfolder_frame = ttk.LabelFrame(root, text="Add Subfolders", padding=10)
custom_subfolder_frame.pack(pady=10, padx=20, fill=tk.X)

ttk.Label(custom_subfolder_frame, text="Select Folder:").pack(side=tk.LEFT, padx=5)
folder_dropdown = ttk.Combobox(custom_subfolder_frame, state="readonly")
folder_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

ttk.Label(custom_subfolder_frame, text="Count:").pack(side=tk.LEFT, padx=5)
subfolder_count_entry = ttk.Entry(custom_subfolder_frame, width=5)
subfolder_count_entry.pack(side=tk.LEFT, padx=5)

ttk.Label(custom_subfolder_frame, text="Base Name:").pack(side=tk.LEFT, padx=5)
subfolder_base_entry = ttk.Entry(custom_subfolder_frame, width=15)
subfolder_base_entry.pack(side=tk.LEFT, padx=5)

# ---------------- LOGIC ---------------- #

# Utilities for parsing/rendering
def extract_folder_names():
    lines = folder_text.get("1.0", tk.END).splitlines()
    names = []
    for line in lines:
        clean = re.sub(r"\(\d+\)$", "", line.strip())
        if clean and clean not in names and clean != "File Structure .":
            names.append(clean)
    folder_dropdown["values"] = sorted(names)

def parse_structure_to_tree(lines):
    tree, stack = [], []
    for line in lines:
        if not line.strip() or line.strip() == "File Structure .": 
            continue
        indent = len(line) - len(line.lstrip())
        node = {"name": line.strip(), "children": []}
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if stack:
            stack[-1][1]["children"].append(node)
        else:
            tree.append(node)
        stack.append((indent, node))
    return tree

def tree_to_lines(tree, indent=0):
    lines = []
    for node in tree:
        lines.append(" " * indent + node["name"])
        if node["children"]:
            lines.extend(tree_to_lines(node["children"], indent + 4))
    return lines

def add_subfolders():
    try:
        count = int(subfolder_count_entry.get())
        base_name = subfolder_base_entry.get().strip()
        parent_name = folder_dropdown.get().strip()
        if not parent_name:
            messagebox.showwarning("Warning", "Please select a folder from dropdown")
            return
        if not base_name:
            messagebox.showwarning("Warning", "Base name cannot be empty")
            return
        if count <= 0:
            messagebox.showwarning("Warning", "Count must be a positive integer")
            return
    except Exception as e:
        messagebox.showwarning("Warning", "Please enter valid count")
        return

    # Parse current structure to tree
    lines = folder_text.get("1.0", tk.END).splitlines()
    tree = parse_structure_to_tree(lines)

    def add_to_tree(node):
        if node["name"] == parent_name:
            for i in range(1, count+1):
                new_folder_name = f"{base_name}_{i}"
                node["children"].append({"name": new_folder_name, "children": []})
            return True
        for child in node["children"]:
            if add_to_tree(child):
                return True
        return False

    for node in tree:
        if add_to_tree(node):
            break
    else:
        messagebox.showinfo("Info", f"Parent folder '{parent_name}' not found")
        return

    new_lines = tree_to_lines(tree)
    folder_text.delete("1.0", tk.END)
    folder_text.insert(tk.END, "\n".join(new_lines))
    extract_folder_names()
    subfolder_count_entry.delete(0, tk.END)
    subfolder_base_entry.delete(0, tk.END)

ttk.Button(custom_subfolder_frame, text="Add Subfolders", command=add_subfolders).pack(side=tk.LEFT, padx=5)

# Functions for folder creation
def create_structure():
    base_dir = selected_path.get().strip()
    
    if not base_dir:
        messagebox.showerror("Error", "Please select a base folder first")
        return

    # Build tree from text input
    lines = folder_text.get("1.0", tk.END).splitlines()
    if not any(line.strip() for line in lines):
        messagebox.showerror("Error", "Folder structure is empty")
        return

    tree = parse_structure_to_tree(lines)

    def create_folders(nodes, current_path):
        for node in nodes:
            folder_name = node["name"].strip()
            if folder_name == "":
                continue
            folder_path = os.path.join(current_path, folder_name)
            try:
                # Only create if it doesn't already exist
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create folder '{folder_path}': {e}")
                return False
            if node["children"]:
                if not create_folders(node["children"], folder_path):
                    return False
        return True

    if create_folders(tree, base_dir):
        messagebox.showinfo("Success", f"Folder structure created under:\n{base_dir}")

def clear_fields():
    folder_text.delete("1.0", tk.END)
    folder_text.insert(tk.END, "File Structure .")
    folder_dropdown["values"] = []
    selected_path.set("")

# Add buttons to main window
button_panel = ttk.Frame(root)
button_panel.pack(pady=10)

ttk.Button(button_panel, text="Create Folder Structure", command=create_structure).grid(row=0, column=0, padx=5)
ttk.Button(button_panel, text="Clear All", command=clear_fields).grid(row=0, column=1, padx=5)

# Function to add a new folder manually
def create_folder():
    lines = folder_text.get("1.0", tk.END).splitlines()
    new_folder = simpledialog.askstring("New Folder", "Enter new folder name:")
    if not new_folder or new_folder.strip() == "":
        return
    new_folder = new_folder.strip()

    # Add at root level for simplicity
    lines.append(new_folder)
    folder_text.delete("1.0", tk.END)
    folder_text.insert(tk.END, "\n".join(lines))
    extract_folder_names()

ttk.Button(button_frame, text="Add Folder", command=create_folder, width=20).pack(pady=5)

# Rename selected folder
def rename_folder():
    selected = folder_dropdown.get().strip()
    if not selected:
        messagebox.showwarning("Warning", "Please select a folder to rename")
        return

    new_name = simpledialog.askstring("Rename Folder", f"Enter new name for '{selected}':")
    if not new_name or new_name.strip() == "":
        return
    new_name = new_name.strip()

    lines = folder_text.get("1.0", tk.END).splitlines()
    updated_lines = []
    for line in lines:
        indent = len(line) - len(line.lstrip())
        if line.strip() == selected:
            updated_lines.append(" " * indent + new_name)
        else:
            updated_lines.append(line)
    folder_text.delete("1.0", tk.END)
    folder_text.insert(tk.END, "\n".join(updated_lines))
    extract_folder_names()

# Delete selected folder
def delete_folder():
    selected = folder_dropdown.get().strip()
    if not selected:
        messagebox.showwarning("Warning", "Please select a folder to delete")
        return

    lines = folder_text.get("1.0", tk.END).splitlines()
    new_lines = []
    skip_indent = None
    for line in lines:
        indent = len(line) - len(line.lstrip())
        if skip_indent is not None:
            if indent > skip_indent:
                continue  # Skip child lines
            else:
                skip_indent = None
        if line.strip() == selected:
            skip_indent = indent  # Mark indent to skip children
            continue  # Skip the line itself
        new_lines.append(line)

    folder_text.delete("1.0", tk.END)
    folder_text.insert(tk.END, "\n".join(new_lines))
    extract_folder_names()

# Move selected folder up
def move_up():
    selected = folder_dropdown.get().strip()
    if not selected:
        messagebox.showwarning("Warning", "Please select a folder to move")
        return

    lines = folder_text.get("1.0", tk.END).splitlines()
    for i in range(1, len(lines)):
        curr = lines[i]
        prev = lines[i - 1]
        if curr.strip() == selected:
            curr_indent = len(curr) - len(curr.lstrip())
            prev_indent = len(prev) - len(prev.lstrip())
            if curr_indent == prev_indent:
                lines[i - 1], lines[i] = lines[i], lines[i - 1]
                folder_text.delete("1.0", tk.END)
                folder_text.insert(tk.END, "\n".join(lines))
                extract_folder_names()
                return
    messagebox.showinfo("Info", "Cannot move up")

# Move selected folder down
def move_down():
    selected = folder_dropdown.get().strip()
    if not selected:
        messagebox.showwarning("Warning", "Please select a folder to move")
        return

    lines = folder_text.get("1.0", tk.END).splitlines()
    for i in range(len(lines) - 1):
        curr = lines[i]
        nxt = lines[i + 1]
        if curr.strip() == selected:
            curr_indent = len(curr) - len(curr.lstrip())
            nxt_indent = len(nxt) - len(nxt.lstrip())
            if curr_indent == nxt_indent:
                lines[i], lines[i + 1] = lines[i + 1], lines[i]
                folder_text.delete("1.0", tk.END)
                folder_text.insert(tk.END, "\n".join(lines))
                extract_folder_names()
                return
    messagebox.showinfo("Info", "Cannot move down")

ttk.Button(button_frame, text="Rename Folder", command=rename_folder, width=20).pack(pady=8)
ttk.Button(button_frame, text="Delete Folder", command=delete_folder, width=20).pack(pady=8)
ttk.Button(button_frame, text="Move Folder Up", command=move_up, width=20).pack(pady=8)
ttk.Button(button_frame, text="Move Folder Down", command=move_down, width=20).pack(pady=8)

# Extract folder names initially (empty at start)
extract_folder_names()

root.mainloop()