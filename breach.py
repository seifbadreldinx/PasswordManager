def check_breach(password):
    try:
        with open("breached.txt", "r") as f:
            leaked_passwords = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return False

    return password.strip() in leaked_passwords