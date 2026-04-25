from database import create_table, insert_password, get_passwords
from generator import generate_password


def main():
    create_table()

    password = generate_password()
    print("Generated Password:", password)

    insert_password("facebook.com", "shrouk123", password)

    data = get_passwords()

    for row in data:
        print(row)


if __name__ == "__main__":
    main()