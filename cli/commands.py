from vault.vault_manager import (
    initialize_user,
    add_credential,
    get_credential,
    update_credential,
    delete_credential,
)
from vault.signer import verify_user_vault
from exchange.exporter import run_sender, run_recipient


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
    result = verify_user_vault(username)
    if result:
        print("Vault signature is valid.")
    else:
        print("Vault signature is INVALID! The vault may have been tampered with.")

def handle_export_vault():
    username = input("Username: ")
    password = input("Master Password: ")
    port_str = input("Port (default 5555): ").strip()
    port = int(port_str) if port_str else 5555
    try:
        run_sender(username, password, port)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def handle_import_vault():
    username = input("Username: ")
    password = input("Master Password: ")
    host = input("Host (default localhost): ").strip() or "localhost"
    port_str = input("Port (default 5555): ").strip()
    port = int(port_str) if port_str else 5555
    try:
        run_recipient(username, password, host, port)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")