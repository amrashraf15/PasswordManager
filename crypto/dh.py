from vault.storage import read_json
from config import DH_PARAMS_FILE
from crypto.math_utils import mod_exp, random_int
from crypto.hash_helper import sha256

def load_dh_params() -> dict:
    data = read_json(DH_PARAMS_FILE)
    q = int(data["q"])
    alpha = int(data["alpha"])
    return {"q": q, "alpha": alpha}

def generate_dh_keypair(q: int, alpha: int) -> tuple[int, int]:
    private_key = random_int(2, q - 2)
    public_key = mod_exp(alpha, private_key, q)
    return private_key, public_key

def compute_shared_secret(public_key_other: int, private_key_self: int, q: int) -> int:
    return mod_exp(public_key_other, private_key_self, q)

def derive_session_key(shared_secret: int) -> bytes:
    return sha256(str(shared_secret))
