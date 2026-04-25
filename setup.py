from auth import set_master_password

password = input("Create Master Password: ")
set_master_password(password)

print("Master Password Set ✔")