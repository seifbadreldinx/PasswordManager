import secrets
import string


def generate_password(length=12, strength="strong"):
    letters = string.ascii_letters
    digits = string.digits
    symbols = "!@#$%^&*"

    if strength == "weak":
        chars = letters

    elif strength == "medium":
        chars = letters + digits

    else:  # strong
        chars = letters + digits + symbols

    password = []

    # 🔐 ensure complexity rules
    if strength == "strong":
        password.append(secrets.choice(symbols))
        password.append(secrets.choice(digits))
        password.append(secrets.choice(letters))

        # fill remaining length
        password += [secrets.choice(chars) for _ in range(length - 3)]

        # cryptographically secure shuffle (Fisher-Yates)
        for i in range(len(password) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password[i], password[j] = password[j], password[i]

        return ''.join(password)

    elif strength == "medium":
        password.append(secrets.choice(digits))
        password += [secrets.choice(chars) for _ in range(length - 1)]

        for i in range(len(password) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password[i], password[j] = password[j], password[i]

        return ''.join(password)

    else:
        return ''.join(secrets.choice(chars) for _ in range(length))