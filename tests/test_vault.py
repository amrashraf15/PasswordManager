import pytest

import vault.storage as storage
import vault.vault_manager as vault_manager


@pytest.fixture
def temp_users_dir(tmp_path, monkeypatch):
    """
    Redirect USERS_DIR inside storage.py to a temporary folder,
    so vault_manager uses a safe test location.
    """
    fake_users_dir = tmp_path / "users"
    monkeypatch.setattr(storage, "USERS_DIR", fake_users_dir)
    return fake_users_dir


def test_initialize_user_creates_user_directory_and_vault(temp_users_dir):
    username = "bob"

    vault_manager.initialize_user(username)

    user_dir = storage.get_user_dir(username)
    vault_path = storage.get_vault_path(username)

    assert user_dir.exists()
    assert user_dir.is_dir()
    assert vault_path.exists()

    vault = storage.read_json(vault_path)
    assert vault["owner"] == username
    assert vault["ciphertext"] == ""
    assert vault["nonce"] == ""
    assert vault["tag"] == ""
    assert vault["signature"] is None
    assert vault["meta"]["version"] == 1
    assert vault["dev_plain_credentials"] == []


def test_add_credential_stores_new_credential(temp_users_dir):
    username = "bob"
    vault_manager.initialize_user(username)

    vault_manager.add_credential(
        username=username,
        site="github.com",
        login="bob_git",
        password="secret123",
    )

    cred = vault_manager.get_credential(username, "github.com")

    assert cred is not None
    assert cred["site"] == "github.com"
    assert cred["login"] == "bob_git"
    assert cred["password"] == "secret123"


def test_get_credential_returns_none_when_site_not_found(temp_users_dir):
    username = "bob"
    vault_manager.initialize_user(username)

    cred = vault_manager.get_credential(username, "missing.com")

    assert cred is None


def test_add_credential_overwrites_existing_site(temp_users_dir):
    username = "bob"
    vault_manager.initialize_user(username)

    vault_manager.add_credential(username, "github.com", "old_login", "old_pass")
    vault_manager.add_credential(username, "github.com", "new_login", "new_pass")

    cred = vault_manager.get_credential(username, "github.com")

    assert cred is not None
    assert cred["login"] == "new_login"
    assert cred["password"] == "new_pass"

    vault = vault_manager.load_vault(username)
    assert len(vault["dev_plain_credentials"]) == 1


def test_update_credential_updates_existing_entry(temp_users_dir):
    username = "bob"
    vault_manager.initialize_user(username)

    vault_manager.add_credential(username, "github.com", "bob_git", "old_pass")
    vault_manager.update_credential(username, "github.com", "bob_new", "new_pass")

    cred = vault_manager.get_credential(username, "github.com")

    assert cred is not None
    assert cred["site"] == "github.com"
    assert cred["login"] == "bob_new"
    assert cred["password"] == "new_pass"


def test_update_credential_raises_for_missing_site(temp_users_dir):
    username = "bob"
    vault_manager.initialize_user(username)

    with pytest.raises(ValueError, match="Credential not found"):
        vault_manager.update_credential(username, "missing.com", "x", "y")


def test_delete_credential_removes_existing_entry(temp_users_dir):
    username = "bob"
    vault_manager.initialize_user(username)

    vault_manager.add_credential(username, "github.com", "bob_git", "secret123")
    assert vault_manager.get_credential(username, "github.com") is not None

    vault_manager.delete_credential(username, "github.com")

    assert vault_manager.get_credential(username, "github.com") is None


def test_delete_credential_raises_for_missing_site(temp_users_dir):
    username = "bob"
    vault_manager.initialize_user(username)

    with pytest.raises(ValueError, match="Credential not found"):
        vault_manager.delete_credential(username, "missing.com")