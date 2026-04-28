import copy
import json
from pathlib import Path
from typing import Union

from crypto.hash_helper import sha256
from vault.storage import (
    get_private_key_path,
    get_public_key_path,
    get_vault_path,
    read_json,
    write_json,
)
from crypto.elgamal import load_private_key, load_public_key
from crypto.math_utils import gcd, mod_exp, mod_inverse, random_int

KeyLike = Union[str, Path, dict]


def _load_private_key(key: KeyLike) -> dict:
    if isinstance(key, dict):
        return key
    return load_private_key(key)


def _load_public_key(key: KeyLike) -> dict:
    if isinstance(key, dict):
        return key
    return load_public_key(key)


def sign_message(message: str, private_key: KeyLike) -> dict:
    priv = _load_private_key(private_key)
    p = int(priv["p"])
    alpha = int(priv["alpha"])
    x = int(priv["x"])

    hash_bytes = sha256(message)
    message_hash = int.from_bytes(hash_bytes, "big") % (p - 1)

    while True:
        k = random_int(2, p - 2)
        if gcd(k, p - 1) == 1:
            break

    r = mod_exp(alpha, k, p)
    k_inv = mod_inverse(k, p - 1)
    s = (k_inv * (message_hash - x * r)) % (p - 1)

    return {"r": r, "s": s, "message_hash": message_hash}


def save_signature(path: Union[str, Path], signature: dict) -> None:
    write_json(path, signature)


def load_signature(path: Union[str, Path]) -> dict:
    return read_json(path)


def _serialize_vault_without_signature(vault: dict) -> str:
    vault_copy = {k: vault[k] for k in vault if k != "signature"}
    return json.dumps(vault_copy, sort_keys=True, separators=(",", ":"))


def vault_hash(vault: dict) -> str:
    serialized = _serialize_vault_without_signature(vault)
    return sha256(serialized).hex()


def sign_vault_data(vault: dict, private_key: KeyLike) -> dict:
    vault_copy = copy.deepcopy(vault)
    serialized = _serialize_vault_without_signature(vault_copy)
    signature = sign_message(serialized, private_key)
    vault_copy["signature"] = signature
    return vault_copy


def verify_signature(
    message_or_vault: Union[str, dict], signature: dict, public_key: KeyLike) -> bool:
    # Basic signature shape check
    if not isinstance(signature, dict) or "r" not in signature or "s" not in signature:
        return False

    pub = _load_public_key(public_key)
    try:
        p = int(pub["p"])
        alpha = int(pub["alpha"])
        y = int(pub["y"])
    except Exception:
        return False

    # Determine message hash
    if isinstance(message_or_vault, dict):
        serialized = _serialize_vault_without_signature(message_or_vault)
        message_hash = int.from_bytes(sha256(serialized), "big") % (p - 1)
    else:
        message_hash = int.from_bytes(sha256(str(message_or_vault)), "big") % (p - 1)

    r = signature.get("r")
    s = signature.get("s")

    if not isinstance(r, int) or not isinstance(s, int):
        return False

    if r <= 0 or r >= p:
        return False

    v1 = (mod_exp(y, r, p) * mod_exp(r, s, p)) % p
    v2 = mod_exp(alpha, message_hash, p)

    return v1 == v2


def verify_vault_data(vault: dict, public_key: KeyLike) -> bool:
    sig = vault.get("signature")
    if not sig:
        return False
    return verify_signature(vault, sig, public_key)


def sign_user_vault(username: str) -> dict:
    vault_path = get_vault_path(username)
    vault_data = read_json(vault_path)
    priv_path = get_private_key_path(username)
    signed = sign_vault_data(vault_data, priv_path)
    write_json(vault_path, signed)
    return signed["signature"]


def verify_user_vault(username: str) -> bool:
    vault_path = get_vault_path(username)
    vault_data = read_json(vault_path)
    pub_path = get_public_key_path(username)
    return verify_vault_data(vault_data, pub_path)
