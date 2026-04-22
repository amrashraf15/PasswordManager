from pathlib import Path
import json

import pytest

import vault.storage as storage


@pytest.fixture
def temp_users_dir(tmp_path, monkeypatch):
    """
    Redirect USERS_DIR inside storage.py to a temporary folder,
    so tests never touch the real data/users directory.
    """
    fake_users_dir = tmp_path / "users"
    monkeypatch.setattr(storage, "USERS_DIR", fake_users_dir)
    return fake_users_dir


def test_validate_username_accepts_valid_names():
    valid_names = [
        "alice",
        "alice_123",
        "alice-123",
        "ALICE",
        "user_1-test",
    ]

    for username in valid_names:
        storage.validate_username(username)  # should not raise


def test_validate_username_rejects_empty_or_invalid_names():
    invalid_names = [
        "",
        "   ",
        "alice smith",
        "alice/smith",
        "alice@smith",
        "alice.smith",
        "ali$ce",
    ]

    for username in invalid_names:
        with pytest.raises(ValueError):
            storage.validate_username(username)


def test_create_user_dir_creates_directory(temp_users_dir):
    username = "alice"

    user_dir = storage.create_user_dir(username)

    assert user_dir == temp_users_dir / username
    assert user_dir.exists()
    assert user_dir.is_dir()


def test_get_vault_path_returns_correct_path(temp_users_dir):
    username = "alice"

    vault_path = storage.get_vault_path(username)

    expected = temp_users_dir / username / storage.VAULT_FILE_NAME
    assert vault_path == expected


def test_write_json_then_read_json(tmp_path):
    file_path = tmp_path / "sample" / "test.json"
    data = {
        "owner": "alice",
        "meta": {"version": 1},
        "items": [{"site": "github.com", "login": "alice"}],
    }

    storage.write_json(file_path, data)
    loaded = storage.read_json(file_path)

    assert file_path.exists()
    assert loaded == data


def test_read_json_raises_for_missing_file(tmp_path):
    missing_file = tmp_path / "does_not_exist.json"

    with pytest.raises(FileNotFoundError):
        storage.read_json(missing_file)