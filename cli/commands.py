from vault.vault_manager import (
    initialize_user,
    add_credential,
    get_credential,
    update_credential,
    delete_credential,
)
from vault.signer import verify_user_vault
from exchange.exporter import secure_export_vault




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
        print("Credintal Not found.")
    else:
        print("\n=== Credential ===")
        print(f"Site: {cred['site']}")
        print(f"Login Identifier: {cred['login_identifier']}")
        print(f"Password: {cred['password']}")


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



def handle_verify_vault():
    username = input("Username: ")
    try:
        valid = verify_user_vault(username)
        if valid:
            print("Vault signature is valid.")
        else:
            print("Vault signature is invalid!")
    except FileNotFoundError:
        print("User vault does not exist.")
    except Exception as e:
        print(f"Error: {e}")


def handle_export_vault():
    sender = input("Sender Username: ")
    sender_pwd = input("Sender Master Password: ")
    recipient = input("Recipient Username: ")
    recipient_pwd = input("Recipient Master Password: ")

    try:
        secure_export_vault(sender, sender_pwd, recipient, recipient_pwd)
        print(f"Vault exported successfully from {sender} to {recipient}.")
    except Exception as e:
        print(f"Export failed: {e}")


def handle_import_vault():
    print("Not implemented yet")