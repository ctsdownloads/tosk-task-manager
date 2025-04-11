# 📂 TOsk — A Terminal Task Planner

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen)

`TOsk` is a terminal-based task planner built with `curses` in Python. It features a splash screen, grid-based task UI, CSV import/export, due dates, history logs, and more — all inside a beautiful fullscreen TUI. 

> 🔪 For users who just want it to work without setup, a prebuilt binary is available under [Releases](#-prebuilt-binary-linux-only).
### 📦 [Download TOsk for Linux](https://github.com/ctsdownloads/tosk-task-manager/releases/latest)

---

## 📥 Installation

### Quick Install (once downloaded to your home directory)

If you've already downloaded the `tosk-linux-x86_64` binary to your home directory, run this one-liner to set it up as the `tosk` command:

```bash
mkdir -p ~/.local/bin && cp ~/tosk-linux-x86_64 ~/.local/bin/tosk && chmod +x ~/.local/bin/tosk && if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc; fi && source ~/.bashrc && echo -e "\n✅ Tosk installed successfully! Type 'tosk' to get started."
```
---

## 🗑️ Uninstallation

To remove Tosk from your system:

```bash
# Remove the binary
rm ~/.local/bin/tosk
```

# Optional: Remove the downloaded binary if you still have it
```
rm ~/tosk-linux-x86_64
```

- Optional: If you don't have any other programs in ~/.local/bin
- you can remove the directory and PATH addition
- rm -rf ~/.local/bin
---

## ✅ Requirements

### For End Users
* No special requirements! The binary will run on most Linux distros
* Just 📦 [download TOsk for Linux](https://github.com/ctsdownloads/tosk-task-manager/releases/latest), and [run this command](https://github.com/ctsdownloads/tosk-task-manager/tree/main?tab=readme-ov-file#-tosk--a-terminal-task-planner)

### For Development
- Python 3.8+
- `python3-venv`
- [PyInstaller](https://pyinstaller.org/)
- Static Linux build of [`viu`](https://github.com/atanunq/viu)
- Will run on most Linux distros!


---

## ✨ Features

- 📋 **Grid-based Task Manager**: View and edit tasks in a scrollable, sortable grid. Add new tasks in real time directly within the app.  
- ✅ **Task Completion Tracking**: Easily toggle tasks as complete/incomplete with the space bar.  
- ⌛ **Estimated Duration Support**: Enter an estimated duration for each task to help plan your day and manage your workload.  
- 🎯 **Priority System**: Assign priority levels to tasks to focus on what matters most.  
- 📅 **Due Date Picker**: Select due dates using full-screen calendar widgets.  
- 🧮 **Built-in Status Bar**: Always visible summary showing task count and completion status.  
- 📂 **CSV Import/Export**: Seamlessly back up or transfer tasks to/from CSV files.  
- 📝 **Plaintext Task Import**: Load tasks from simple `.txt` lists using the format:  
  ```
  Task sentence::duration::priority::YYYY-MM-DD`
  ```  
  For example:
  ```  
  Review pull request::30::2::2025-04-15
  Fix bug in main.py::60::1::2025-04-16
  Draft release notes::45::3::2025-04-18
  ``` 
  If only a task title is given, default values are used: duration `60`, priority `1`, and no due date.
   
- 🔄 **Sortable Headers**: Click headers to sort the task list by various criteria.  
- 📷 **Splash Screen Support**: Enjoy a terminal-rendered splash image on launch using `viu`.  
- 🎨 **Colorized UI**: Bold, themed visuals provide a clean, distraction-free interface.  
- 🔐 **Encrypted Configuration Management**: Securely store sensitive configuration data (e.g., GitHub Token, Encryption Passphrase, GitHub Owner, and GitHub Repository) in an encrypted file (`config.json`), ensuring your credentials remain protected.  
- 💾 **GitHub Backup & Import**: [Automatically encrypt and upload your tasks](https://github.com/ctsdownloads/tosk-task-manager/blob/main/README.md#-how-to-set-up-a-github-personal-access-token) (e.g., `tasks.json` and `tasks_export.csv`) to your private GitHub repository and seamlessly import them when needed.  
- 🔒 **Secure Communication**: All interactions with GitHub are transmitted over HTTPS for data security.  
- 🔄 **Offline Capability**: Core functionality works without an internet connection.  
- 🐧 **Linux Native**: Optimized for Linux terminal environments (e.g., GNOME Terminal, xterm, etc.).


---

---

## 📚 Additional Documentation

For detailed instructions on how to configure GitHub backups and secure your data, please refer to the following guides:

- [🔄 Backup How‑To Guide](docs/backup-howto.md)  
  Learn how to set up and use the GitHub backup functionality to securely upload your task files.

- [🔒 Security Policy](docs/security-policy.md)  
  Read about the security measures implemented in TOsk, including encrypted configuration and secure communication.

---

### 🔑 How to Set Up a GitHub Personal Access Token

To enable GitHub backup and restore features, you must create a Personal Access Token:

1. Visit [https://github.com/settings/tokens](https://github.com/settings/tokens).
2. Click **"Generate new token"** → **"Fine-grained token"**.
3. Give it a name (e.g. `TOsk Backup Token`) and expiration date.
4. Select the repository scope where you will store your backups (e.g. `tosk-backups`).
5. Grant the following permission:
 - **Contents → Read and write**
6. Click **Generate token**, then copy the token.
7. Paste this token into TOsk when prompted for `GitHub Token` on first launch.

> 💡 Your token is encrypted and stored locally in `config.json`, which is itself encrypted using a master password.

---

## 📘 Changelog

Want to see what’s new? Check out the full [CHANGELOG ➜](./CHANGELOG.md)


## 🚀 Build Instructions (Linux Only)

Clone the repo and follow these steps to build a fully self-contained binary:

<details>
<summary><strong>Expand for full build steps</strong></summary>

```bash
# 1. Install python3-venv if needed
sudo apt-get update
sudo apt-get install python3-venv curl tar

# 2. Set up your project directory
mkdir -p ~/ncurses_TOsk_app/bin
cd ~/ncurses_TOsk_app

# 3. Download the static Linux binary for 'viu'
curl -L https://github.com/atanunq/viu/releases/latest/download/viu-x86_64-unknown-linux-musl.tar.gz -o /tmp/viu.tar.gz
mkdir -p /tmp/viu-install
tar -xzf /tmp/viu.tar.gz -C /tmp/viu-install
cp /tmp/viu-install/bin/viu bin/
chmod +x bin/viu

# 4. Add the project files (or clone this repo)
# You should have:
# - main.py
# - tosk.jpg
# - bin/viu

# 5. Create and activate a virtual environment
python3 -m venv ~/pyenv
source ~/pyenv/bin/activate

# 6. Install PyInstaller inside the venv
pip install pyinstaller

# 7. Patch main.py to support PyInstaller (if not already done)
# Add this function near the top of main.py:
# def resource_path(relative_path):
#     import sys, os
#     if hasattr(sys, '_MEIPASS'):
#         return os.path.join(sys._MEIPASS, relative_path)
#     return os.path.join(os.path.abspath("."), relative_path)
#
# Replace:
# subprocess.call(["./bin/viu", "tosk.jpg"])
# With:
# subprocess.call([resource_path("bin/viu"), resource_path("tosk.jpg")])

# 8. Build it!
pyinstaller --onefile \
  --add-data "bin/viu:bin" \
  --add-data "tosk.jpg:." \
  main.py

# 9. Rename the output binary
mv dist/main dist/tosk
chmod +x dist/tosk

# 10. Run it
./dist/tosk

# 11. Deactivate the venv when done
deactivate
```

</details>

---

## 🧰 What the Build Process Does

- Sets up an isolated Python environment using `venv`.
- Downloads and embeds a statically built `viu` terminal image viewer.
- Uses PyInstaller to create a single-file executable that bundles:
  - All Python code
  - The `tosk.jpg` splash image
  - The `viu` binary for splash rendering
- Produces a portable `tosk` binary that runs without needing Python installed.

---

## 🗼 Screenshots

Here's what TOsk looks like in action:

> 📸
![Splashscreen with TOsk](https://raw.githubusercontent.com/ctsdownloads/tosk-task-manager/refs/heads/main/images/tosk1.png)

![Main TOsk Menu](https://raw.githubusercontent.com/ctsdownloads/tosk-task-manager/refs/heads/main/images/tosk2.png)

![Manage Tasks, with TOsk](https://raw.githubusercontent.com/ctsdownloads/tosk-task-manager/refs/heads/main/images/tosk3.png)

![Set due date year, with TOsk](https://raw.githubusercontent.com/ctsdownloads/tosk-task-manager/refs/heads/main/images/tosk4.png)

![Set due date month, with TOsk](https://raw.githubusercontent.com/ctsdownloads/tosk-task-manager/refs/heads/main/images/tosk5.png)

![Set due date day, with TOsk](https://raw.githubusercontent.com/ctsdownloads/tosk-task-manager/refs/heads/main/images/tosk6.png)




---

## 📆 Prebuilt Binary (Linux Only)

A precompiled binary is available for **Linux x86_64** systems. This allows you to run TOsk without installing Python or any dependencies.

### ✅ How to Use

1. **Download the binary** from the [Releases](#) section.
2. Make it executable:
   ```bash
   chmod +x tosk-linux-x86_64
   ```
3. Run it from the terminal:
   ```bash
   ./tosk-linux-x86_64
   ```
or...

>You can install it, make it executable and anything else you need by simply [clicking here](https://github.com/ctsdownloads/tosk-task-manager/tree/main?tab=readme-ov-file#-tosk--a-terminal-task-planner)

### ⚠️ Requirements & Notes

- This binary is intended for **Linux (64-bit)** systems.
- It includes a bundled copy of [`viu`](https://github.com/atanunq/viu) to display the splash screen.  
  > Note: This only works if your terminal supports image previews (e.g., iTerm2, Kitty, some Linux terminals).
- For full functionality:
  - Use a terminal window with enough size (80x24 or larger recommended).
  - A monospaced font will give the best experience.

### 🛠 If You Prefer Source
You can also [build from source](#-build-instructions-linux-only) or run the Python script directly if you prefer.

---

## 🙈 How to Disable the Splash Screen

While Sci-Fi fans may find the splash image of TOsk entertaining, others may prefer a faster startup experience or a cleaner launch. If you'd rather remove the image of the application's namesake, here's how to disable it:

1. Open `main.py` in a text editor.
2. Locate this line:
   ```python
   subprocess.call([resource_path("bin/viu"), resource_path("tosk.jpg")])
   ```
3. Replace it with:
   ```python
   pass  # Splash screen disabled
   ```

This will skip the splash entirely and launch straight into the planner. Once disabled, you can also safely delete the `tosk.jpg` image from the project folder if it's no longer needed.

---

## ❗ Note

This project requires a statically linked `viu` binary to render the splash image. The `viu` binary is **not distributed in this repository** by default. Please follow the build guide to include it manually.

---

## 📜 Acknowledgments

This project bundles a statically compiled version of [`viu`](https://github.com/atanunq/viu) by [Tanuj Sinha](https://github.com/atanunq) (MIT License) for the splash screen.

See [LICENSE.viu](./LICENSE.viu) for details.

