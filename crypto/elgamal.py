from vault.storage import read_json, write_json
from config import ELGAMAL_PARAMS_FILE
from crypto.math_utils import mod_exp, random_int, is_prime, is_primitive_root


def validate_elgamal_params(p:int ,alpha:int) -> None:
    if not is_prime(p):
        raise ValueError("Elgamal Parameter (p) must be prime")
    if not is_primitive_root(alpha,p):
        raise ValueError("ElGamal parameter alpha must be a primitive root modulo p.")

 # load params from json file
def load_elgamal_params() -> dict:
    data = read_json(ELGAMAL_PARAMS_FILE)
    if "p" not in data or "alpha" not in data:
        raise ValueError(" ElGamal Parameters must contain 'p' and 'alpha'")
    p = int(data["p"])
    alpha = int(data["alpha"])
    validate_elgamal_params(p,alpha)
    return {
        "p": p,
        "alpha":alpha,
    }

# public and private key generation
def generate_private_key(p:int) -> int:
    return random_int(2,p-2)

def generate_public_key(p:int,alpha:int,private_key:int) -> int:
    return mod_exp(alpha,private_key,p) 

# keypair generation

def generate_keypair() ->tuple[dict,dict]:
    params = load_elgamal_params()
    p = params["p"]
    alpha = params["alpha"]
    x = generate_private_key(p)
    y = generate_public_key(p,alpha,x)

    private_key_data = {
        "p":p,
        "alpha": alpha,
        "x": x,
    }
    public_key_data = {
        "p": p,
        "alpha": alpha,
        "y": y,
    }

    return private_key_data, public_key_data

# save keys
def save_private_key(path, private_key_data: dict) -> None:
    write_json(path, private_key_data)

def save_public_key(path, public_key_data: dict) -> None:
    write_json(path, public_key_data)

# load keys
def load_private_key(path) -> dict:
    data = read_json(path)
    if "p" not in data or "alpha" not in data or "x" not in data:
        raise ValueError(" ElGamal Private key must contain 'p' and 'alpha' and 'x'")

    return data

def load_public_key(path) -> dict:
    data = read_json(path)
    if "p" not in data or "alpha" not in data or "y" not in data:
        raise ValueError(" ElGamal Public key must contain 'p' and 'alpha' and 'y'")
    
    return data


def initialize_user_keys(private_key_path, public_key_path) -> None:
    if private_key_path.exists() and public_key_path.exists():
        return

    private_key_data, public_key_data = generate_keypair()
    save_private_key(private_key_path, private_key_data)
    save_public_key(public_key_path, public_key_data)

