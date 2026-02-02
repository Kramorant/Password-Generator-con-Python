import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import secrets
import string
from PIL import Image, ImageTk
from datetime import datetime
import json
import os
import sys
from cryptography.fernet import Fernet

# Global list to store password history
password_history = []

# Encryption setup
KEY_FILE = "password_vault.key"
VAULT_FILE = "password_vault.encrypted"

# ADD THIS FUNCTION - Critical for executable to find images!
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_or_create_key():
    """Get encryption key or create new one."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
        return key

def load_saved_passwords():
    """Load and decrypt saved passwords from vault."""
    try:
        key = get_or_create_key()
        cipher = Fernet(key)
        
        with open(VAULT_FILE, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = cipher.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Could not load saved passwords: {e}")
        return []

def save_passwords_to_vault(passwords):
    """Encrypt and save passwords to vault."""
    try:
        key = get_or_create_key()
        cipher = Fernet(key)
        
        json_data = json.dumps(passwords, indent=2)
        encrypted_data = cipher.encrypt(json_data.encode())
        
        with open(VAULT_FILE, 'wb') as f:
            f.write(encrypted_data)
        return True
    except Exception as e:
        print(f"Could not save passwords: {e}")
        return False

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
        
        # Add to history
        add_to_history(result)

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number for length.")

def add_to_history(password):
    """Add password to history with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    password_history.append({
        'password': password,
        'time': timestamp,
        'length': len(password)
    })
    
    # Keep only last 10 passwords in session history
    if len(password_history) > 10:
        password_history.pop(0)

def update_history_display():
    """Update the history display in the popup window."""
    history_text.delete(1.0, tk.END)
    
    if not password_history:
        history_text.insert(tk.END, "No passwords generated yet...")
        history_text.tag_add("center", "1.0", "end")
        history_text.tag_config("center", justify='center', foreground='#7CB68C')
        return
    
    history_text.insert(tk.END, "Time     | Password                                    | Length\n")
    history_text.insert(tk.END, "-" * 70 + "\n")
    
    for entry in reversed(password_history):
        line = f"{entry['time']} | {entry['password']:<43} | {entry['length']:>2}\n"
        history_text.insert(tk.END, line)

def save_password_with_label():
    """Save current password to encrypted vault with a label."""
    password = password_entry.get()
    
    if not password:
        messagebox.showwarning("No Password", "Please generate a password first!")
        return
    
    # Create dialog to get label
    label_window = tk.Toplevel(root)
    label_window.title("Save Password")
    label_window.geometry("400x200")
    label_window.configure(bg="#E8F4ED")
    label_window.resizable(False, False)
    
    # Set icon - UPDATED with resource_path
    try:
        label_window.iconbitmap(resource_path("icon.ico"))
    except:
        try:
            label_window.iconphoto(True, icon_photo)
        except:
            pass
    
    tk.Label(label_window, text="💾 Save Password", 
            font=("Arial", 16, "bold"), bg="#E8F4ED", fg="#2D5F3F").pack(pady=15)
    
    tk.Label(label_window, text="Enter a label for this password:", 
            font=("Arial", 10), bg="#E8F4ED", fg="#2D5F3F").pack(pady=5)
    
    label_entry = tk.Entry(label_window, font=("Arial", 11), width=30, 
                          bg="#F5FAF7", fg="#2D5F3F")
    label_entry.pack(pady=10)
    label_entry.focus()
    
    def save_it():
        label = label_entry.get().strip()
        if not label:
            messagebox.showwarning("No Label", "Please enter a label!")
            return
        
        # Load existing passwords
        saved_passwords = load_saved_passwords()
        
        # Add new password
        saved_passwords.append({
            'label': label,
            'password': password,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'length': len(password)
        })
        
        # Save to vault
        if save_passwords_to_vault(saved_passwords):
            messagebox.showinfo("Saved!", f"Password saved as '{label}' in encrypted vault!")
            label_window.destroy()
        else:
            messagebox.showerror("Error", "Could not save password to vault!")
    
    button_frame = tk.Frame(label_window, bg="#E8F4ED")
    button_frame.pack(pady=15)
    
    tk.Button(button_frame, text="💾 Save", command=save_it,
             bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
             padx=20, pady=5, cursor="hand2", relief="flat").pack(side=tk.LEFT, padx=5)
    
    tk.Button(button_frame, text="✖ Cancel", command=label_window.destroy,
             bg="#FF6B6B", fg="white", font=("Arial", 11, "bold"),
             padx=20, pady=5, cursor="hand2", relief="flat").pack(side=tk.LEFT, padx=5)
    
    # Bind Enter key to save
    label_entry.bind('<Return>', lambda e: save_it())

