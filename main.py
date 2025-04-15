#!/usr/bin/env python3
import sys
import os
import curses
import curses.textpad
import csv
import math
import json
import re
import textwrap
import subprocess
import time
import base64
import requests
from datetime import datetime, timedelta, date

# --- Encryption Imports ---
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# -------------------------------------------------------------------------
# ENCRYPTION/DECRYPTION FUNCTIONS
# -------------------------------------------------------------------------
def derive_key(passphrase, salt):
    """
    Derive a 256-bit key from the given passphrase and salt using PBKDF2HMAC.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(passphrase.encode())

def encrypt_data(data, passphrase):
    """
    Encrypt data using AESGCM. Returns salt + nonce + ciphertext.
    """
    salt = os.urandom(16)
    key = derive_key(passphrase, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return salt + nonce + ciphertext

def decrypt_data(enc_data, passphrase):
    """
    Decrypt data that was encrypted using encrypt_data.
    Expects first 16 bytes as salt and next 12 bytes as nonce.
    """
    salt = enc_data[:16]
    nonce = enc_data[16:28]
    ciphertext = enc_data[28:]
    key = derive_key(passphrase, salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)

# -------------------------------------------------------------------------
# CONFIGURATION MANAGEMENT (Persistent, Encrypted)
# -------------------------------------------------------------------------
CONFIG_FILE = "config.json"

def encrypt_config_data(data, master_password):
    """
    Serialize the configuration dictionary to JSON, encrypt it using AES-GCM,
    and return a base64-encoded string containing salt + nonce + ciphertext.
    """
    plaintext = json.dumps(data).encode("utf-8")
    salt = os.urandom(16)
    key = derive_key(master_password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    encrypted = salt + nonce + ciphertext
    return base64.b64encode(encrypted).decode("utf-8")

def decrypt_config_data(enc_data_str, master_password):
    """
    Decrypt the configuration data (base64-encoded) using the master password
    and return the configuration dictionary.
    """
    encrypted = base64.b64decode(enc_data_str.encode("utf-8"))
    salt = encrypted[:16]
    nonce = encrypted[16:28]
    ciphertext = encrypted[28:]
    key = derive_key(master_password, salt)
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return json.loads(plaintext.decode("utf-8"))

def load_config():
    """Load configuration from config.json if it exists."""
    if os.path.exists(CONFIG_FILE):
        master_pass = input("Enter your master configuration password: ").strip()
        with open(CONFIG_FILE, "r") as f:
            enc_data = f.read().strip()
        try:
            config = decrypt_config_data(enc_data, master_pass)
            return config
        except Exception as e:
            sys.exit(f"Failed to decrypt configuration file: {e}")
    return {}

def save_config(config, master_password):
    """Encrypt the configuration dictionary with the master password and save it."""
    try:
        enc_data = encrypt_config_data(config, master_password)
        with open(CONFIG_FILE, "w") as f:
            f.write(enc_data)
    except Exception as e:
        print(f"Error saving configuration: {e}")

def prompt_for_config():
    """
    Loads configuration from config.json if it exists.
    Prompts the user for any missing required keys and then saves the config.
    Required keys: GITHUB_TOKEN, ENCRYPTION_PASSPHRASE, GITHUB_OWNER, GITHUB_REPO.
    Sets these values in os.environ.
    """
    config = load_config()
    required_keys = [
        ("GITHUB_TOKEN", "Enter your GitHub Token: "),
        ("ENCRYPTION_PASSPHRASE", "Enter your Encryption Passphrase (used to encrypt backups): "),
        ("GITHUB_OWNER", "Enter your GitHub Owner (username or organization: "),
        ("GITHUB_REPO", "Enter your GitHub Repository Name (e.g., tosk-backups): ")
    ]
    changed = False
    for key, prompt_text in required_keys:
        value = config.get(key, "").strip()
        if not value:
            value = input(prompt_text).strip()
            if key in ["GITHUB_TOKEN", "GITHUB_OWNER", "GITHUB_REPO"] and not value:
                sys.exit(f"{key} is required. Exiting.")
            config[key] = value
            changed = True
        os.environ[key] = config[key]
    if not os.path.exists(CONFIG_FILE) or changed:
        master_password = input("Set a master configuration password (used to encrypt your config): ").strip()
        if not master_password:
            sys.exit("Master configuration password is required. Exiting.")
        save_config(config, master_password)
    return config

# -------------------------------------------------------------------------
# HELPER: Resource Path (for PyInstaller)
# -------------------------------------------------------------------------
def resource_path(relative_path):
    """Return the absolute path to the resource."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# FILE CONSTANTS
TASK_FILE = "tasks.json"
LOG_FILE = "task_log.txt"
EXPORT_FILE = "tasks_export.csv"

