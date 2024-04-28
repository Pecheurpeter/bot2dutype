from tkinter import Tk, ttk, StringVar, messagebox, Entry
from tkinter.font import Font
import subprocess
import threading
import requests
import sys
import os
from datetime import datetime, timezone
from tkinter.scrolledtext import ScrolledText

script_process = None

def get_pc_uuid():
    try:
        output = subprocess.check_output('wmic csproduct get uuid', shell=True)
        uuid = output.decode().split('\n')[1].strip()
        return uuid
    except Exception as e:
        messagebox.showerror("Error", f"Error retrieving PC UUID: {e}")
        return None

def validate_token(token):
    pc_uuid = get_pc_uuid()
    if not pc_uuid:
        messagebox.showwarning("Warning", "PC UUID could not be retrieved.")
        return False
    
    SUPABASE_URL = ''
    SUPABASE_KEY = ''
    TABLE_NAME = 'license_keys'
    
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    query_url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?token=eq.{token}&uuid=eq.{pc_uuid}"
    response = requests.get(query_url, headers=headers)
    
    if response.status_code == 200 and response.json():
        license_data = response.json()[0]
        expires_at = license_data['expires_at']
        if expires_at:
            expires_at = datetime.fromisoformat(expires_at)
        if license_data['active'] and (expires_at is None or expires_at > datetime.now(timezone.utc)):
            return True
    return False

def update_status(status):
    status_var.set(f"Status: {status}")

def start_script():
    global script_process

    token = token_entry.get()
    if validate_token(token):
        if getattr(sys, 'frozen', False):
            bundled_path = os.path.join(sys._MEIPASS, 'main.py')
        else:
            bundled_path = 'main.py'

        script_process = subprocess.Popen(['python', bundled_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)
        update_status("Running")
        threading.Thread(target=update_console_and_wait, args=(console, script_process), daemon=True).start()
    else:
        messagebox.showerror("Error", "Invalid token or expired license.")

def update_console_and_wait(console, process):
    while True:
        output = process.stdout.readline()
        if output:
            if "WARNING: Wireshark is installed, but cannot read manuf" not in output:
                console.insert('end', output)
                console.see('end')
        if output == '' and process.poll() is not None:
            break
    update_status("Stopped")

def on_stop_button_click():
    global script_process
    if script_process:
        script_process.terminate()
        script_process = None
        update_status("Stopped")

root = Tk()
root.title("Superior PICwarior381")
root.geometry("270x600")
root.configure(bg="#333333")
root.iconbitmap("utils/spartan.ico")

customFont = Font(family="Segoe UI", size=10)

dark_bg = "#333333"
light_fg = "#ffffff"
light_bg = "#ff0000"
button_active_bg = "#555555"

status_var = StringVar()
status_var.set("Status: Not Started Yet")
status_label = ttk.Label(root, textvariable=status_var, font=customFont, background=dark_bg, foreground=light_fg)
status_label.pack(pady=(10, 0))

token_label = ttk.Label(root, text="Token:", font=customFont, background=dark_bg, foreground=light_fg)
token_label.pack(pady=(10, 0))
token_var = StringVar()
token_entry = Entry(root, textvariable=token_var, font=customFont, bg=dark_bg, fg=light_fg, insertbackground=light_fg)
token_entry.pack(pady=(5, 10))

style = ttk.Style()
style.configure('TButton', font=('Segoe UI', 10), borderwidth='1')
style.map('TButton',
          foreground=[('pressed', light_bg), ('active', light_bg)],
          background=[('pressed', '!disabled', button_active_bg), ('active', button_active_bg)])

start_button = ttk.Button(root, text="Start", command=start_script)
start_button.pack(pady=5, fill='x', padx=10)
stop_button = ttk.Button(root, text="Stop", command=on_stop_button_click)
stop_button.pack(pady=5, fill='x', padx=10)

console = ScrolledText(root, height=10, bg="#222222", fg=light_fg, borderwidth=1, relief="solid", font=("Consolas", 10))
console.pack(pady=(5, 10), fill='both', expand=True, padx=10)

root.mainloop()
