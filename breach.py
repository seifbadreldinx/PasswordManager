import hashlib


def check_breach(password):
    """
    Check whether a password appears in the offline breach database.
    Passwords are stored as SHA-1 hashes (HIBP format) so no plaintext
    credentials are ever kept on disk.
    """
    try:
        pwd_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        with open("breached.txt", "r") as f:
            for line in f:
                if line.strip().upper() == pwd_hash:
                    return True
        return False
    except FileNotFoundError:
        return False