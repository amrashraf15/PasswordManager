from pathlib import Path
import json
import re

from config import (
    USERS_DIR,
    VAULT_FILE_NAME,
    PRIVATE_KEY_FILE_NAME,
    PUBLIC_KEY_FILE_NAME,
)


def validate_username(username: str) -> None:
    if not username or not username.strip():
        raise ValueError("Username cannot be empty.")

    if not re.fullmatch(r"[A-Za-z0-9_-]+", username):
        raise ValueError("Username can only contain letters, numbers, underscores, and hyphens.")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict) -> None:
    ensure_dir(path.parent)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def file_exists(path: Path) -> bool:
    return path.exists()


def get_user_dir(username: str) -> Path:
    validate_username(username)
    return USERS_DIR / username


def create_user_dir(username: str) -> Path:
    user_dir = get_user_dir(username)
    ensure_dir(user_dir)
    return user_dir


def get_vault_path(username: str) -> Path:
    return get_user_dir(username) / VAULT_FILE_NAME


def get_private_key_path(username: str) -> Path:
    return get_user_dir(username) / PRIVATE_KEY_FILE_NAME


def get_public_key_path(username: str) -> Path:
    return get_user_dir(username) / PUBLIC_KEY_FILE_NAME