def view_saved_passwords():
    """View all saved passwords in the vault."""
    saved_passwords = load_saved_passwords()
    
    vault_window = tk.Toplevel(root)
    vault_window.title("Password Vault")
    vault_window.geometry("800x500")
    vault_window.configure(bg="#E8F4ED")
    vault_window.resizable(False, False)
    
    # Set icon - UPDATED with resource_path
    try:
        vault_window.iconbitmap(resource_path("icon.ico"))
    except:
        try:
            vault_window.iconphoto(True, icon_photo)
        except:
            pass
    
    # Military robot icon for Vault - UPDATED with resource_path
    try:
        vault_icon = Image.open(resource_path("vault_icon.png"))
        vault_icon = vault_icon.resize((60, 60), Image.Resampling.LANCZOS)
        vault_icon_photo = ImageTk.PhotoImage(vault_icon)
        
        icon_lbl = tk.Label(vault_window, image=vault_icon_photo, bg="#E8F4ED")
        icon_lbl.image = vault_icon_photo
        icon_lbl.pack(pady=(15, 5))
    except Exception as e:
        print(f"Could not load vault icon: {e}")
    
    # Title
    tk.Label(vault_window, text="🔐 Password Vault", 
            font=("Arial", 18, "bold"), bg="#E8F4ED", fg="#2D5F3F").pack(pady=(0, 10))
    
    # Info
    tk.Label(vault_window, text=f"Total saved passwords: {len(saved_passwords)}", 
            font=("Arial", 10), bg="#E8F4ED", fg="#2D5F3F").pack(pady=5)
    
    # Passwords display
    vault_frame = tk.Frame(vault_window, bg="#9DC2A8", bd=2)
    vault_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)
    
    vault_text = scrolledtext.ScrolledText(
        vault_frame,
        font=("Courier", 9),
        bg="#F5FAF7",
        fg="#2D5F3F",
        wrap=tk.NONE,
        relief="flat",
        bd=0,
        padx=10,
        pady=10
    )
    vault_text.pack(fill=tk.BOTH, expand=True)
    
    # Display passwords
    if not saved_passwords:
        vault_text.insert(tk.END, "No saved passwords yet.\n\nGenerate a password and click the 💾 button to save it!")
    else:
        vault_text.insert(tk.END, "Label                    | Password                          | Date                | Length\n")
        vault_text.insert(tk.END, "-" * 100 + "\n")
        
        for entry in reversed(saved_passwords):
            line = f"{entry['label']:<24} | {entry['password']:<33} | {entry['date']:<19} | {entry['length']:>2}\n"
            vault_text.insert(tk.END, line)
    
    # Buttons
    button_frame = tk.Frame(vault_window, bg="#E8F4ED")
    button_frame.pack(pady=15)
    
    def copy_from_vault():
        try:
            selection = vault_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            root.clipboard_clear()
            root.clipboard_append(selection)
            messagebox.showinfo("Copied", "Selected text copied to clipboard!")
        except:
            messagebox.showwarning("No Selection", "Please select text to copy!")
    
    def delete_vault():
        if saved_passwords:
            response = messagebox.askyesno("Delete Vault", 
                                          "⚠️ Are you sure you want to delete ALL saved passwords?\n\nThis cannot be undone!")
            if response:
                if save_passwords_to_vault([]):
                    messagebox.showinfo("Deleted", "All passwords have been deleted from vault!")
                    vault_window.destroy()
        else:
            messagebox.showinfo("Empty", "Vault is already empty!")
    
    tk.Button(button_frame, text="📋 Copy Selection", command=copy_from_vault,
             bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
             padx=15, pady=5, cursor="hand2", relief="flat").pack(side=tk.LEFT, padx=5)
    
    tk.Button(button_frame, text="🗑️ Delete All", command=delete_vault,
             bg="#FF6B6B", fg="white", font=("Arial", 10, "bold"),
             padx=15, pady=5, cursor="hand2", relief="flat").pack(side=tk.LEFT, padx=5)
    
    tk.Button(button_frame, text="✖ Close", command=vault_window.destroy,
             bg="#5FA877", fg="white", font=("Arial", 10, "bold"),
             padx=20, pady=5, cursor="hand2", relief="flat").pack(side=tk.LEFT, padx=5)

