# 📜 CHANGELOG

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
