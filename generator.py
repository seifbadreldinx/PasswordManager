import random
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
        password.append(random.choice(symbols))
        password.append(random.choice(digits))
        password.append(random.choice(letters))

        # fill remaining length
        password += [random.choice(chars) for _ in range(length - 3)]

        random.shuffle(password)
        return ''.join(password)

    elif strength == "medium":
        password.append(random.choice(digits))
        password += [random.choice(chars) for _ in range(length - 1)]
        random.shuffle(password)
        return ''.join(password)

    else:
        return ''.join(random.choice(chars) for _ in range(length))