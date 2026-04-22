import hashlib

# we hash data using sha256 

def sha256(data: str) -> bytes:
    data_bytes = data.encode()
    hash_object = hashlib.sha256(data_bytes)
    hash_result = hash_object.digest()
    return hash_result

