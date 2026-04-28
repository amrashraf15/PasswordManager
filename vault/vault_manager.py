import json

import vault
from vault.storage import (
    create_user_dir,
    get_vault_path,
    read_json,
    write_json,
    file_exists,
    validate_username,
    get_public_key_path,
    get_private_key_path,
)
from crypto.elgamal import initialize_user_keys
from crypto.hash_helper import sha256
from crypto.aes_helper import encrypt_data, decrypt_data
from vault.signer import sign_vault_data, verify_vault_data


#  helpers
def decrypt_credentials(vault:dict , master_password:str) -> list[dict]:
    key = sha256(master_password)
    try:
        return decrypt_data(key,vault)
    except Exception:
        raise  ValueError("Invalid master password ")

def encrypt_credentials(credentials: list[dict], master_password: str) ->dict:
    key = sha256(master_password)
    return encrypt_data(key,credentials)

def empty_vault(username: str) -> dict:
    return {
        "owner": username,
        "ciphertext": "",
        "nonce": "",
        "tag": "",
        "signature": None,
    }


def load_vault(username: str) -> dict:
    path = get_vault_path(username)
    if not file_exists(path):
        raise FileNotFoundError("Vault does not exist. Initialize user first.")
    return read_json(path)


def save_vault(username: str, vault: dict):
    write_json(get_vault_path(username), vault)


def find_index(credentials: list[dict], site: str) -> int:
    for i, cred in enumerate(credentials):
        if cred["site"] == site:
            return i
    return -1






# Initialize User
def initialize_user(username: str, master_password: str):
    validate_username(username)
    create_user_dir(username)
    private_key_path = get_private_key_path(username)
    public_key_path = get_public_key_path(username)
    initialize_user_keys(private_key_path, public_key_path)
    initialize_empty_vault(username, master_password)


def initialize_empty_vault(username: str,master_password: str):
    path = get_vault_path(username)

    if file_exists(path):
        return
    vault = empty_vault(username)
    encrypted_vault = encrypt_credentials([], master_password)
    vault["ciphertext"] = encrypted_vault["ciphertext"]
    vault["nonce"] = encrypted_vault["nonce"]
    vault["tag"] = encrypted_vault["tag"]
    write_json(path, vault)


def add_credential(username: str, master_password: str,site: str, login_identifier: str, password: str):
    vault = load_vault(username)
    credentials = decrypt_credentials(vault, master_password)

    idx = find_index(credentials, site)

    new_entry = {
        "site": site,
        "login_identifier": login_identifier,
        "password": password
    }

    if idx == -1:
        credentials.append(new_entry)
    else:
        credentials[idx] = new_entry
    
    encrypted = encrypt_credentials(credentials, master_password)
    vault["ciphertext"] = encrypted["ciphertext"]
    vault["nonce"] = encrypted["nonce"]
    vault["tag"] = encrypted["tag"]

    vault = sign_vault_data(vault, get_private_key_path(username))
    save_vault(username, vault)


def get_credential(username: str,master_password: str, site: str):
    vault = load_vault(username)

    # Verify signature on encrypted vault content before decryption
    if not verify_vault_data(vault, get_public_key_path(username)):
        raise ValueError("Vault signature is invalid! The vault may have been tampered with.")
    credentials = decrypt_credentials(vault, master_password)

    idx = find_index(credentials, site)
    if idx == -1:
        return None

    return credentials[idx]



def update_credential(username: str, master_password: str, site: str, new_login_identifier: str, new_password: str):
    vault = load_vault(username)
    credentials = decrypt_credentials(vault, master_password)

    idx = find_index(credentials, site)
    if idx == -1:
        raise ValueError("Credential not found")

    credentials[idx] = {
        "site": site,
        "login_identifier": new_login_identifier,
        "password": new_password
    }

    encrypted = encrypt_credentials(credentials, master_password)
    vault["ciphertext"] = encrypted["ciphertext"]
    vault["nonce"] = encrypted["nonce"]
    vault["tag"] = encrypted["tag"]

    vault = sign_vault_data(vault, get_private_key_path(username))
    save_vault(username, vault)



def delete_credential(username: str, master_password: str, site: str):
    vault = load_vault(username)
    credentials = decrypt_credentials(vault, master_password)

    idx = find_index(credentials, site)
    if idx == -1:
        raise ValueError("Credential not found")

    credentials.pop(idx)
    encrypted = encrypt_credentials(credentials, master_password)
    vault["ciphertext"] = encrypted["ciphertext"]
    vault["nonce"] = encrypted["nonce"]
    vault["tag"] = encrypted["tag"]
    vault = sign_vault_data(vault, get_private_key_path(username))
    save_vault(username, vault)