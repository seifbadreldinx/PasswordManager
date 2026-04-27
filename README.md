# 🔐 Secure Password Manager with End-to-End Encryption

## 📌 Project Overview
This project is a Secure Password Manager desktop application built using Python and PyQt5.  
It allows users to securely store, generate, and manage passwords with strong encryption and security features.

---

## ⚠ Problem Statement
Users often reuse weak passwords across multiple websites, making them vulnerable to data breaches and credential theft.  
There is a need for a secure system that generates, stores, and manages passwords safely without exposing them.

---

## 💡 Solution
A local desktop application that:
- Stores passwords securely using encryption (AES-256-GCM)
- Generates strong random passwords
- Checks password strength and leakage
- Prevents reuse of weak or compromised passwords
- Organizes passwords into categories

---

## 🔐 Zero-Knowledge Architecture
This system follows a zero-knowledge security model:

- The master password is NEVER stored anywhere.
- It is used only to derive an encryption key using PBKDF2.
- All passwords are encrypted before storage using AES-256-GCM.
- Decryption happens only locally on the device.
- Even database access does not expose plaintext data.

---

## 🔒 Encryption & Key Derivation
All passwords are protected using:

- AES-256-GCM encryption for confidentiality and integrity
- PBKDF2 key derivation function to generate a secure encryption key from the master password
- Salt + multiple iterations to resist brute-force attacks

This ensures that even if the database is leaked, passwords remain unreadable without the master password.

---

## 🔒 Security Note
Even if the database is exposed, all passwords remain encrypted and unreadable without the master password.

---

## 🧠 Key Features
✔ AES-256-GCM Encryption  
✔ PBKDF2 Key Derivation  
✔ Password Generator (weak / medium / strong)  
✔ Password Strength Checker  
✔ Password Entropy Analysis  
✔ Breach Detection (offline check)  
✔ Password Reuse Detection  
✔ Categories (Social / Banking / Work / Other)  
✔ Secure Clipboard Auto-Clear (10 seconds)  
✔ Dark / Light Theme Toggle (on every window)  
✔ Password Masking (show / hide toggle)  
✔ Live Strength & Entropy Indicator while typing  
✔ Delete with Confirmation Dialog  

---

## � UI Overview

### Login Window
- Centered card layout — stays clean and centred at any window size
- Dark / Light theme toggle pinned to the top-right corner
- Enter key submits the password
- Red border flash on wrong password

### Main Vault Window
- Two-column layout: **form panel** (fixed width, left) + **expanding vault table** (right)
- Live strength & entropy indicator updates as you type a password
- Passwords displayed as `••••••••` by default; **Show Passwords** button reveals them
- **Copy Password** copies the selected entry and auto-clears clipboard after 10 seconds
- **Delete Selected** requires confirmation before removing an entry
- Dark / Light theme toggle in the top bar

---


Password entropy measures how random and secure a password is.

- Low entropy → Weak password  
- Medium entropy → Moderate security  
- High entropy → Strong password  

Higher entropy means better protection against attacks.

---

## 🛠 Technologies Used
- Python  
- PyQt5 (GUI)  
- SQLite (Database)  
- PyCryptodome (AES Encryption)  
- PBKDF2 (Key Derivation)  
- Pyperclip (Clipboard handling)  

---

## ▶ How to Run

### Prerequisites
- Python 3.8 or higher

### 1. Clone the repository
```bash
git clone https://github.com/seifbadreldinx/PasswordManager.git
cd PasswordManager
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the application
```bash
python login.py
```

---

## 📖 Usage Guide

### First Launch — Create a Master Password
On the first run, a styled **Create Vault** dialog appears immediately (before the login window).  
Enter your new master password in both fields — they must match before the vault is created.  
This password is hashed with PBKDF2 (150,000 iterations) and **never stored in plaintext**.  
After creation, the **login window** appears — enter your new password to unlock the vault.  
> ⚠ If you forget your master password, your vault cannot be recovered.

### Saving a Password
1. Enter the **Site**, **Username**, and **Password** fields
2. Select a **Category** (Social, Banking, Work, Other)
3. Choose **Strength** and **Length** for generation (optional)
4. Click **Save Password**

The app will:
- Check if the password has appeared in breach databases
- Warn if you are reusing a password across sites
- Display the entropy score and strength rating

### Generating a Password
1. Set desired **Length** (6–32 characters) and **Strength** level
2. Click **Generate Password** — the password fills the field and copies to clipboard
3. Clipboard is automatically cleared after **10 seconds**

### Deleting a Password
1. Click any row in the password table to select it
2. Click **Delete Selected**
3. Confirm the deletion in the dialog

### Breach Detection
The app checks passwords against `breached.txt` — an offline list of known leaked passwords.  
To update the breach list, replace or append entries to `breached.txt` (one password per line).

---

## 📁 Project Structure

| File | Purpose |
|---|---|
| `login.py` | Entry point — master password setup & login window |
| `auth.py` | PBKDF2 hashing and verification of master password |
| `gui.py` | Main PyQt5 vault interface (two-column layout, theme toggle) |
| `database.py` | SQLite vault — encrypted CRUD operations |
| `crypto.py` | AES-256-GCM encrypt/decrypt with PBKDF2 key derivation |
| `generator.py` | Cryptographically secure password generation (`secrets` module) |
| `security.py` | Strength scoring and entropy calculation |
| `breach.py` | Offline breach database checker |
| `breached.txt` | Offline list of 50+ known leaked passwords |
| `requirements.txt` | Python dependencies |
| `pyrightconfig.json` | Pylance/Pyright config (suppresses PyQt5 import warnings) |

---