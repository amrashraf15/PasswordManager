from Crypto.Cipher import AES
import base64
import json




# Encrypt Each credential list using AES-GCM. Returns dict with ciphertext, nonce, tag.
def encrypt_data(key: bytes, data: list[dict]) -> dict:

    # Convert Python object to bytes
    plaintext = json.dumps(data).encode("utf-8")

    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    return {
        "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
        "nonce": base64.b64encode(cipher.nonce).decode("utf-8"),
        "tag": base64.b64encode(tag).decode("utf-8"),
    }



# Decrypt AES-GCM vault data and return credential list.
def decrypt_data(key: bytes, vault: dict) -> list[dict]:

    ciphertext = base64.b64decode(vault["ciphertext"])
    nonce = base64.b64decode(vault["nonce"])
    tag = base64.b64decode(vault["tag"])

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    plaintext = cipher.decrypt_and_verify(ciphertext, tag)

    return json.loads(plaintext.decode("utf-8"))