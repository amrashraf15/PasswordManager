import json
from crypto.dh import load_dh_params, generate_dh_keypair, compute_shared_secret, derive_session_key
from vault.signer import sign_message, verify_signature, sign_vault_data, verify_vault_data
from vault.storage import get_private_key_path, get_public_key_path
from vault.vault_manager import decrypt_credentials, encrypt_credentials, load_vault, save_vault
from crypto.aes_helper import encrypt_data, decrypt_data

def secure_export_vault(sender_username: str, sender_pwd: str, recipient_username: str, recipient_pwd: str):

    dh_params = load_dh_params()
    q = dh_params["q"]
    alpha = dh_params["alpha"]
    
    sender_priv = get_private_key_path(sender_username)
    sender_pub = get_public_key_path(sender_username)
    
    recipient_priv = get_private_key_path(recipient_username)
    recipient_pub = get_public_key_path(recipient_username)
    
    # Exchange DH public keys
    sender_dh_priv, sender_dh_pub = generate_dh_keypair(q, alpha)
    sender_dh_sig = sign_message(str(sender_dh_pub), sender_priv)
    
    if not verify_signature(str(sender_dh_pub), sender_dh_sig, sender_pub):
        raise ValueError("Key Exchange Aborted: Recipient failed to verify Sender's DH public key signature.")
        
    recipient_dh_priv, recipient_dh_pub = generate_dh_keypair(q, alpha)
    recipient_dh_sig = sign_message(str(recipient_dh_pub), recipient_priv)
    
    if not verify_signature(str(recipient_dh_pub), recipient_dh_sig, recipient_pub):
        raise ValueError("Key Exchange Aborted: Sender failed to verify Recipient's DH public key signature.")
        
    sender_shared_secret = compute_shared_secret(recipient_dh_pub, sender_dh_priv, q)
    recipient_shared_secret = compute_shared_secret(sender_dh_pub, recipient_dh_priv, q)
    
    if sender_shared_secret != recipient_shared_secret:
        raise ValueError("Shared secrets do not match!")
        
    session_key = derive_session_key(sender_shared_secret)
    
    # Transfer Phase
    sender_vault = load_vault(sender_username)
    if not verify_vault_data(sender_vault, sender_pub):
        raise ValueError("Sender vault signature is invalid!")
    credentials = decrypt_credentials(sender_vault, sender_pwd)
    
    encrypted_transfer_data = encrypt_data(session_key, credentials)
    
    transfer_payload = {
        "ciphertext": encrypted_transfer_data["ciphertext"],
        "nonce": encrypted_transfer_data["nonce"],
        "tag": encrypted_transfer_data["tag"]
    }
    transfer_payload_signed = sign_vault_data(transfer_payload, sender_priv)
    
    # Import Phase
    if not verify_vault_data(transfer_payload_signed, sender_pub):
        raise ValueError("Import Aborted: Signature verification failed on transfer payload.")
        
    decrypted_credentials = decrypt_data(session_key, transfer_payload_signed)
    
    recipient_encrypted = encrypt_credentials(decrypted_credentials, recipient_pwd)
    
    recipient_vault = load_vault(recipient_username)
    recipient_vault["ciphertext"] = recipient_encrypted["ciphertext"]
    recipient_vault["nonce"] = recipient_encrypted["nonce"]
    recipient_vault["tag"] = recipient_encrypted["tag"]
    
    recipient_vault_signed = sign_vault_data(recipient_vault, recipient_priv)
    
    save_vault(recipient_username, recipient_vault_signed)
    return True
