import base64
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256


def derive_key(master_password, salt):
    return PBKDF2(
        master_password,
        salt,
        dkLen=32,
        count=150000,
        hmac_hash_module=SHA256
    )


def encrypt_text(master_password, plain_text):
    salt = get_random_bytes(16)
    key = derive_key(master_password, salt)

    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plain_text.encode())

    data = salt + cipher.nonce + tag + ciphertext
    return base64.b64encode(data).decode()


def decrypt_text(master_password, encrypted_text):
    try:
        raw = base64.b64decode(encrypted_text)

        salt = raw[:16]
        nonce = raw[16:32]
        tag = raw[32:48]
        ciphertext = raw[48:]

        key = derive_key(master_password, salt)

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        text = cipher.decrypt_and_verify(ciphertext, tag)

        return text.decode()

    except Exception:
        return None