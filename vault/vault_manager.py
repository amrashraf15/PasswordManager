from vault.storage import (
    create_user_dir,
    get_vault_path,
    read_json,
    write_json,
    file_exists,
    validate_username,
)



#  helpers

def empty_vault(username: str) -> dict:
    return {
        "owner": username,
        "ciphertext": "",
        "nonce": "",
        "tag": "",
        "signature": None,
        "meta": {"version": 1},
        "dev_plain_credentials": []
    }


def load_vault(username: str) -> dict:
    path = get_vault_path(username)
    if not file_exists(path):
        raise FileNotFoundError("Vault does not exist. Initialize user first.")
    return read_json(path)


def save_vault(username: str, vault: dict):
    write_json(get_vault_path(username), vault)


def find_index(vault: dict, site: str):
    for i, cred in enumerate(vault["dev_plain_credentials"]):
        if cred["site"] == site:
            return i
    return -1



# Initialize User
def initialize_user(username: str):
    validate_username(username)
    create_user_dir(username)
    initialize_empty_vault(username)


def initialize_empty_vault(username: str):
    path = get_vault_path(username)

    if file_exists(path):
        return

    vault = empty_vault(username)
    write_json(path, vault)


def add_credential(username: str, site: str, login: str, password: str):
    vault = load_vault(username)

    idx = find_index(vault, site)

    new_entry = {
        "site": site,
        "login": login,
        "password": password
    }

    if idx == -1:
        vault["dev_plain_credentials"].append(new_entry)
    else:
        vault["dev_plain_credentials"][idx] = new_entry  # overwrite

    save_vault(username, vault)


def get_credential(username: str, site: str):
    vault = load_vault(username)

    idx = find_index(vault, site)
    if idx == -1:
        return None

    return vault["dev_plain_credentials"][idx]



def update_credential(username: str, site: str, new_login: str, new_password: str):
    vault = load_vault(username)

    idx = find_index(vault, site)
    if idx == -1:
        raise ValueError("Credential not found")

    vault["dev_plain_credentials"][idx] = {
        "site": site,
        "login": new_login,
        "password": new_password
    }

    save_vault(username, vault)

    

def delete_credential(username: str, site: str):
    vault = load_vault(username)

    idx = find_index(vault, site)
    if idx == -1:
        raise ValueError("Credential not found")

    vault["dev_plain_credentials"].pop(idx)

    save_vault(username, vault)