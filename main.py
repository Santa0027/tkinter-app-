import tkinter as tk
import subprocess
import os
import sys

from tkinter import ttk, filedialog, messagebox, simpledialog
import json
from PIL import Image, ImageTk
import re
# Functions to launch external Python files
def open_app_one():
    subprocess.Popen(["python", "folder_structure_creation.py"])

def open_app_two():
    subprocess.Popen(["python", "folder_structure_updation.py"])

def open_app_three():
    subprocess.Popen(["python", "backuptool.py"])

# Main application window
root = tk.Tk()
root.title("App Launcher")
root.geometry("500x300")

# --- Helper to handle image paths in PyInstaller bundle ---
def resource_path(relative_path):   
    try:
        # PyInstaller stores files in a temp folder in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


logo_path = resource_path("green.jpeg")
logo_img = Image.open(logo_path)
logo_img = logo_img.resize((300, 100))
logo_photo = ImageTk.PhotoImage(logo_img)
logo_label = ttk.Label(root, image=logo_photo)
logo_label.image = logo_photo  # Prevent garbage collection
logo_label.pack(pady=10)


# App title label
title_label = tk.Label(root, text="Select an App", font=("Helvetica", 14))
title_label.pack(pady=10)

# Buttons for each app
btn1 = tk.Button(root, text="New Structure", width=20, command=open_app_one)
btn1.pack(pady=5)

btn2 = tk.Button(root, text="Open Structure", width=20, command=open_app_two)
btn2.pack(pady=5)

btn3 = tk.Button(root, text="Task scheduler", width=20, command=open_app_three)
btn3.pack(pady=5)

# Run the app
root.mainloop()
