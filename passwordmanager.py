import tkinter as tk
from tkinter import ttk, messagebox
import secrets
import string

def generate_password():
    """Generate password based on UI selections."""
    try:
        length = int(length_var.get())
        if length < 4:
            messagebox.showwarning("Invalid Lenght", "Password length must be at least 8")
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
        
        # Rellenar los espacios restantes / Fill the remaining spaces
        for _ in range(length - len(password)):
            password.append(secrets.choice(characters))

        secrets.SystemRandom().shuffle(password)
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

# Configuración de la ventana principal / Main window setup
root = tk.Tk()
root.title("Password Generator")
root.geometry("450x350")
root.resizable(False, False)

# Titulo / Title
title_label = tk.Label(root, text="🔐 Password Generator", font=("Arial", 18, "bold"))
title_label.pack(pady=15)

# Longitud del frame / Length frame
length_frame = tk.Frame(root)
length_frame.pack(pady=10)

tk.Label(length_frame, text="Password Length:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
length_var = tk.StringVar(value="16")
length_spinbox = tk.Spinbox(length_frame, from_=4, to=128, textvariable=length_var, width=10, font=("Arial", 11))
length_spinbox.pack(side=tk.LEFT)

# Opciones de caracteres / Character options
options_frame = tk.LabelFrame(root, text="Character Types", font=("Arial", 11, "bold"), padx=20, pady=10)
options_frame.pack(pady=10, padx=20, fill="x")

uppercase_var = tk.BooleanVar(value=True)
lowercase_var = tk.BooleanVar(value=True)
digits_var = tk.BooleanVar(value=True)
symbols_var = tk.BooleanVar(value=True)

tk.Checkbutton(options_frame, text="Uppercase (A-Z)", variable=uppercase_var, font=("Arial", 10)).pack(anchor="w")
tk.Checkbutton(options_frame, text="Lowercase (a-z)", variable=lowercase_var, font=("Arial", 10)).pack(anchor="w")
tk.Checkbutton(options_frame, text="Digits (0-9)", variable=digits_var, font=("Arial", 10)).pack(anchor="w")
tk.Checkbutton(options_frame, text="Symbols (@#!€$...)", variable=symbols_var, font=("Arial", 10)).pack(anchor="w")

# Boton de generation / Generate button
generate_btn = tk.Button(root, text="Generate Password", command=generate_password,
                         bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                         padx=20, pady=5, cursor="hand2")
generate_btn.pack(pady=15)

# Campo de contraseña / Password field
result_frame = tk.Frame(root)
result_frame.pack(pady=5, padx=20, fill="x")

password_entry = tk.Entry(result_frame, font=("Courier", 12), justify="center", width=30)
password_entry.pack(side=tk.LEFT, padx=5, fill="x", expand=True)

copy_btn = tk.Button(result_frame, text="📋 Copy", command=copy_to_clipboard,
                     bg="#2196F3", fg="white", font=("Arial", 10), cursor="hand2")
copy_btn.pack(side=tk.LEFT)

# Iniciar la aplicación / Start the application
root.mainloop()