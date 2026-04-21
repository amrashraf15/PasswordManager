import hashlib

def sha256(data: str) -> bytes:
    return hashlib.sha256(data.encode()).digest()