# -------------------------------------------------------------------------
# BACKUP FUNCTIONS FOR GITHUB (WITH ENCRYPTION)
# -------------------------------------------------------------------------
def backup_file(local_file_path, repo_file_path, commit_message, branch="main"):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return "Error: GITHUB_TOKEN is not set in the environment."
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    owner = os.getenv("GITHUB_OWNER", "")
    repo  = os.getenv("GITHUB_REPO", "")
    if not os.path.exists(local_file_path):
        return f"File '{local_file_path}' not found; skipping backup."
    with open(local_file_path, "rb") as f:
        content = f.read()
    enc_pass = os.getenv("ENCRYPTION_PASSPHRASE")
    if enc_pass:
        encrypted_data = encrypt_data(content, enc_pass)
        data_to_upload = base64.b64encode(encrypted_data).decode("utf-8")
    else:
        data_to_upload = base64.b64encode(content).decode("utf-8")
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{repo_file_path}"
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None
    payload = {
        "message": commit_message,
        "content": data_to_upload,
        "branch": branch
    }
    if sha:
        payload["sha"] = sha
    put_response = requests.put(url, headers=headers, data=json.dumps(payload))
    if put_response.status_code in [200, 201]:
        return f"Backup of '{local_file_path}' succeeded."
    else:
        return f"Backup of '{local_file_path}' failed (Status: {put_response.status_code}): {put_response.text}"

def backup_to_github():
    messages = []
    msg1 = backup_file("tasks.json", "backups/tasks.json", "Manual backup: Update tasks.json")
    messages.append(msg1)
    if os.path.exists("tasks_export.csv"):
        msg2 = backup_file("tasks_export.csv", "backups/tasks_export.csv", "Manual backup: Update tasks_export.csv")
        messages.append(msg2)
    else:
        messages.append("Optional file 'tasks_export.csv' not found; skipped.")
    return messages

# -------------------------------------------------------------------------
# IMPORT FUNCTIONS FROM GITHUB (WITH DECRYPTION)
# -------------------------------------------------------------------------
def import_file_from_github(repo_file_path, local_file_path, branch="main"):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return "Error: GITHUB_TOKEN is not set in the environment."
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    owner = os.getenv("GITHUB_OWNER", "")
    repo  = os.getenv("GITHUB_REPO", "")
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{repo_file_path}?ref={branch}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            content_data = response.json()
            encoded_content = content_data["content"]
            downloaded_data = base64.b64decode(encoded_content.encode("utf-8"))
            enc_pass = os.getenv("ENCRYPTION_PASSPHRASE")
            if enc_pass:
                decrypted_data = decrypt_data(downloaded_data, enc_pass)
            else:
                decrypted_data = downloaded_data
            with open(local_file_path, "wb") as f:
                f.write(decrypted_data)
            return f"Imported '{local_file_path}' from GitHub."
        except Exception as e:
            return f"Error decoding or writing '{local_file_path}': {e}"
    else:
        return f"Failed to import '{local_file_path}' (Status: {response.status_code}): {response.text}"

def import_from_github():
    messages = []
    msg1 = import_file_from_github("backups/tasks.json", "tasks.json")
    messages.append(msg1)
    msg2 = import_file_from_github("backups/tasks_export.csv", "tasks_export.csv")
    messages.append(msg2)
    return messages

# -------------------------------------------------------------------------
# SPLASH
# -------------------------------------------------------------------------
def show_splash():
    try:
        viu_path = resource_path("bin/viu")
        img_path = resource_path("tosk.jpg")
        os.chmod(viu_path, 0o755)
        subprocess.call([viu_path, img_path])
        time.sleep(3)
    except Exception as e:
        print(f"Splash error: {e}")
    os.system("clear")

