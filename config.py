from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
USERS_DIR = DATA_DIR / "users"
SHARED_DIR = DATA_DIR / "shared"

ELGAMAL_PARAMS_FILE = SHARED_DIR / "elgamal_params.json"
DH_PARAMS_FILE = SHARED_DIR / "dh_params.json"

VAULT_FILE_NAME = "vault.json"
PRIVATE_KEY_FILE_NAME = "private_key.json"
PUBLIC_KEY_FILE_NAME = "public_key.json"
