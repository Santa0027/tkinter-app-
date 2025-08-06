import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
from PIL import Image, ImageTk
import re

# --- Constants ---

# Use a single file for saved and predefined structures
structure_file = "saved_structures.json"


# --- Helper to handle image paths in PyInstaller bundle ---
def resource_path(relative_path):
    try:
        # PyInstaller stores files in a temp folder in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# --- GUI Code ---
root = tk.Tk()
# logo_path = resource_path("green.jpeg")

# # Load and resize logo safely
# try:
#     logo_img = Image.open(logo_path)
#     logo_img = logo_img.resize((300, 100))
#     logo_photo = ImageTk.PhotoImage(logo_img)
#     logo_label = ttk.Label(root, image=logo_photo)
#     logo_label.image = logo_photo  # Prevent garbage collection
#     logo_label.pack(pady=10)
# except Exception as e:
#     print(f"Could not load logo image: {e}")

root.title("Project Folder Structure Generator")
root.geometry("900x950")

# Top frame for project name and location
top_frame = ttk.LabelFrame(root, text="Project Info", padding=10)
top_frame.pack(pady=10, padx=20, fill=tk.X)

ttk.Label(top_frame, text="Client Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
client_name_entry = ttk.Entry(top_frame, width=40)
client_name_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(top_frame, text="Project Name:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
project_name_entry = ttk.Entry(top_frame, width=40)
project_name_entry.grid(row=1, column=1, padx=5, pady=5)

STATIC_SAVE_LOCATION = r"\\192.168.29.136\EFX_Projects\clients"
save_location_entry = ttk.Entry(top_frame, width=40)
save_location_entry.grid(row=2, column=1, padx=5, pady=5)
save_location_entry.insert(0, STATIC_SAVE_LOCATION)
save_location_entry.config(state='readonly')


# --- Functions for parsing/rendering structure ---
def parse_structure_to_tree(lines):
    tree, stack = [], []
    for line in lines:
        if not line.strip():
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


# --- Main Application Logic ---

# Middle frame for folder structure
structure_frame = ttk.LabelFrame(root, text="Folder Structure", padding=5)
structure_frame.pack(pady=1, padx=1, fill=tk.BOTH, expand=False)

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

# Frame for predefined structure dropdown
predefined_frame = ttk.LabelFrame(root, text="Predefined Structures", padding=10)
predefined_frame.pack(pady=10, padx=20, fill=tk.X)

predefined_structures_data = {}


def load_predefined_structures():
    global predefined_structures_data
    if os.path.exists(structure_file):
        try:
            with open(structure_file, 'r', encoding='utf-8') as f:
                predefined_structures_data = json.load(f)
                return list(predefined_structures_data.keys())
        except (IOError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Could not load saved structures:\n{e}")
            return []
    return []


def load_selected_structure(event=None):
    selected = dropdown.get()
    if selected in predefined_structures_data:
        structure = predefined_structures_data[selected]
        folder_text.delete("1.0", tk.END)
        lines = tree_to_lines(structure)
        folder_text.insert(tk.END, "\n".join(lines))
        extract_folder_names()


ttk.Label(predefined_frame, text="Select a structure:").pack(side=tk.LEFT, padx=5)
dropdown = ttk.Combobox(predefined_frame, state="readonly")
dropdown['values'] = load_predefined_structures()
dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
dropdown.bind("<<ComboboxSelected>>", load_selected_structure)

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


# Utilities for parsing/rendering
def extract_folder_names():
    lines = folder_text.get("1.0", tk.END).splitlines()
    names = []
    for line in lines:
        clean = re.sub(r"\(\d+\)$", "", line.strip())
        if clean and clean not in names and "File Structure ." not in clean:
            names.append(clean)
    folder_dropdown["values"] = sorted(names)


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

    lines = folder_text.get("1.0", tk.END).splitlines()
    tree = parse_structure_to_tree(lines)

    def add_to_tree(node):
        if node["name"] == parent_name:
            for i in range(1, count + 1):
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


# Functions for folder creation and file saving
def create_structure():
    client_name = client_name_entry.get().strip()
    project_name = project_name_entry.get().strip()
    base_dir = save_location_entry.get().strip()

    if not client_name or not project_name or not base_dir:
        messagebox.showerror("Error", "Please fill all fields")
        return

    project_dir = os.path.join(base_dir, client_name, project_name)
    try:
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
    except Exception as e:
        messagebox.showerror("Error", f"Cannot create base project directory: {e}")
        return

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
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create folder '{folder_path}': {e}")
                return False
            if node["children"]:
                if not create_folders(node["children"], folder_path):
                    return False
        return True

    if create_folders(tree, project_dir):
        messagebox.showinfo("Success", f"Project structure created at:\n{project_dir}")


def save_structure():
    lines = folder_text.get("1.0", tk.END).splitlines()
    if not any(line.strip() for line in lines) or folder_text.get("1.0", "1.10").strip() == "File Structure .":
        messagebox.showerror("Error", "Folder structure is empty")
        return

    name = simpledialog.askstring("Save Structure", "Enter a name for the structure:")
    if not name or name.strip() == "":
        return
    name = name.strip()

    structure = parse_structure_to_tree(lines)

    data = {}
    if os.path.exists(structure_file):
        try:
            with open(structure_file, "r") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not read saved structure file: {e}")

    data[name] = structure

    try:
        with open(structure_file, "w") as f:
            json.dump(data, f, indent=4)
        messagebox.showinfo("Saved", f"Folder structure saved as '{name}'")
        dropdown['values'] = load_predefined_structures()  # Refresh dropdown
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save structure: {e}")


def clear_fields():
    client_name_entry.delete(0, tk.END)
    project_name_entry.delete(0, tk.END)
    save_location_entry.config(state='normal')
    save_location_entry.delete(0, tk.END)
    save_location_entry.insert(0, STATIC_SAVE_LOCATION)
    save_location_entry.config(state='readonly')
    folder_text.delete("1.0", tk.END)
    folder_text.insert(tk.END, "File Structure .")
    folder_dropdown["values"] = []


# Add buttons to main window
button_panel = ttk.Frame(root)
button_panel.pack(pady=10)

ttk.Button(button_panel, text="Create Folder Structure", command=create_structure).grid(row=0, column=3, padx=5)
ttk.Button(button_panel, text="Save Structure", command=save_structure).grid(row=0, column=1, padx=5)
# Load Structure is now handled by the dropdown
ttk.Button(button_panel, text="Clear All", command=clear_fields).grid(row=0, column=4, padx=5)


# Function to add a new folder manually
def create_folder():
    lines = folder_text.get("1.0", tk.END).splitlines()
    new_folder = simpledialog.askstring("New Folder", "Enter new folder name:")
    if not new_folder or new_folder.strip() == "":
        return
    new_folder = new_folder.strip()

    if folder_text.get("1.0", "1.10").strip() == "File Structure .":
        folder_text.delete("1.0", tk.END)
        lines = []

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
                continue
            else:
                skip_indent = None
        if line.strip() == selected:
            skip_indent = indent
            continue
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