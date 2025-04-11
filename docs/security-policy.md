# Security

  🔐 End-to-End Encryption
    Your tasks are secured using AES‑GCM encryption. When you back up your files to GitHub, TOsk encrypts your task data using a key derived from your personal encryption passphrase (via PBKDF2HMAC). This ensures that only someone with the correct passphrase can decrypt the files. When you import tasks, the files are automatically decrypted on your local machine, so your data remains protected at every step.

  🔑 Encrypted Configuration
    TOsk stores your critical configuration details—such as your GitHub Token, GitHub Owner, GitHub Repository, and Encryption Passphrase—in a configuration file (config.json). This file is itself encrypted using your chosen master configuration password. Even if someone gains access to this file, they won’t be able to read your sensitive information without the master password.

  📡 Secure Communication
    All interactions with GitHub are performed over HTTPS. This guarantees that your data is securely transmitted, protecting it from eavesdropping or man‑in‑the‑middle attacks.

  ⚡ Transient Environment Variables
    After loading your configuration, TOsk sets the sensitive values as environment variables for the duration of your session only. This minimizes the risk of long‑term exposure of your credentials.

In summary, TOsk leverages robust encryption, secure storage, and secure network communications to ensure your task data and configuration are well-protected—from local storage to cloud backup on GitHub.
