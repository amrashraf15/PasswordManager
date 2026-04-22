from pathlib import Path

import pytest

import vault.vault_manager as vm


@pytest.fixture
def temp_user_env(tmp_path, monkeypatch):
    """
    Redirect vault/key paths to a temporary folder so tests do not touch real data.
    """
    base_dir = tmp_path / "data"
    users_dir = base_dir / "users"
    users_dir.mkdir(parents=True, exist_ok=True)

    def fake_get_user_dir(username: str) -> Path:
        return users_dir / username

    def fake_get_vault_path(username: str) -> Path:
        return fake_get_user_dir(username) / "vault.json"

    def fake_get_private_key_path(username: str) -> Path:
        return fake_get_user_dir(username) / "private_key.json"

    def fake_get_public_key_path(username: str) -> Path:
        return fake_get_user_dir(username) / "public_key.json"

    monkeypatch.setattr(vm, "get_vault_path", fake_get_vault_path)
    monkeypatch.setattr(vm, "get_private_key_path", fake_get_private_key_path)
    monkeypatch.setattr(vm, "get_public_key_path", fake_get_public_key_path)

    return {
        "base_dir": base_dir,
        "users_dir": users_dir,
        "username": "amr",
        "master_password": "123456",
    }


@pytest.fixture
def initialized_user(temp_user_env):
    username = temp_user_env["username"]
    master_password = temp_user_env["master_password"]
    vm.initialize_user(username, master_password)
    return temp_user_env


def read_vault_file(username: str) -> dict:
    return vm.load_vault(username)


def test_initialize_user_creates_user_keys_and_encrypted_empty_vault(initialized_user):
    username = initialized_user["username"]

    vault_path = vm.get_vault_path(username)
    private_key_path = vm.get_private_key_path(username)
    public_key_path = vm.get_public_key_path(username)

    assert vault_path.exists()
    assert private_key_path.exists()
    assert public_key_path.exists()

    vault_data = vm.load_vault(username)

    assert vault_data["owner"] == username
    assert vault_data["ciphertext"] != ""
    assert vault_data["nonce"] != ""
    assert vault_data["tag"] != ""
    assert vault_data["signature"] is None

    creds = vm.decrypt_credentials(vault_data, initialized_user["master_password"])
    assert creds == []


def test_add_credential_stores_and_returns_data(initialized_user):
    username = initialized_user["username"]
    master_password = initialized_user["master_password"]

    vm.add_credential(username, master_password, "facebook", "amr123", "pass123")

    cred = vm.get_credential(username, master_password, "facebook")

    assert cred is not None
    assert cred["site"] == "facebook"
    assert cred["login_identifier"] == "amr123"
    assert cred["password"] == "pass123"


def test_get_missing_credential_returns_none(initialized_user):
    username = initialized_user["username"]
    master_password = initialized_user["master_password"]

    cred = vm.get_credential(username, master_password, "nonexistent")

    assert cred is None


def test_add_same_site_overwrites_existing_credential(initialized_user):
    username = initialized_user["username"]
    master_password = initialized_user["master_password"]

    vm.add_credential(username, master_password, "facebook", "old_user", "old_pass")
    vm.add_credential(username, master_password, "facebook", "new_user", "new_pass")

    cred = vm.get_credential(username, master_password, "facebook")

    assert cred == {
        "site": "facebook",
        "login_identifier": "new_user",
        "password": "new_pass",
    }

    vault_data = vm.load_vault(username)
    creds = vm.decrypt_credentials(vault_data, master_password)
    assert len(creds) == 1


def test_update_existing_credential(initialized_user):
    username = initialized_user["username"]
    master_password = initialized_user["master_password"]

    vm.add_credential(username, master_password, "facebook", "amr123", "pass123")
    vm.update_credential(username, master_password, "facebook", "amr999", "pass999")

    cred = vm.get_credential(username, master_password, "facebook")

    assert cred == {
        "site": "facebook",
        "login_identifier": "amr999",
        "password": "pass999",
    }


def test_update_missing_credential_raises_value_error(initialized_user):
    username = initialized_user["username"]
    master_password = initialized_user["master_password"]

    with pytest.raises(ValueError, match="Credential not found"):
        vm.update_credential(username, master_password, "facebook", "user", "pass")


def test_delete_existing_credential(initialized_user):
    username = initialized_user["username"]
    master_password = initialized_user["master_password"]

    vm.add_credential(username, master_password, "facebook", "amr123", "pass123")
    vm.delete_credential(username, master_password, "facebook")

    cred = vm.get_credential(username, master_password, "facebook")
    assert cred is None

    vault_data = vm.load_vault(username)
    creds = vm.decrypt_credentials(vault_data, master_password)
    assert creds == []


def test_delete_missing_credential_raises_value_error(initialized_user):
    username = initialized_user["username"]
    master_password = initialized_user["master_password"]

    with pytest.raises(ValueError, match="Credential not found"):
        vm.delete_credential(username, master_password, "facebook")


def test_wrong_master_password_raises_value_error(initialized_user):
    username = initialized_user["username"]
    correct_password = initialized_user["master_password"]

    vm.add_credential(username, correct_password, "facebook", "amr123", "pass123")

    with pytest.raises(ValueError, match="Invalid master password"):
        vm.get_credential(username, "wrong_password", "facebook")


def test_vault_file_does_not_store_plaintext(initialized_user):
    username = initialized_user["username"]
    master_password = initialized_user["master_password"]

    vm.add_credential(username, master_password, "facebook", "amr123", "super_secret_password")

    vault_path = vm.get_vault_path(username)
    raw_text = vault_path.read_text(encoding="utf-8")

    assert "facebook" not in raw_text
    assert "amr123" not in raw_text
    assert "super_secret_password" not in raw_text


def test_load_vault_for_missing_user_raises_file_not_found():
    with pytest.raises(FileNotFoundError, match="Vault does not exist"):
        vm.load_vault("missing_user")


def test_find_index_returns_correct_index():
    credentials = [
        {"site": "google", "login_identifier": "u1", "password": "p1"},
        {"site": "facebook", "login_identifier": "u2", "password": "p2"},
    ]

    assert vm.find_index(credentials, "google") == 0
    assert vm.find_index(credentials, "facebook") == 1
    assert vm.find_index(credentials, "twitter") == -1


def test_initialize_user_twice_does_not_break_existing_vault(initialized_user):
    username = initialized_user["username"]
    master_password = initialized_user["master_password"]

    vm.add_credential(username, master_password, "facebook", "amr123", "pass123")

    # Calling initialize_user again should not wipe existing vault
    vm.initialize_user(username, master_password)

    cred = vm.get_credential(username, master_password, "facebook")
    assert cred is not None
    assert cred["login_identifier"] == "amr123"