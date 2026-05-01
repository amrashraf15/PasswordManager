import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vault.vault_manager import initialize_user, add_credential, get_credential
from exchange.exporter import secure_export_vault
import shutil
from config import USERS_DIR

def setup_users():
    if os.path.exists(USERS_DIR):
        shutil.rmtree(USERS_DIR)
        
    # User 1 (Sender)
    initialize_user("alice", "alicepass")
    add_credential("alice", "alicepass", "example.com", "alice_ex", "p@ssword1")
    
    # User 2 (Recipient)
    initialize_user("bob", "bobpass")

def main():
    print("Setting up users...")
    setup_users()
    
    print("Alice's vault before export:")
    print(get_credential("alice", "alicepass", "example.com"))
    
    print("\nBob's vault before export (should be None):")
    print(get_credential("bob", "bobpass", "example.com"))
    
    print("\nStarting secure export...")
    success = secure_export_vault("alice", "alicepass", "bob", "bobpass")
    print(f"Export Success: {success}")
    
    print("\nBob's vault after export (should have Alice's credentials):")
    print(get_credential("bob", "bobpass", "example.com"))

if __name__ == "__main__":
    main()
