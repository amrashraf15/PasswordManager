import socket
import json

from crypto.dh import load_dh_params, generate_dh_keypair, compute_shared_secret, derive_session_key
from vault.signer import sign_message, verify_signature, sign_vault_data, verify_vault_data
from vault.storage import get_private_key_path, get_public_key_path
from vault.vault_manager import decrypt_credentials, encrypt_credentials, load_vault, save_vault
from crypto.aes_helper import encrypt_data, decrypt_data

DEFAULT_PORT = 5555


def send_json(sock, data):
    sock.sendall((json.dumps(data) + "\n").encode())


def recv_json(sock):
    buf = b""
    while not buf.endswith(b"\n"):
        buf += sock.recv(65536)
    return json.loads(buf.decode())


def run_sender(username, password, port=DEFAULT_PORT, on_status=print):
    dh_params = load_dh_params()
    q, alpha = dh_params["q"], dh_params["alpha"]
    priv_path = get_private_key_path(username)
    pub_path = get_public_key_path(username)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen(1)
    on_status(f"Waiting for recipient on port {port}...")

    conn, addr = server.accept()
    on_status(f"Recipient connected from {addr}")

    try:
        hello = recv_json(conn)
        recipient_username = hello["username"]
        on_status(f"Recipient: {recipient_username}")

        dh_priv, dh_pub = generate_dh_keypair(q, alpha)
        dh_sig = sign_message(str(dh_pub), priv_path)
        send_json(conn, {"username": username, "dh_pub": dh_pub, "signature": dh_sig})
        on_status("Sent signed DH public key")

        r_dh = recv_json(conn)
        if not verify_signature(str(r_dh["dh_pub"]), r_dh["signature"], get_public_key_path(recipient_username)):
            raise ValueError("Recipient DH key verification failed")
        on_status("Verified recipient DH key")

        session_key = derive_session_key(compute_shared_secret(r_dh["dh_pub"], dh_priv, q))
        on_status("Session key derived")

        vault = load_vault(username)
        if not verify_vault_data(vault, pub_path):
            raise ValueError("Local vault signature invalid")
        credentials = decrypt_credentials(vault, password)
        encrypted = encrypt_data(session_key, credentials)
        transfer = {"ciphertext": encrypted["ciphertext"], "nonce": encrypted["nonce"], "tag": encrypted["tag"]}
        signed_transfer = sign_vault_data(transfer, priv_path)
        send_json(conn, signed_transfer)
        on_status(f"Sent encrypted vault ({len(credentials)} credentials)")

        ack = recv_json(conn)
        if ack.get("status") == "success":
            on_status("Transfer complete!")
            return True
        return False
    finally:
        conn.close()
        server.close()


def run_recipient(username, password, host="localhost", port=DEFAULT_PORT, on_status=print):
    dh_params = load_dh_params()
    q, alpha = dh_params["q"], dh_params["alpha"]
    priv_path = get_private_key_path(username)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    on_status(f"Connected to sender at {host}:{port}")

    try:
        send_json(sock, {"username": username})

        s_dh = recv_json(sock)
        sender_username = s_dh["username"]
        on_status(f"Sender: {sender_username}")
        if not verify_signature(str(s_dh["dh_pub"]), s_dh["signature"], get_public_key_path(sender_username)):
            raise ValueError("Sender DH key verification failed")
        on_status("Verified sender DH key")

        dh_priv, dh_pub = generate_dh_keypair(q, alpha)
        dh_sig = sign_message(str(dh_pub), priv_path)
        send_json(sock, {"dh_pub": dh_pub, "signature": dh_sig})
        on_status("Sent signed DH public key")

        session_key = derive_session_key(compute_shared_secret(s_dh["dh_pub"], dh_priv, q))
        on_status("Session key derived")

        transfer = recv_json(sock)
        if not verify_vault_data(transfer, get_public_key_path(sender_username)):
            send_json(sock, {"status": "error"})
            raise ValueError("Transfer signature verification failed")
        on_status("Verified transfer signature")

        credentials = decrypt_data(session_key, transfer)
        on_status(f"Decrypted {len(credentials)} credential(s)")

        encrypted = encrypt_credentials(credentials, password)
        vault = load_vault(username)
        vault["ciphertext"] = encrypted["ciphertext"]
        vault["nonce"] = encrypted["nonce"]
        vault["tag"] = encrypted["tag"]
        signed_vault = sign_vault_data(vault, priv_path)
        save_vault(username, signed_vault)
        on_status("Vault saved and signed")

        send_json(sock, {"status": "success"})
        on_status("Transfer complete!")
        return True
    finally:
        sock.close()
