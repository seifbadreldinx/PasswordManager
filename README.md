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
✔ Secure Clipboard Auto-Clear  

---

## 📊 Password Entropy
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

### 1. Install requirements:
```bash
pip install pyqt5 pycryptodome pyperclip"

2. Run the application:
python login.py