def show_history_window():
    """Open a new window showing password history."""
    global history_text
    
    history_window = tk.Toplevel(root)
    history_window.title("Password History")
    history_window.geometry("700x450")
    history_window.configure(bg="#E8F4ED")
    history_window.resizable(False, False)
    
    # Set icon - UPDATED with resource_path
    try:
        history_window.iconbitmap(resource_path("icon.ico"))
    except:
        try:
            history_window.iconphoto(True, icon_photo)
        except:
            pass
    
    # Blue dizzy robot icon for History - UPDATED with resource_path
    try:
        history_icon = Image.open(resource_path("history_icon.png"))
        history_icon = history_icon.resize((60, 60), Image.Resampling.LANCZOS)
        history_icon_photo = ImageTk.PhotoImage(history_icon)
        
        icon_lbl = tk.Label(history_window, image=history_icon_photo, bg="#E8F4ED")
        icon_lbl.image = history_icon_photo
        icon_lbl.pack(pady=(15, 5))
    except Exception as e:
        print(f"Could not load history icon: {e}")
    
    # Title
    title = tk.Label(history_window, text="📜 Password History", 
                    font=("Arial", 18, "bold"), bg="#E8F4ED", fg="#2D5F3F")
    title.pack(pady=(0, 10))
    
    # Info label
    info = tk.Label(history_window, text=f"Last {len(password_history)} generated passwords (newest first):", 
                   font=("Arial", 10), bg="#E8F4ED", fg="#2D5F3F")
    info.pack(pady=5)
    
    # History text area with frame
    history_frame = tk.Frame(history_window, bg="#9DC2A8", bd=2)
    history_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)
    
    history_text = scrolledtext.ScrolledText(
        history_frame,
        font=("Courier", 10),
        bg="#F5FAF7",
        fg="#2D5F3F",
        wrap=tk.NONE,
        relief="flat",
        bd=0,
        padx=10,
        pady=10
    )
    history_text.pack(fill=tk.BOTH, expand=True)
    
    update_history_display()
    
    # Buttons frame
    button_frame = tk.Frame(history_window, bg="#E8F4ED")
    button_frame.pack(pady=15)
    
    # Clear history button
    clear_btn = tk.Button(button_frame, text="🗑️ Clear History", command=clear_history,
                         bg="#FF6B6B", fg="white", font=("Arial", 10, "bold"),
                         padx=15, pady=5, cursor="hand2", relief="flat",
                         activebackground="#EE5A52")
    clear_btn.pack(side=tk.LEFT, padx=5)
    
    # Close button
    close_btn = tk.Button(button_frame, text="✖ Close", command=history_window.destroy,
                         bg="#5FA877", fg="white", font=("Arial", 10, "bold"),
                         padx=20, pady=5, cursor="hand2", relief="flat",
                         activebackground="#4E8A62")
    close_btn.pack(side=tk.LEFT, padx=5)

def clear_history():
    """Clear all password history."""
    global password_history
    if password_history:
        response = messagebox.askyesno("Clear History", 
                                       "Are you sure you want to clear all password history?")
        if response:
            password_history = []
            update_history_display()
            messagebox.showinfo("Cleared", "Password history has been cleared!")
    else:
        messagebox.showinfo("Empty", "History is already empty!")

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

# Set the app icon - UPDATED with resource_path
try:
    root.iconbitmap(resource_path("icon.ico"))
    print("Loaded .ico icon")
except:
    try:
        icon_image = Image.open(resource_path("icon.png"))
        icon_photo = ImageTk.PhotoImage(icon_image)
        root.iconphoto(True, icon_photo)
        print("Loaded .png icon")
    except Exception as e:
        print(f"Could not load icon: {e}")

# Load background image - UPDATED with resource_path
try:
    original_image = Image.open(resource_path("background.png"))
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
main_frame.place(x=40, y=40, width=380, height=460)

# Subtle border
border_frame = tk.Frame(root, bg="#9DC2A8", bd=0)
border_frame.place(x=38, y=38, width=384, height=464)
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

# Password field with ALL buttons in one row
result_frame = tk.Frame(main_frame, bg="#E8F4ED")
result_frame.pack(pady=5, padx=20, fill="x")

password_entry = tk.Entry(result_frame, font=("Courier", 10), justify="center",
                         bg="#F5FAF7", fg="#2D5F3F", relief="flat", bd=1, 
                         highlightthickness=1, highlightbackground="#9DC2A8",
                         highlightcolor="#FF8C42")
password_entry.pack(side=tk.LEFT, padx=5, fill="x", expand=True, ipady=4)

# Save button (💾)
save_btn = tk.Button(result_frame, text="💾", command=save_password_with_label,
                    bg="#9C27B0", fg="white", font=("Arial", 11), cursor="hand2",
                    activebackground="#7B1FA2", relief="flat", bd=0, padx=8, pady=4)
save_btn.pack(side=tk.LEFT, padx=1)

# Copy button (📋)
copy_btn = tk.Button(result_frame, text="📋", command=copy_to_clipboard,
                     bg="#5FA877", fg="white", font=("Arial", 11), cursor="hand2",
                     activebackground="#4E8A62", relief="flat", bd=0, padx=8, pady=4)
copy_btn.pack(side=tk.LEFT, padx=1)

# History button (📜)
history_btn = tk.Button(result_frame, text="📜", command=show_history_window,
                       bg="#2196F3", fg="white", font=("Arial", 11), cursor="hand2",
                       activebackground="#1976D2", relief="flat", bd=0, padx=8, pady=4)
history_btn.pack(side=tk.LEFT, padx=1)

# Vault button (🔐)
vault_btn = tk.Button(result_frame, text="🔐", command=view_saved_passwords,
                     bg="#9C27B0", fg="white", font=("Arial", 11), cursor="hand2",
                     activebackground="#7B1FA2", relief="flat", bd=0, padx=8, pady=4)
vault_btn.pack(side=tk.LEFT)

# Info label at the bottom
info_label = tk.Label(main_frame, text="💾 Save  📋 Copy  📜 History  🔐 Vault", 
                     font=("Arial", 8), bg="#E8F4ED", fg="#7CB68C")
info_label.pack(pady=(10, 5))

root.mainloop()