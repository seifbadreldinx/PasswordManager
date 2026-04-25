import sqlite3
from crypto import encrypt_text, decrypt_text

MASTER_PASSWORD = "master123"


def connect():
    return sqlite3.connect("vault.db")


def create_table():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            category TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_password(site, username, password, category):
    conn = connect()
    cur = conn.cursor()

    encrypted = encrypt_text(MASTER_PASSWORD, password)

    cur.execute("""
        INSERT INTO passwords (site, username, password, category)
        VALUES (?, ?, ?, ?)
    """, (site, username, encrypted, category))

    conn.commit()
    conn.close()


def get_passwords():
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM passwords")
    rows = cur.fetchall()

    conn.close()

    data = []

    for row in rows:
        data.append((
            row[0],
            row[1],
            row[2],
            decrypt_text(MASTER_PASSWORD, row[3]),
            row[4]
        ))

    return data


def check_password_reuse(password):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT site, password FROM passwords")
    rows = cur.fetchall()

    conn.close()

    sites = []

    for site, enc_password in rows:
        try:
            if decrypt_text(MASTER_PASSWORD, enc_password) == password:
                sites.append(site)
        except:
            pass

    return (True, sites) if sites else (False, [])