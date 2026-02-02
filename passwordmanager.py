import tkinter as tk
from tkinter import ttk, messagebox
import secrets
import string
from PIL import Image, ImageTk

def resize_background(event):
    """Resize background image when window is resized."""
    global bg_photo, original_image
    try:
        new_width = event.width
        new_height = event.height
        resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(resized_image)
        bg_label.config(image=bg_photo)
        bg_label.image = bg_photo
    except:
        pass

def generate_password():
    """Generate password based on UI selections."""
    try:
        length = int(length_var.get())
        
        if length < 4:
            messagebox.showwarning("Invalid Length", "Password length must be at least 4")
            return
        
        characters = ""
        password = []

        if uppercase_var.get():
            characters += string.ascii_uppercase
            password.append(secrets.choice(string.ascii_uppercase))

        if lowercase_var.get():
            characters += string.ascii_lowercase
            password.append(secrets.choice(string.ascii_lowercase))

        if digits_var.get():
            characters += string.digits
            password.append(secrets.choice(string.digits))

        if symbols_var.get():
            characters += string.punctuation
            password.append(secrets.choice(string.punctuation))

        if not characters:
            messagebox.showwarning("No characters selected", "Please select at least one character type")
            return
        
        for _ in range(length - len(password)):
            password.append(secrets.choice(characters))

        import random
        random.shuffle(password)
        result = ''.join(password)

        password_entry.delete(0, tk.END)
        password_entry.insert(0, result)

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number for length.")

def copy_to_clipboard():
    """Copy generated password to clipboard."""
    password = password_entry.get()
    if password:
        root.clipboard_clear()
        root.clipboard_append(password)
        messagebox.showinfo("Copied", "Password copied to clipboard")

# Main window setup
root = tk.Tk()
root.title("Password Generator")
root.geometry("900x500")
root.minsize(700, 450)

# Set the app icon (works for Windows, Linux, and macOS)
try:
    # Try .ico format first (best for Windows)
    root.iconbitmap("icon.ico")
    print("Loaded .ico icon")
except:
    # Fallback to .png format (cross-platform)
    try:
        icon_image = Image.open("icon.png")
        icon_photo = ImageTk.PhotoImage(icon_image)
        root.iconphoto(True, icon_photo)
        print("Loaded .png icon")
    except Exception as e:
        print(f"Could not load icon: {e}")

# Load background image
try:
    original_image = Image.open("background.png")
    bg_image = original_image.resize((900, 500), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    root.bind('<Configure>', resize_background)
except Exception as e:
    print(f"Could not load background image: {e}")
    root.configure(bg="#7CB68C")

# UI Frame with green-tinted glass effect
main_frame = tk.Frame(root, bg="#E8F4ED", bd=0, relief="flat")
main_frame.place(x=40, y=40, width=380, height=420)

# Subtle border
border_frame = tk.Frame(root, bg="#9DC2A8", bd=0)
border_frame.place(x=38, y=38, width=384, height=424)
main_frame.lift()

# Title
title_label = tk.Label(main_frame, text="🔐 Password Generator", 
                       font=("Arial", 18, "bold"), bg="#E8F4ED", fg="#2D5F3F")
title_label.pack(pady=15)

# Length frame
length_frame = tk.Frame(main_frame, bg="#E8F4ED")
length_frame.pack(pady=10)

tk.Label(length_frame, text="Password Length:", font=("Arial", 11), 
         bg="#E8F4ED", fg="#2D5F3F").pack(side=tk.LEFT, padx=5)
length_var = tk.StringVar(value="16")
length_spinbox = tk.Spinbox(length_frame, from_=4, to=128, textvariable=length_var, 
                            width=10, font=("Arial", 11), relief="flat", bd=1,
                            bg="#F5FAF7", fg="#2D5F3F")
length_spinbox.pack(side=tk.LEFT)

# Character options with green theme
options_frame = tk.LabelFrame(main_frame, text="Character Types", 
                              font=("Arial", 11, "bold"), padx=20, pady=10, 
                              bg="#E8F4ED", fg="#2D5F3F", relief="flat", bd=1,
                              highlightbackground="#9DC2A8", highlightthickness=1)
options_frame.pack(pady=10, padx=20, fill="x")

uppercase_var = tk.BooleanVar(value=True)
lowercase_var = tk.BooleanVar(value=True)
digits_var = tk.BooleanVar(value=True)
symbols_var = tk.BooleanVar(value=True)

tk.Checkbutton(options_frame, text="Uppercase (A-Z)", variable=uppercase_var, 
               font=("Arial", 10), bg="#E8F4ED", fg="#2D5F3F", 
               activebackground="#E8F4ED", selectcolor="#C8E6D4").pack(anchor="w", pady=2)
tk.Checkbutton(options_frame, text="Lowercase (a-z)", variable=lowercase_var, 
               font=("Arial", 10), bg="#E8F4ED", fg="#2D5F3F", 
               activebackground="#E8F4ED", selectcolor="#C8E6D4").pack(anchor="w", pady=2)
tk.Checkbutton(options_frame, text="Digits (0-9)", variable=digits_var, 
               font=("Arial", 10), bg="#E8F4ED", fg="#2D5F3F", 
               activebackground="#E8F4ED", selectcolor="#C8E6D4").pack(anchor="w", pady=2)
tk.Checkbutton(options_frame, text="Symbols (@#!€$...)", variable=symbols_var, 
               font=("Arial", 10), bg="#E8F4ED", fg="#2D5F3F", 
               activebackground="#E8F4ED", selectcolor="#C8E6D4").pack(anchor="w", pady=2)

# Generate button with ORANGE color
generate_btn = tk.Button(main_frame, text="Generate Password", command=generate_password,
                         bg="#FF8C42", fg="white", font=("Arial", 12, "bold"),
                         padx=20, pady=8, cursor="hand2", activebackground="#FF7A29",
                         relief="flat", bd=0)
generate_btn.pack(pady=15)

# Password field
result_frame = tk.Frame(main_frame, bg="#E8F4ED")
result_frame.pack(pady=5, padx=20, fill="x")

password_entry = tk.Entry(result_frame, font=("Courier", 11), justify="center",
                         bg="#F5FAF7", fg="#2D5F3F", relief="flat", bd=1, 
                         highlightthickness=1, highlightbackground="#9DC2A8",
                         highlightcolor="#FF8C42")
password_entry.pack(side=tk.LEFT, padx=5, fill="x", expand=True, ipady=4)

copy_btn = tk.Button(result_frame, text="📋 Copy", command=copy_to_clipboard,
                     bg="#5FA877", fg="white", font=("Arial", 10), cursor="hand2",
                     activebackground="#4E8A62", relief="flat", bd=0, padx=10, pady=4)
copy_btn.pack(side=tk.LEFT)

root.mainloop()