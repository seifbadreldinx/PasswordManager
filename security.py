import math
import string

common_passwords = [
    "123456", "password", "123456789",
    "admin", "12345678", "abc123"
]


def calculate_entropy(password):
    pool = 0

    if any(c.islower() for c in password):
        pool += 26
    if any(c.isupper() for c in password):
        pool += 26
    if any(c.isdigit() for c in password):
        pool += 10
    if any(c in string.punctuation for c in password):
        pool += 32

    if pool == 0:
        return 0

    return round(len(password) * math.log2(pool), 2)


def entropy_level(entropy):
    if entropy < 40:
        return "Weak"
    elif entropy < 70:
        return "Medium"
    return "Strong"


def check_strength(password):
    score = 0
    alerts = []

    if password.lower() in common_passwords:
        return "Weak", "Common password"

    if len(password) < 8:
        alerts.append("Too short")
    else:
        score += 1

    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in string.punctuation for c in password):
        score += 1

    if score <= 2:
        return "Weak", ", ".join(alerts) or "Weak password"
    elif score <= 4:
        return "Medium", "Could be stronger"
    return "Strong", "Good password"