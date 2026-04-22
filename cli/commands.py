from vault.vault_manager import (
    initialize_user,
    add_credential,
    get_credential,
    update_credential,
    delete_credential,
)


def handle_init_user():
    username = input("Enter username: ")
    initialize_user(username)
    print("User initialized successfully.")


def handle_add_credential():
    username = input("Username: ")
    site = input("Site: ")
    login = input("Login: ")
    password = input("Password: ")

    add_credential(username, site, login, password)
    print("Credential added.")


def handle_get_credential():
    username = input("Username: ")
    site = input("Site: ")

    cred = get_credential(username, site)

    if not cred:
        print("Not found.")
    else:
        print(cred)


def handle_update_credential():
    username = input("Username: ")
    site = input("Site: ")
    login = input("New login: ")
    password = input("New password: ")

    update_credential(username, site, login, password)
    print("Updated.")


def handle_delete_credential():
    username = input("Username: ")
    site = input("Site: ")

    delete_credential(username, site)
    print("Deleted.")


# placeholders
def handle_verify_vault():
    print("Not implemented yet")


def handle_export_vault():
    print("Not implemented yet")


def handle_import_vault():
    print("Not implemented yet")