============================================================
             🚀 TOsk GitHub Backup Setup Instructions
============================================================

1. 🔑 Configure Your GitHub Credentials:
   • When you run TOsk for the first time, you'll be prompted to enter:
       – **GitHub Token**: Your personal access token for GitHub.
       – **GitHub Owner**: Your GitHub username or organization name.
       – **GitHub Repository**: The name of your private backup repository (e.g., tosk-backups).
   • These values are encrypted and stored in the file `config.json` using your master configuration password.

2. 🔐 Set Your Encryption Passphrase:
   • When prompted, enter your Encryption Passphrase.
   • This passphrase encrypts your task data before it’s uploaded to GitHub.
   • On future runs, you only need to enter your master configuration password to load your secure settings.

3. 💾 Back Up Your Tasks to GitHub:
   • From the TOsk main menu, select **"Manage Tasks"**.
   • Then choose **"Backup to GitHub"**.
   • TOsk will encrypt (if an encryption passphrase is set) and upload your tasks (e.g., tasks.json and tasks_export.csv) to your private GitHub repository.
   • All communication with GitHub is handled over HTTPS.

4. 🔄 Import Your Tasks from GitHub:
   • To restore your tasks, choose **"Import from GitHub"** from the Manage Tasks submenu.
   • The application downloads and decrypts your tasks locally using your provided encryption passphrase.

5. ⚡ Security Highlights:
   • **No Credentials in Code**: Your GitHub token, owner, and repo are never hard-coded.
   • **Encrypted Configuration**: Your sensitive configuration is stored securely in an encrypted file.
   • **HTTPS Communication**: All interactions with GitHub are securely transmitted over HTTPS.

============================================================
