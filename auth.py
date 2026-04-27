import json
import os
import base64
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256

FILE = "auth.json"


def set_master_password(password):
    """Hash the master password with PBKDF2 and store only the salt + hash."""
    salt = get_random_bytes(16)
    key = PBKDF2(password, salt, dkLen=32, count=150000, hmac_hash_module=SHA256)
    data = {
        "salt": base64.b64encode(salt).decode(),
        "hash": base64.b64encode(key).decode()
    }
    with open(FILE, "w") as f:
        json.dump(data, f)


def verify_master_password(password):
    """Verify a password against the stored PBKDF2 hash."""
    if not os.path.exists(FILE):
        return False
    with open(FILE, "r") as f:
        data = json.load(f)
    salt = base64.b64decode(data["salt"])
    stored_hash = base64.b64decode(data["hash"])
    derived = PBKDF2(password, salt, dkLen=32, count=150000, hmac_hash_module=SHA256)
    return derived == stored_hash


def is_setup():
    """Return True if a master password has already been configured."""
    return os.path.exists(FILE)