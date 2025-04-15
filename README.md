# 📂 TOsk — A Terminal Task Planner

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen)

`TOsk` is a terminal-based task planner built with `curses` in Python. It features a splash screen, grid-based task UI, CSV import/export, due dates, history logs, and more — all inside a beautiful fullscreen TUI.

> 📦 For users who just want it to work without setup, a prebuilt binary is available under [Prebuilt Binary (Linux Only)](#-prebuilt-binary-linux-only).

---

## ✅ Requirements

### For End Users
- No special requirements!
- 📂 Just [download TOsk for Linux](https://github.com/ctsdownloads/tosk-task-manager/releases/latest) and make it executable (chmod +x tosk-linux-x86_64 , then run it.
- 📦 Rather [install it](#-installation) as tosk in your terminal?

### For Development
- Python 3.8+
- `python3-venv`
- [PyInstaller](https://pyinstaller.org/)
- Static Linux build of [`viu`](https://github.com/atanunq/viu)

---

## ✨ Features

- 📋 **Grid-based Task Manager**: Scrollable, sortable, real-time editable grid.
- ✅ **Task Completion Tracking**: Toggle with space bar.
- ⌛ **Estimated Duration Support**: Helps plan your day. Enter an estimated duration for each task to help plan your day and manage your workload.
- 🎯 **Priority System**: Focus on what matters most. Assign priority levels to tasks to focus on what matters most. Browse to the top of app page, select PRI, enter to sort.
- 📅 **Due Date Picker**: Asign due dates. Set a due date  on a selected task, select due dates using full-screen calendar widgets.
- 🧮 **Built-in Status Bar**: Always visible summary showing task count and completion status.
- 📂 **CSV Import/Export**: Backup or transfer tasks.
- 📝 **Plaintext Task Import**: Use this format or even by creating a task within the app itself:
  ```
  Task sentence::duration::priority::YYYY-MM-DD
  ```
  Example:
  ```
  Fix bug::30::1::2025-04-15
  ```
  If only a task name is given, defaults apply.
- 🔄 **Sortable Headers**: Sort by clicking headers.
- 📷 **Splash Screen Support**: Terminal image with `viu`.
- 🎨 **Colorized UI**: Themed, bold visuals.
- 🔐 **Encrypted Configuration**: Securely store sensitive configuration data (e.g., GitHub Token, Encryption Passphrase, GitHub Owner, and GitHub Repository) in an encrypted file (config.json), ensuring your credentials remain protected.
- 💾 **GitHub Backup & Import**: [See guide](#-how-to-set-up-a-github-personal-access-token)
- 🔒 **Secure Communication**: All interactions with GitHub are transmitted over HTTPS for data security.
- 🔄 **Offline Capability**: Core functionality works without an internet connection.
- 🐧 **Linux Native**: Optimized for Linux terminal environments (e.g., GNOME Terminal, xterm, etc.).

---

## 📚 Additional Documentation

- [🔄 Backup How‑To Guide](docs/backup-howto.md)  
- [🔒 [Security Policy](docs/security-policy.md#security-and-token-access-explained)

---

## 🔑 How to Set Up a GitHub Personal Access Token

1. Visit: [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **"Generate new token" → "Fine-grained token"**
3. Name it (e.g. `TOsk Backup Token`)
4. Choose your repo scope (e.g. `tosk-backups`)
5. Permissions:
   - **Contents → Read and write**
6. Generate token and copy it.
7. Paste into TOsk when prompted.

> 💡 Stored in `config.json`, encrypted with your master password.

---

## 📘 Changelog

Check out what’s new: [CHANGELOG ➜](./CHANGELOG.md)

---

## 🚀 Build Instructions (Linux Only)

<details>
<summary><strong>Expand for full build steps</strong></summary>

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install python3-venv curl tar

# Set up project directory
mkdir -p ~/ncurses_TOsk_app/bin
cd ~/ncurses_TOsk_app

# Download and extract viu
curl -L https://github.com/atanunq/viu/releases/latest/download/viu-x86_64-unknown-linux-musl.tar.gz -o /tmp/viu.tar.gz
mkdir -p /tmp/viu-install
tar -xzf /tmp/viu.tar.gz -C /tmp/viu-install
cp /tmp/viu-install/bin/viu bin/
chmod +x bin/viu

# Clone repo or add main.py, tosk.jpg

# Setup virtual env
python3 -m venv ~/pyenv
source ~/pyenv/bin/activate
pip install pyinstaller

# Patch main.py
# def resource_path(relative_path):
#     import sys, os
#     if hasattr(sys, '_MEIPASS'):
#         return os.path.join(sys._MEIPASS, relative_path)
#     return os.path.join(os.path.abspath("."), relative_path)
# Replace all static paths to viu and tosk.jpg with resource_path(...)

# Build
pyinstaller --onefile \
  --add-data "bin/viu:bin" \
  --add-data "tosk.jpg:." \
  main.py

# Rename and run
mv dist/main dist/tosk
chmod +x dist/tosk
./dist/tosk

# Deactivate
deactivate
```

</details>

---

## 🧰 What the Build Process Does

- Creates a `venv`
- Downloads and embeds `viu`
- Uses PyInstaller to bundle:
  - All code
  - Splash image
  - `viu` binary
- Outputs single-file executable `tosk`

---

## 🗼 Screenshots

> 📸  
![Splash](https://raw.githubusercontent.com/ctsdownloads/tosk-task-manager/refs/heads/main/images/tosk1.png)  
![Main Menu](https://raw.githubusercontent.com/ctsdownloads/tosk-task-manager/refs/heads/main/images/tosk2.png)  
![Task Grid](https://raw.githubusercontent.com/ctsdownloads/tosk-task-manager/refs/heads/main/images/tosk3.png)  
![Due Date Year](https://raw.githubusercontent.com/ctsdownloads/tosk-task-manager/refs/heads/main/images/tosk4.png)  
![Due Date Month](https://raw.githubusercontent.com/ctsdownloads/tosk-task-manager/refs/heads/main/images/tosk5.png)  
![Due Date Day](https://raw.githubusercontent.com/ctsdownloads/tosk-task-manager/refs/heads/main/images/tosk6.png)

---

### 📥 Installation

1. Download from [Releases](https://github.com/ctsdownloads/tosk-task-manager/releases/latest)
2. Make it executable:
   ```bash
   chmod +x tosk-linux-x86_64
   ```
3. Run it:
   ```bash
   ./tosk-linux-x86_64
   ```

Or install it permanently:
```bash
mkdir -p ~/.local/bin && cp tosk-linux-x86_64 ~/.local/bin/tosk && chmod +x ~/.local/bin/tosk
```

## 🗑️ Uninstallation

To remove TOsk if it is installed:

```bash
rm ~/.local/bin/tosk
```

Optionally, remove the downloaded binary:

```bash
rm ~/tosk-linux-x86_64
```

---

### ⚠️ Notes

- Requires Linux (64-bit)
- Includes statically built `viu` for splash
- Terminal must support image previews (Kitty, iTerm2, etc.)

---

## 🙈 How to Disable the Splash Screen

### 🛠 Option 1: Quick & Safe

1. Open `tosk.py`
2. Scroll to the bottom
3. Find:
   ```
   show_splash()
   ```
4. Comment it out:
   ```
   # show_splash()
   ```

---

### ⚙️ Option 2: Make It Configurable

1. Replace:
   ```
   show_splash()
   ```
   With:
   ```python
   config = prompt_for_config()
   if not config.get("DISABLE_SPLASH", False):
       show_splash()
   ```

2. Edit your `config.json`:
   ```json
   {
     "DISABLE_SPLASH": true
   }
   ```

3. Binary users should [build from source](#-build-instructions-linux-only) to enable this option.

---

## ❗ Note on Splash Rendering

- Requires statically compiled `viu`
- Not distributed in this repo
- Download and include via build guide above

---

## 📜 Acknowledgments

- Splash support uses [`viu`](https://github.com/atanunq/viu) by [Tanuj Sinha](https://github.com/atanunq)  
- MIT Licensed — see [LICENSE.viu](./LICENSE.viu)
