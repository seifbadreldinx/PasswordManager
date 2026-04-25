import json
import os

FILE = "auth.json"


def set_master_password(password):
    data = {"master_password": password}

    with open(FILE, "w") as f:
        json.dump(data, f)


def get_master_password():
    if not os.path.exists(FILE):
        return None

    with open(FILE, "r") as f:
        data = json.load(f)

    return data.get("master_password")