from vault.vault_manager import (
    initialize_user,
    add_credential,
    get_credential,
    update_credential,
    delete_credential,
)


def handle_init_user():
    username = input("Enter username: ")
    master_password = input("Enter Master Password: ")
    initialize_user(username,master_password)
    print("User initialized successfully.")


def handle_add_credential():
    try:
        username = input("Username: ")
        master_password = input("Enter Master Password: ")
        site = input("Site: ")
        login_identifier = input("Enter Login Identifier: ")
        password = input("Password: ")
        add_credential(username, master_password,site,login_identifier, password)
        print("Credential added.")
    except FileNotFoundError:
        print("User does not exist. Please initialize first.")
    except ValueError as e:
        print(f"Error: {e}")

    except Exception:
        print("Unexpected error occurred.")
    


def handle_get_credential():
    username = input("Username: ")
    master_password = input("Enter Master Password: ")
    site = input("Site: ")

    cred = get_credential(username, master_password, site)

    if not cred:
        print("Not found.")
    else:
        print(cred)


def handle_update_credential():
    username = input("Username: ")
    master_password = input("Enter Master Password: ")
    site = input("Site: ")
    login_identifier = input("Enter New login Identifier: ")
    password = input("New password: ")

    update_credential(username, master_password, site, login_identifier, password)
    print("Updated Sucessfully.")


def handle_delete_credential():
    username = input("Username: ")
    master_password = input("Enter Master Password: ")
    site = input("Site: ")

    delete_credential(username, master_password, site)
    print("Deleted successfully.")


# placeholders
def handle_verify_vault():
    print("Not implemented yet")


def handle_export_vault():
    print("Not implemented yet")


def handle_import_vault():
    print("Not implemented yet")