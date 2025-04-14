# 📜 CHANGELOG

# Changelog Update

All notable changes to this project will be documented in this file.

---
## Release Notes for v2.2 – 4-14-25

**v2.3 – 4-14-25**

New Features & Improvements

### Robust Error Handling in UI

- Modified curses UI functions to wrap addnstr calls in try/except blocks. This prevents crashes when strings overflow the terminal boundaries or when the window dimensions are too small. Users will now have a more stable experience when viewing or editing task lists, especially on environments with limited terminal sizes.

###  Improved GitHub API Interaction

- Enhanced URL safety in GitHub backup and import functions by adding proper URL encoding (using urllib.parse.quote) for repository file paths. This change ensures that any special characters or spaces in paths do not trigger Python errors during API calls.

### Enhanced Stability Post-Import

- Fixed an issue where importing tasks from GitHub could lead to terminal rendering errors when subsequently viewing the task list. The updated error handling ensures that the UI recovers gracefully after the data import process.

#### Refined Build Process on GitHub Actions

- Updated the GitHub Actions workflow to build the binary using a controlled Ubuntu environment with PyInstaller. This provides a more consistent release build that replicates the stable behavior seen in the original binary releases.

- The workflow includes steps to check out the repository, set up Python and its dependencies, build the binary with the correct data-inclusions, create a Git tag, and upload the binary as a new release.

### Bug Fixes

####Curses Error Fix

- Resolved the curses.error from `addnstr() returned ERR issue which was encountered locally after importing tasks from GitHub. This fix prevents unexpected crashes and improves overall UI resilience.

#### General UI Enhancements

- Minor adjustments to the task list display logic to ensure proper text alignment and truncation, reducing the likelihood of content overflow errors.


---

## Release Notes for v2.2 – 4-11-25

- **Configuration Management**
  - Added persistent, encrypted configuration support.
    - The application now stores required values (GitHub Token, Encryption Passphrase, GitHub Owner, GitHub Repository) in a file (`config.json`) encrypted using AES‑GCM.
    - On first run, users are prompted for these values and for a master configuration password to encrypt the config file.
    - On subsequent runs, users only need to enter the master configuration password to load the configuration.

- **Encryption and Decryption**
  - Integrated AES‑GCM‑based encryption for both file contents (tasks backups) and configuration data.
  - Updated encryption/decryption functions to handle both backup files and the configuration file.

- **GitHub Backup & Import**
  - Implemented GitHub backup functionality:
    - When backing up tasks (e.g., `tasks.json` and optionally `tasks_export.csv`), files are encrypted (if an encryption passphrase is provided), base64‑encoded, and uploaded to the specified GitHub repository under the `/backups/` directory.
  - Added GitHub import functionality:
    - On import, the application downloads the encrypted backup file from GitHub, decodes and decrypts it locally using the provided passphrase so that tasks are available as plain‑text JSON.

- **Help Section Update**
  - Completely refreshed the help screen to include up‑to‑date instructions for all application functions:
    - **General Controls:** Navigation with arrow keys or j/k/h/l; Enter to select; q or ESC to exit.
    - **Main Menu Options:** Descriptions for “View Tasks,” “Manage Tasks,” “Help,” and “Exit.”
    - **Manage Tasks Submenu:** Detailed explanations for all task management functions including adding, editing, deleting tasks; CSV import/export; calendar-based due date selection; plaintext import; GitHub backup and import.
    - **Calendar Controls:** Instructions for selecting month, day, and year.
    - **Configuration & Security:** Description of how configuration values are handled, encrypted, and stored, plus GitHub communication over HTTPS.
    - **GitHub Backup & Import:** Specific details on how backups are encrypted before upload and decrypted on import.

- **User Interface Improvements**
  - Consolidated and deduplicated all curses‑UI helper functions (menu selection, popups, calendar grids, etc.) ensuring that functions such as `selectable_menu` are defined only once and are in scope.
  - Updated the help screen and other UI elements to reflect the latest set of features and improvements.


---

## Release Notes for v2.1 – 2025-04-10

Changes

    Removed History Feature: Simplified the application by removing the history tracking functionality
    Improved overall performance and reduced memory usage
    Streamlined user experience with a more focused interface

Binary Information

    Built with PyInstaller for Linux x86_64
    Includes all necessary dependencies
    Compatible with previous data formats

This release focuses on simplification by removing the history feature, resulting in a more lightweight and focused application.

---

## Release Notes – 2025-04-10

Bug Fixes & Improvements

    Fixed workflow configuration for GitHub Actions release process
    Resolved permission issues for automated binary publishing
    Streamlined build and release pipeline
    Ironed out various deployment wrinkles

Binary Information

    Built with PyInstaller for Linux x86_64
    Includes all necessary dependencies
    Ready for production use

Thank you for your patience while we were ironing out some deployment issues. This release provides a stable binary that should work smoothly on Linux systems.

---

## [1.0.0] – 2025-04-10

### ✨ Added

- Initial public release of TOsk 🎉
- Fullscreen curses-based terminal UI
- Task viewing and editing in a sortable grid
- Add/edit/delete task functionality
- CSV import/export support
- Plaintext task import using format:
  ```
  Task sentence::duration::priority::YYYY-MM-DD
  ```
- Due date selector (with calendar picker)
- Priority and estimated duration fields
- Task completion toggles (with log tracking)
- History log file (`task_log.txt`)
- Splash screen with terminal-rendered image using `viu`
- Theme-colored UI elements
- Fully self-contained PyInstaller build system
- Linux x86_64 binary release with included `viu` binary

### 🛠 Changed

- N/A – This is the initial release.

### 🐞 Fixed

- N/A – No known issues in the initial release.

---

## [Unreleased]

- 🔜 Dark mode themes
- 🔜 Configurable color sets
- 🔜 Keyboard shortcut customization
- 🔜 Windows/macOS support