# -------------------------------------------------------------------------
# CURSES UI FUNCTIONS
# -------------------------------------------------------------------------
def selectable_menu(stdscr, title, options, start_row=0, error_msg=""):
    cur = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        # Draw the title centered.
        stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        tx = max(0, (w - len(title)) // 2)
        if start_row < h:
            stdscr.addnstr(start_row, tx, title, w - tx)
        stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        row = start_row + 2

        # Draw each menu option only if there's space.
        for idx, opt in enumerate(options):
            y = row + idx
            if y >= h:
                break  # no space to draw further options
            x = max(0, (w - len(opt)) // 2)
            display_length = max(0, w - x)
            try:
                if idx == cur:
                    stdscr.attron(curses.color_pair(6))
                    stdscr.addnstr(y, x, opt, display_length)
                    stdscr.attroff(curses.color_pair(6))
                else:
                    stdscr.attron(curses.color_pair(5))
                    stdscr.addnstr(y, x, opt, display_length)
                    stdscr.attroff(curses.color_pair(5))
            except curses.error:
                pass

        # Draw error message if provided and if there's space.
        if error_msg:
            err_y = row + len(options) + 2
            if err_y < h:
                err_x = max(0, (w - len(error_msg)) // 2)
                try:
                    stdscr.attron(curses.color_pair(4))
                    stdscr.addnstr(err_y, err_x, error_msg, max(0, w - err_x))
                    stdscr.attroff(curses.color_pair(4))
                except curses.error:
                    pass

        stdscr.refresh()
        k = stdscr.getch()
        if k in [curses.KEY_UP, ord('k')]:
            cur = (cur - 1) % len(options)
        elif k in [curses.KEY_DOWN, ord('j')]:
            cur = (cur + 1) % len(options)
        elif k in [10, 13]:
            return options[cur]


def selectable_menu_index(stdscr, title, options, start_row=0, error_msg=""):
    chosen = selectable_menu(stdscr, title, options, start_row, error_msg)
    return options.index(chosen)

def yes_no_menu(stdscr, prompt_str, start_row=0):
    return selectable_menu(stdscr, prompt_str, ["Yes", "No"], start_row=start_row)

def scrollable_view(stdscr, lines_with_attr):
    h, w = stdscr.getmaxyx()
    pad_height = max(len(lines_with_attr) + 1, h)
    pad = curses.newpad(pad_height, w)
    for i, (line, attr) in enumerate(lines_with_attr):
        current_attr = attr if attr else curses.color_pair(5)
        try:
            pad.addstr(i, 0, line, current_attr)
        except curses.error:
            pass
    top_line = 0
    pad.refresh(top_line, 0, 0, 0, h - 1, w - 1)
    while True:
        key = stdscr.getch()
        if key in [ord('q'), 27]:
            break
        elif key in [curses.KEY_UP, ord('k')]:
            top_line = max(0, top_line - 1)
        elif key in [curses.KEY_DOWN, ord('j')]:
            top_line = min(pad_height - h, top_line + 1)
        pad.refresh(top_line, 0, 0, 0, h - 1, w - 1)

def draw_popup(stdscr, content):
    h, w = stdscr.getmaxyx()
    wrap_w = max(10, w - 8)
    lines = []
    for line in content.splitlines():
        lines.extend(textwrap.wrap(line, wrap_w) or [""])
    if not lines:
        lines = ["[empty]"]
    max_len = max(len(ln) for ln in lines)
    box_w = min(w - 4, max_len + 4)
    box_h = min(h - 4, len(lines) + 4)
    start_y = (h - box_h) // 2
    start_x = (w - box_w) // 2
    win = curses.newwin(box_h, box_w, start_y, start_x)
    win.box()
    for idx, ln in enumerate(lines):
        if idx + 1 < box_h - 2:
            try:
                win.addstr(idx + 1, 2, ln, curses.color_pair(5))
            except curses.error:
                pass
    try:
        win.addstr(box_h - 2, 2, "Press q or ESC to close", curses.color_pair(5))
    except curses.error:
        pass
    win.refresh()
    while True:
        c = win.getch()
        if c in [ord('q'), 27]:
            break
    win.clear()
    stdscr.touchwin()
    stdscr.refresh()

def prompt_input(stdscr, y, x, prompt):
    curses.echo()
    stdscr.attron(curses.color_pair(2))
    stdscr.addstr(y, x, prompt)
    stdscr.attroff(curses.color_pair(2))
    stdscr.refresh()
    txt = stdscr.getstr(y, x + len(prompt), 50).decode('utf-8')
    curses.noecho()
    return txt

def edit_field(stdscr, y, x, width, initial_text):
    h, w = stdscr.getmaxyx()
    eff_w = min(width, w - 4)
    truncated = initial_text[:eff_w]
    win = curses.newwin(1, eff_w, y, x)
    try:
        win.addnstr(0, 0, truncated, eff_w)
    except curses.error:
        pass
    stdscr.attron(curses.color_pair(2))
    stdscr.addstr(y + 1, x, "(Press ENTER to move onto the next step)")
    stdscr.attroff(curses.color_pair(2))
    stdscr.refresh()
    box = curses.textpad.Textbox(win)
    curses.curs_set(1)
    new_text = box.edit().strip()
    curses.curs_set(0)
    return new_text

def load_tasks():
    if not os.path.exists("tasks.json"):
        return []
    with open("tasks.json", 'r') as f:
        return json.load(f)

def save_tasks(tasks):
    with open("tasks.json", 'w') as f:
        json.dump(tasks, f, indent=2)

def add_task(line, category="General"):
    tasks = load_tasks()
    parts = line.split("::")
    title = parts[0].strip() if len(parts) > 0 else "Untitled"
    dur_str = parts[1].strip() if len(parts) > 1 else "60"
    pri_str = parts[2].strip() if len(parts) > 2 else "1"
    dd_str = parts[3].strip() if len(parts) > 3 else ""
    duration = 60
    try:
        duration = int(dur_str)
    except:
        pass
    priority = 1
    try:
        priority = int(pri_str)
    except:
        pass
    new_task = {
        "id": len(tasks) + 1,
        "title": title,
        "duration": duration,
        "category": category,
        "priority": priority,
        "completed": False,
        "due_date": dd_str
    }
    tasks.append(new_task)
    save_tasks(tasks)

def update_task(task_id, new_title=None, new_duration=None, new_priority=None):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            if new_title and new_title.strip():
                t["title"] = new_title.strip()
            if new_duration and new_duration.strip():
                try:
                    t["duration"] = int(new_duration.strip())
                except:
                    pass
            if new_priority and new_priority.strip():
                try:
                    t["priority"] = int(new_priority.strip())
                except:
                    pass
            break
    save_tasks(tasks)

def delete_task(task_id):
    tasks = load_tasks()
    newlist = [t for t in tasks if t["id"] != task_id]
    for idx, t in enumerate(newlist, 1):
        t["id"] = idx
    save_tasks(newlist)

def draw_status_bar(stdscr, text):
    h, w = stdscr.getmaxyx()
    stdscr.attron(curses.color_pair(2))
    stdscr.addstr(h - 1, 0, text.ljust(w - 1))
    stdscr.attroff(curses.color_pair(2))
    stdscr.refresh()

def update_status_bar(stdscr):
    tasks = load_tasks()
    total = len(tasks)
    completed = sum(1 for t in tasks if t.get("completed", False))
    bar = f"Total: {total} | Completed: {completed}"
    draw_status_bar(stdscr, bar)

# -------------------------------------------------------------------------
# UPDATED HELP SCREEN (Covering ALL Functions)
# -------------------------------------------------------------------------
def help_screen(stdscr):
    lines = [
        ("=== HELP ===", curses.color_pair(2) | curses.A_BOLD),
        ("", None),
        ("General Controls:", curses.A_BOLD),
        ("  - Use arrow keys or j/k/h/l to navigate menus.", None),
        ("  - Press Enter to select an option.", None),
        ("  - Press q or ESC to exit a menu or popup.", None),
        ("", None),
        ("Main Menu Options:", curses.A_BOLD),
        ("  - View Tasks: Display your tasks in a selectable grid.", None),
        ("  - Manage Tasks: Open the task management submenu.", None),
        ("  - Help: View this help screen.", None),
        ("  - Exit: Quit the application.", None),
        ("", None),
        ("Manage Tasks Submenu:", curses.A_BOLD),
        ("  - View All Tasks: See all tasks (same as View Tasks).", None),
        ("  - Add New Tasks: Enter new tasks using the format:", None),
        ("      title::duration::priority::due_date", None),
        ("      e.g., Buy milk::30::1::2025-01-01", None),
        ("  - Edit Task: Select and edit an existing task.", None),
        ("  - Delete Task: Remove a task from your list.", None),
        ("  - Export Tasks: Save tasks to a CSV file (tasks_export.csv).", None),
        ("  - Import Tasks: Load tasks from a CSV file (tasks_export.csv).", None),
        ("  - Add Due Date: Use a calendar grid to assign a due date.", None),
        ("  - Import Plaintext: Import tasks from a plaintext file.", None),
        ("  - Backup to GitHub: Encrypt (if enabled) and upload your tasks.", None),
        ("  - Import from GitHub: Download and decrypt your tasks from GitHub.", None),
        ("  - Help: Show this help screen.", None),
        ("  - Back to Main Menu: Return to the main menu.", None),
        ("", None),
        ("Calendar Controls:", curses.A_BOLD),
        ("  - Use arrow keys to navigate the month, day, and year grids.", None),
        ("  - Press Enter to select the highlighted value.", None),
        ("  - Press q or ESC to cancel the selection.", None),
        ("", None),
        ("Configuration & Security:", curses.A_BOLD),
        ("  - On first run, you'll be prompted for:", None),
        ("      • GitHub Token", None),
        ("      • Encryption Passphrase (for backups)", None),
        ("      • GitHub Owner (username/organization)", None),
        ("      • GitHub Repository Name", None),
        ("  - These values are encrypted and stored in config.json", None),
        ("    using a master configuration password.", None),
        ("  - On subsequent runs, you only need to enter the master password.", None),
        ("  - All communication with GitHub is done over HTTPS.", None),
        ("", None),
        ("GitHub Backup & Import:", curses.A_BOLD),
        ("  - Backup to GitHub encrypts your local tasks (if an encryption", None),
        ("    passphrase is set) and uploads them to your private repo.", None),
        ("  - Import from GitHub downloads and decrypts your tasks for local use.", None),
        ("", None),
        ("Press Q to return to the previous menu.", curses.color_pair(2) | curses.A_BOLD)
    ]
    scrollable_view(stdscr, lines)

# -------------------------------------------------------------------------
# CONTINUED CURSES UI FUNCTIONS (Logging, Task operations, etc.)
# -------------------------------------------------------------------------
def log_action(action, task):
    if not os.path.exists("task_log.txt"):
        open("task_log.txt", 'w').close()
    try:
        with open("task_log.txt", 'a') as f:
            stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{stamp}] {action} - Task {task.get('id')}: {task.get('title')}\n")
    except:
        pass

def toggle_task_completion(task_id):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["completed"] = not t.get("completed", False)
            log_action("TOGGLE_COMPLETION", t)
            break
    save_tasks(tasks)

def import_plaintext_file(stdscr):
    stdscr.clear()
    stdscr.addstr(0, 0, "Import Plaintext File", curses.color_pair(2) | curses.A_BOLD)
    stdscr.addstr(2, 0, "Enter filename (e.g. tasks_import.txt):", curses.color_pair(5))
    stdscr.refresh()
    fname = prompt_input(stdscr, 3, 0, "> ")
    fname = fname.strip()
    if not os.path.exists(fname):
        draw_popup(stdscr, f"File not found: {fname}")
        return
    added_count = 0
    with open(fname, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                add_task(line)
                added_count += 1
    draw_popup(stdscr, f"Imported {added_count} tasks from {fname}.")

def export_tasks_to_csv(stdscr):
    tasks = load_tasks()
    if not tasks:
        draw_popup(stdscr, "No tasks to export.")
        return
    try:
        with open("tasks_export.csv", 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(["ID", "Title", "Duration", "Category", "Priority", "Due Date", "Completed"])
            for t in tasks:
                w.writerow([
                    t.get("id"),
                    t.get("title"),
                    t.get("duration", 60),
                    t.get("category", "General"),
                    t.get("priority", 1),
                    t.get("due_date", ""),
                    t.get("completed", False)
                ])
        draw_popup(stdscr, f"Tasks exported to tasks_export.csv")
    except Exception as e:
        draw_popup(stdscr, f"Export failed: {e}")

def import_tasks_from_csv(stdscr):
    if not os.path.exists("tasks_export.csv"):
        draw_popup(stdscr, "No CSV file: tasks_export.csv")
        return
    try:
        with open("tasks_export.csv", 'r', newline='') as f:
            rd = csv.DictReader(f)
            newt = []
            for row in rd:
                newt.append({
                    "id": int(row["ID"]),
                    "title": row["Title"],
                    "duration": int(row["Duration"]),
                    "category": row.get("Category", "General"),
                    "priority": int(row.get("Priority", "1")),
                    "due_date": row.get("Due Date", ""),
                    "completed": (row.get("Completed", "False") == "True")
                })
        save_tasks(newt)
        draw_popup(stdscr, "Imported tasks from tasks_export.csv")
    except Exception as e:
        draw_popup(stdscr, f"Import failed: {e}")

def import_file_from_github(repo_file_path, local_file_path, branch="main"):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return "Error: GITHUB_TOKEN is not set in the environment."
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    owner = os.getenv("GITHUB_OWNER", "")
    repo  = os.getenv("GITHUB_REPO", "")
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{repo_file_path}?ref={branch}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            content_data = response.json()
            encoded_content = content_data["content"]
            downloaded_data = base64.b64decode(encoded_content.encode("utf-8"))
            enc_pass = os.getenv("ENCRYPTION_PASSPHRASE")
            if enc_pass:
                decrypted_data = decrypt_data(downloaded_data, enc_pass)
            else:
                decrypted_data = downloaded_data
            with open(local_file_path, "wb") as f:
                f.write(decrypted_data)
            return f"Imported '{local_file_path}' from GitHub."
        except Exception as e:
            return f"Error decoding or writing '{local_file_path}': {e}"
    else:
        return f"Failed to import '{local_file_path}' (Status: {response.status_code}): {response.text}"

def import_from_github():
    messages = []
    msg1 = import_file_from_github("backups/tasks.json", "tasks.json")
    messages.append(msg1)
    msg2 = import_file_from_github("backups/tasks_export.csv", "tasks_export.csv")
    messages.append(msg2)
    return messages

def display_tasks_screen(stdscr, tasks, header):
    stdscr.clear()
    stdscr.attron(curses.color_pair(2) | curses.A_BOLD | curses.A_UNDERLINE)
    stdscr.addstr(0, 0, header)
    stdscr.attroff(curses.color_pair(2) | curses.A_BOLD | curses.A_UNDERLINE)
    row = 2
    if tasks:
        for t in tasks:
            st = "[Done]" if t.get("completed", False) else ""
            dd = t.get("due_date", "")
            line = f"ID {t['id']}: {st}{t['title']} (Dur {t.get('duration',60)}, Pri {t.get('priority',1)}, Due {dd})"
            stdscr.attron(curses.color_pair(5))
            stdscr.addstr(row, 2, line)
            stdscr.attroff(curses.color_pair(5))
            row += 1
    else:
        stdscr.attron(curses.color_pair(5))
        stdscr.addstr(row, 2, "No tasks found.")
        stdscr.attroff(curses.color_pair(5))
    stdscr.addstr(row + 2, 2, "Press Q key to return...", curses.color_pair(2))
    stdscr.refresh()
    stdscr.getch()

def add_tasks_screen(stdscr):
    stdscr.clear()
    stdscr.addstr(0, 0, "Enter tasks (title::dur::pri::due). '.' or 'q' to finish.", curses.color_pair(2))
    row = 3
    curses.echo()
    while True:
        stdscr.attron(curses.color_pair(5))
        stdscr.addstr(row, 0, "> ")
        stdscr.attroff(curses.color_pair(5))
        line = stdscr.getstr(row, 2, 200).decode('utf-8')
        if line.strip() in [".", "q", "Q"]:
            break
        if line.strip():
            add_task(line.strip())
        row += 1
    curses.noecho()
    stdscr.addstr(row + 2, 0, "Tasks added. Press any key...", curses.color_pair(2))
    stdscr.refresh()
    stdscr.getch()

def edit_tasks_screen(stdscr):
    tasks = load_tasks()
    if not tasks:
        display_tasks_screen(stdscr, tasks, "No tasks to edit.")
        return
    opts = [f"ID {t['id']}: {t['title'][:40]}" for t in tasks]
    idx = selectable_menu_index(stdscr, "Select Task to Edit", opts, start_row=1)
    chosen = tasks[idx]
    stdscr.clear()
    stdscr.addstr(0, 0, "Editing Task:", curses.color_pair(2) | curses.A_BOLD)
    stdscr.attron(curses.color_pair(5))
    stdscr.addstr(1, 0, f"(Current Title: {chosen['title']})")
    stdscr.attroff(curses.color_pair(5))
    hh, ww = stdscr.getmaxyx()
    tw = ww - 4
    new_title = edit_field(stdscr, 2, 0, tw, chosen["title"])
    stdscr.addstr(4, 0, f"(Current Dur: {chosen.get('duration',60)})", curses.color_pair(5))
    new_dur = edit_field(stdscr, 5, 0, 10, str(chosen.get("duration",60)))
    stdscr.addstr(7, 0, f"(Current Priority: {chosen.get('priority',1)})", curses.color_pair(5))
    new_pri = edit_field(stdscr, 8, 0, 10, str(chosen.get("priority",1)))
    update_task(chosen["id"], new_title, new_dur, new_pri)
    stdscr.addstr(10, 0, "Task updated. Press any key...", curses.color_pair(2))
    stdscr.refresh()
    stdscr.getch()

def delete_tasks_screen(stdscr):
    tasks = load_tasks()
    if not tasks:
        display_tasks_screen(stdscr, tasks, "No tasks to delete.")
        return
    opts = [f"ID {t['id']}: {t['title'][:40]}" for t in tasks]
    idx = selectable_menu_index(stdscr, "Select Task to Delete", opts, start_row=1)
    chosen = tasks[idx]
    c = yes_no_menu(stdscr, f"Delete Task [ID {chosen['id']}]: {chosen['title'][:40]}?", start_row=1)
    if c == "Yes":
        delete_task(chosen['id'])
        stdscr.clear()
        stdscr.addstr(2, 2, "Task deleted. Press any key...", curses.color_pair(2))
        stdscr.refresh()
        stdscr.getch()

def select_month_grid(stdscr):
    months = [f"{m:02d}" for m in range(1,13)]
    grid = []
    idx = 0
    for r in range(3):
        row = []
        for c in range(4):
            row.append(months[idx])
            idx += 1
        grid.append(row)
    cur_r = 0
    cur_c = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        title = "Select Month (Grid)"
        stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(1, max(0, (w - len(title)) // 2), title)
        stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        cell_w = 4
        total_w = cell_w * 4 + (4 - 1) * 2
        left_x = max(0, (w - total_w) // 2)
        top_y = 3
        for rr in range(3):
            y = top_y + rr
            x = left_x
            for cc in range(4):
                val = grid[rr][cc]
                if rr == cur_r and cc == cur_c:
                    stdscr.attron(curses.color_pair(6))
                    stdscr.addstr(y, x, val.center(cell_w))
                    stdscr.attroff(curses.color_pair(6))
                else:
                    stdscr.attron(curses.color_pair(5))
                    stdscr.addstr(y, x, val.center(cell_w))
                    stdscr.attroff(curses.color_pair(5))
                x += cell_w + 2
        msg = "[Arrows => Move; Enter => Select month; q => cancel]"
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(top_y + 4, max(0, (w - len(msg)) // 2), msg)
        stdscr.attroff(curses.color_pair(2))
        stdscr.refresh()
        k = stdscr.getch()
        if k in [ord('q'), 27]:
            return ""
        elif k in [curses.KEY_UP, ord('k')]:
            cur_r = (cur_r - 1) % 3
        elif k in [curses.KEY_DOWN, ord('j')]:
            cur_r = (cur_r + 1) % 3
        elif k in [curses.KEY_LEFT, ord('h')]:
            cur_c = (cur_c - 1) % 4
        elif k in [curses.KEY_RIGHT, ord('l')]:
            cur_c = (cur_c + 1) % 4
        elif k in [10, 13]:
            return grid[cur_r][cur_c]

def select_day_grid(stdscr):
    days = [f"{d:02d}" for d in range(1,32)]
    grid = []
    idx = 0
    for r in range(5):
        row = []
        for c in range(7):
            val = days[idx] if idx < len(days) else ""
            row.append(val)
            idx += 1
        grid.append(row)
    cur_r = 0
    cur_c = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        title = "Select Day (Grid)"
        stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(1, max(0, (w - len(title)) // 2), title)
        stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        cell_w = 4
        total_w = cell_w * 7 + (7 - 1) * 2
        left_x = max(0, (w - total_w) // 2)
        top_y = 3
        for rr in range(5):
            y = top_y + rr
            x = left_x
            for cc in range(7):
                val = grid[rr][cc]
                disp = val if val else "  "
                if rr == cur_r and cc == cur_c:
                    stdscr.attron(curses.color_pair(6))
                    stdscr.addstr(y, x, disp.center(cell_w))
                    stdscr.attroff(curses.color_pair(6))
                else:
                    stdscr.attron(curses.color_pair(5))
                    stdscr.addstr(y, x, disp.center(cell_w))
                    stdscr.attroff(curses.color_pair(5))
                x += cell_w + 2
        msg = "[Arrows => Move; Enter => Select day; q => cancel]"
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(top_y + 6, max(0, (w - len(msg)) // 2), msg)
        stdscr.attroff(curses.color_pair(2))
        stdscr.refresh()
        k = stdscr.getch()
        if k in [ord('q'), 27]:
            return ""
        elif k in [curses.KEY_UP, ord('k')]:
            cur_r = (cur_r - 1) % 5
        elif k in [curses.KEY_DOWN, ord('j')]:
            cur_r = (cur_r + 1) % 5
        elif k in [curses.KEY_LEFT, ord('h')]:
            cur_c = (cur_c - 1) % 7
        elif k in [curses.KEY_RIGHT, ord('l')]:
            cur_c = (cur_c + 1) % 7
        elif k in [10, 13]:
            val = grid[cur_r][cur_c]
            if val:
                return val

def select_year(stdscr):
    years = [str(y) for y in range(2023, 2033)]
    idx = selectable_menu_index(stdscr, "Select Year", years, start_row=2)
    if idx < 0:
        return ""
    return years[idx]

def select_date_screen(stdscr):
    y = select_year(stdscr)
    if not y:
        return ""
    m = select_month_grid(stdscr)
    if not m:
        return ""
    d = select_day_grid(stdscr)
    if not d:
        return ""
    return f"{y}-{m}-{d}"

def add_due_date_to_task_screen(stdscr):
    tasks = load_tasks()
    if not tasks:
        draw_popup(stdscr, "No tasks available.")
        return
    opts = [f"ID {t['id']}: {t['title'][:40]}" for t in tasks]
    idx = selectable_menu_index(stdscr, "Select Task to Add Due Date", opts, start_row=2)
    chosen = tasks[idx]
    stdscr.clear()
    due_str = select_date_screen(stdscr)
    if not due_str:
        draw_popup(stdscr, "Canceled date selection.")
        return
    chosen["due_date"] = due_str.strip()
    save_tasks(tasks)
    draw_popup(stdscr, f"Due date for Task {chosen['id']} set to {due_str}!")

def selectable_tasks_view(stdscr):
    tasks = load_tasks()
    if not tasks:
        display_tasks_screen(stdscr, tasks, "No tasks available.")
        return
    header = ["ID", "Title", "Dur", "Pri", "Due"]
    col_w = [5, 22, 5, 5, 10]
    data = [header]
    for t in tasks:
        ttl = t["title"]
        if t.get("completed", False):
            ttl = "[Done] " + ttl
        data.append([
            str(t["id"]),
            ttl,
            str(t.get("duration", 60)),
            str(t.get("priority", 1)),
            t.get("due_date", "")
        ])
    n_rows = len(data)
    n_cols = len(data[0])
    sel_row, sel_col = 0, 1
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        title_str = "Task List (Selectable Grid) - arrow=move; e=edit; d=delete; space=toggle; ?=help; q=quit"
        try:
            stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
            stdscr.addnstr(0, 0, title_str, w - 1)
            stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        except curses.error:
            pass

        # Draw headers
        for c in range(n_cols):
            x = 2 + sum(col_w[:c]) + 3 * c
            try:
                if sel_row == 0 and sel_col == c:
                    stdscr.attron(curses.color_pair(6))
                    stdscr.addnstr(2, x, data[0][c].ljust(col_w[c]), col_w[c])
                    stdscr.attroff(curses.color_pair(6))
                else:
                    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                    stdscr.addnstr(2, x, data[0][c].ljust(col_w[c]), col_w[c])
                    stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            except curses.error:
                pass

        # Separator
        try:
            stdscr.attron(curses.color_pair(5))
            stdscr.addnstr(3, 2, "-" * (sum(col_w) + 3 * (n_cols - 1)), w - 3)
            stdscr.attroff(curses.color_pair(5))
        except curses.error:
            pass

        # Draw data rows
        for r in range(1, n_rows):
            y_pos = 4 + (r - 1)
            x_pos = 2
            for c in range(n_cols):
                cell = data[r][c]
                disp = cell if len(cell) <= col_w[c] else cell[:col_w[c] - 3] + "..."
                try:
                    if r == sel_row and c == sel_col:
                        stdscr.attron(curses.color_pair(6))
                        stdscr.addnstr(y_pos, x_pos, disp.ljust(col_w[c]), col_w[c])
                        stdscr.attroff(curses.color_pair(6))
                    else:
                        stdscr.attron(curses.color_pair(5))
                        stdscr.addnstr(y_pos, x_pos, disp.ljust(col_w[c]), col_w[c])
                        stdscr.attroff(curses.color_pair(5))
                except curses.error:
                    pass
                x_pos += col_w[c] + 3
        update_status_bar(stdscr)
        stdscr.refresh()
        
        k = stdscr.getch()
        if k in [ord('q'), 27]:
            break
        elif k in [curses.KEY_UP, ord('k')]:
            if sel_row > 0:
                sel_row -= 1
        elif k in [curses.KEY_DOWN, ord('j')]:
            if sel_row < n_rows - 1:
                sel_row += 1
        elif k in [curses.KEY_LEFT, ord('h')]:
            if sel_col > 0:
                sel_col -= 1
        elif k in [curses.KEY_RIGHT, ord('l')]:
            if sel_col < n_cols - 1:
                sel_col += 1
        elif k in [10, 13]:
            if sel_row == 0:
                # Sort tasks by the column selected
                if sel_col == 0:
                    tasks = sorted(tasks, key=lambda x: int(x.get("id", 0)))
                elif sel_col == 1:
                    tasks = sorted(tasks, key=lambda x: x.get("title", "").lower())
                elif sel_col == 2:
                    tasks = sorted(tasks, key=lambda x: int(x.get("duration", 60)))
                elif sel_col == 3:
                    tasks = sorted(tasks, key=lambda x: int(x.get("priority", 1)))
                elif sel_col == 4:
                    tasks = sorted(tasks, key=lambda x: x.get("due_date", ""))
                data = [header]
                for t in tasks:
                    ttl = t["title"]
                    if t.get("completed", False):
                        ttl = "[Done] " + ttl
                    data.append([
                        str(t["id"]),
                        ttl,
                        str(t.get("duration", 60)),
                        str(t.get("priority", 1)),
                        t.get("due_date", "")
                    ])
                n_rows = len(data)
                sel_row, sel_col = 0, 1
            else:
                if sel_col == 1:
                    content = data[sel_row][sel_col] or "[empty]"
                    draw_popup(stdscr, content)
        elif k == ord(' '):
            if sel_row > 0:
                task_id = int(data[sel_row][0])
                toggle_task_completion(task_id)
                tasks = load_tasks()
                data = [header]
                for t in tasks:
                    ttl = t["title"]
                    if t.get("completed", False):
                        ttl = "[Done] " + ttl
                    data.append([
                        str(t["id"]),
                        ttl,
                        str(t.get("duration", 60)),
                        str(t.get("priority", 1)),
                        t.get("due_date", "")
                    ])
                n_rows = len(data)
        elif k == ord('e'):
            if sel_row > 0:
                task_id = int(data[sel_row][0])
                chosen = None
                for t in tasks:
                    if t["id"] == task_id:
                        chosen = t
                        break
                if chosen:
                    stdscr.clear()
                    try:
                        stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                        stdscr.addnstr(0, 0, "Direct Edit Task:", w - 1)
                        stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
                    except curses.error:
                        pass
                    try:
                        stdscr.attron(curses.color_pair(5))
                        stdscr.addnstr(1, 0, f"(Current Title: {chosen['title']})", w - 1)
                        stdscr.attroff(curses.color_pair(5))
                    except curses.error:
                        pass
                    hh, ww = stdscr.getmaxyx()
                    tw = ww - 4
                    new_title = edit_field(stdscr, 2, 0, tw, chosen["title"])
                    try:
                        stdscr.addnstr(4, 0, f"(Duration e.g.80: {chosen.get('duration', 60)})", w - 1, curses.color_pair(5))
                    except curses.error:
                        pass
                    new_dur = edit_field(stdscr, 5, 0, 10, str(chosen.get("duration", 60)))
                    try:
                        stdscr.addnstr(7, 0, f"(Priority (1=highest), e.g.3: {chosen.get('priority', 1)})", w - 1, curses.color_pair(5))
                    except curses.error:
                        pass
                    new_pri = edit_field(stdscr, 8, 0, 10, str(chosen.get("priority", 1)))
                    update_task(chosen["id"], new_title, new_dur, new_pri)
                    try:
                        stdscr.addnstr(10, 0, "Task updated. Press any key...", w - 1, curses.color_pair(2))
                    except curses.error:
                        pass
                    stdscr.refresh()
                    stdscr.getch()
                    tasks = load_tasks()
                    data = [header]
                    for t in tasks:
                        ttl = t["title"]
                        if t.get("completed", False):
                            ttl = "[Done] " + ttl
                        data.append([
                            str(t["id"]),
                            ttl,
                            str(t.get("duration", 60)),
                            str(t.get("priority", 1)),
                            t.get("due_date", "")
                        ])
                    n_rows = len(data)
        elif k == ord('d'):
            if sel_row > 0:
                task_id = int(data[sel_row][0])
                delete_task(task_id)
                tasks = load_tasks()
                data = [header]
                for t in tasks:
                    ttl = t["title"]
                    if t.get("completed", False):
                        ttl = "[Done] " + ttl
                    data.append([
                        str(t["id"]),
                        ttl,
                        str(t.get("duration", 60)),
                        str(t.get("priority", 1)),
                        t.get("due_date", "")
                    ])
                n_rows = len(data)
                sel_row = max(1, sel_row - 1)
        elif k == ord('?'):
            help_screen(stdscr)
        sel_row = max(0, min(sel_row, n_rows - 1))
        sel_col = max(0, min(sel_col, n_cols - 1))
        update_status_bar(stdscr)


def manage_tasks_menu(stdscr):
    while True:
        opts = [
            "View All Tasks",
            "Add New Tasks",
            "Edit Task",
            "Delete Task",
            "Export Tasks",
            "Import Tasks",
            "Add Due Date",
            "Import Plaintext",
            "Backup to GitHub",
            "Import from GitHub",
            "Help",
            "Back to Main Menu"
        ]
        sel = selectable_menu(stdscr, "Manage Tasks", opts, start_row=1)
        if sel == "View All Tasks":
            selectable_tasks_view(stdscr)
        elif sel == "Add New Tasks":
            add_tasks_screen(stdscr)
        elif sel == "Edit Task":
            edit_tasks_screen(stdscr)
        elif sel == "Delete Task":
            delete_tasks_screen(stdscr)
        elif sel == "Export Tasks":
            export_tasks_to_csv(stdscr)
        elif sel == "Import Tasks":
            import_tasks_from_csv(stdscr)
        elif sel == "Add Due Date":
            add_due_date_to_task_screen(stdscr)
        elif sel == "Import Plaintext":
            import_plaintext_file(stdscr)
        elif sel == "Backup to GitHub":
            messages = backup_to_github()
            draw_popup(stdscr, "\n".join(messages))
        elif sel == "Import from GitHub":
            messages = import_from_github()
            draw_popup(stdscr, "\n".join(messages))
        elif sel == "Help":
            help_screen(stdscr)
        elif sel == "Back to Main Menu":
            break

def main(stdscr):
    curses.curs_set(0)
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)
    while True:
        main_opts = ["View Tasks", "Manage Tasks", "Help", "Exit"]
        choice = selectable_menu(stdscr, "TOsk - A Task Planner Menu", main_opts, start_row=1)
        if choice == "View Tasks":
            sub = ["View Tasks (Selectable Grid)", "Back to Main Menu"]
            while True:
                sc = selectable_menu(stdscr, "View Tasks", sub, start_row=1)
                if sc == "View Tasks (Selectable Grid)":
                    selectable_tasks_view(stdscr)
                elif sc == "Back to Main Menu":
                    break
        elif choice == "Manage Tasks":
            manage_tasks_menu(stdscr)
        elif choice == "Help":
            help_screen(stdscr)
        elif choice == "Exit":
            break

if __name__ == "__main__":
    prompt_for_config()
    show_splash()
    curses.wrapper(main)
