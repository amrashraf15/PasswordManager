import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pytest

import vault.signer as signer


@pytest.fixture
def keypair():
    private_key = {
        "p": 467,
        "alpha": 2,
        "x": 127,
    }
    public_key = {
        "p": 467,
        "alpha": 2,
        "y": pow(2, 127, 467),
    }

    return private_key, public_key


@pytest.fixture
def sample_vault():
    return {
        "owner": "amr",
        "ciphertext": "encrypted-data",
        "nonce": "nonce",
        "tag": "tag",
        "signature": None,
    }


def test_sign_vault_data_adds_valid_signature(sample_vault, keypair):
    private_key, public_key = keypair

    signed_vault = signer.sign_vault_data(sample_vault, private_key)

    assert signed_vault["signature"] is not None
    assert "r" in signed_vault["signature"]
    assert "s" in signed_vault["signature"]
    assert signer.verify_vault_data(signed_vault, public_key) is True


def test_signature_does_not_mutate_original_vault(sample_vault, keypair):
    private_key, _ = keypair

    signed_vault = signer.sign_vault_data(sample_vault, private_key)

    assert sample_vault["signature"] is None
    assert signed_vault["signature"] is not None


def test_verify_vault_data_rejects_tampered_vault(sample_vault, keypair):
    private_key, public_key = keypair
    signed_vault = signer.sign_vault_data(sample_vault, private_key)

    signed_vault["ciphertext"] = "changed-data"

    assert signer.verify_vault_data(signed_vault, public_key) is False


def test_verify_vault_data_rejects_missing_signature(sample_vault, keypair):
    _, public_key = keypair

    assert signer.verify_vault_data(sample_vault, public_key) is False


def test_vault_hash_ignores_signature_field(sample_vault):
    first_hash = signer.vault_hash(sample_vault)
    sample_vault["signature"] = {"r": 1, "s": 2}

    assert signer.vault_hash(sample_vault) == first_hash


def test_sign_and_verify_user_vault(tmp_path, monkeypatch, sample_vault, keypair):
    private_key, public_key = keypair
    username = "amr"
    user_dir = tmp_path / username
    user_dir.mkdir()

    vault_path = user_dir / "vault.json"
    private_key_path = user_dir / "private_key.json"
    public_key_path = user_dir / "public_key.json"

    write_json(vault_path, sample_vault)
    write_json(private_key_path, private_key)
    write_json(public_key_path, public_key)

    monkeypatch.setattr(signer, "get_vault_path", lambda name: vault_path)
    monkeypatch.setattr(signer, "get_private_key_path", lambda name: private_key_path)
    monkeypatch.setattr(signer, "get_public_key_path", lambda name: public_key_path)

    signature = signer.sign_user_vault(username)
    signed_vault = signer.read_json(vault_path)

    assert signature == signed_vault["signature"]
    assert signer.verify_user_vault(username) is True


def test_verify_signature_rejects_malformed_signature(sample_vault, keypair):
    _, public_key = keypair

    assert signer.verify_signature(sample_vault, {"r": 1}, public_key) is False


def write_json(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
