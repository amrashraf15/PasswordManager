# Password Manager

A secure command-line password manager built in Python that combines modern cryptography with modular software design. The project supports encrypted password storage, ElGamal-based signing, Diffie–Hellman secure exchange, and AES-GCM encryption.

---

# Features

* Secure password vault encrypted with AES-GCM
* ElGamal public-key cryptography for digital signatures
* Diffie–Hellman key exchange for securely sharing vault data
* SHA-256 hashing utilities
* JSON-based storage for user keys and vault data
* Modular architecture for maintainability and testing
* Automated test suite for all cryptographic modules

---

# Project Structure

```text
password_manager/
│
├── app.py                  # CLI entry point
├── config.py               # Shared parameters, paths, constants
├── models.py               # Data classes and shared models
│
├── crypto/
│   ├── elgamal.py          # ElGamal encryption/signature algorithms
│   ├── dh.py               # Diffie-Hellman key exchange
│   ├── aes_helper.py       # AES-GCM wrapper
│   ├── hash_helper.py      # SHA-256 wrapper
│   └── math_utils.py       # Modular arithmetic and helper functions
│
├── vault/
│   ├── vault_manager.py    # Main vault logic
│   ├── storage.py          # Read/write JSON storage
│   └── signer.py           # ElGamal sign/verify functions
│
├── exchange/
│   └── exporter.py         # Secure vault export/import workflow
│
├── data/
│   ├── users/
│   │   └── alice/
│   │       ├── private_key.json
│   │       ├── public_key.json
│   │       └── vault.json
│   └── shared/
│       ├── elgamal_params.json
│       └── dh_params.json
│
├── tests/
│   ├── test_elgamal.py
│   ├── test_vault.py
│   ├── test_signing.py
│   └── test_dh.py
│
└── README.md
```

---

# Cryptographic Design

## AES-GCM Vault Encryption

Passwords stored in the vault are encrypted using AES-GCM. This provides:

* Confidentiality
* Integrity verification
* Protection against tampering

Each vault entry is encrypted using a randomly generated symmetric key and nonce.

## ElGamal Digital Signatures

The vault file can be signed using the owner's ElGamal private key. This ensures:

* The vault has not been modified
* The vault belongs to the correct owner

The signature is generated in `vault/signer.py` and verified before loading or importing vault data.

## Diffie–Hellman Secure Exchange

The export/import workflow uses Diffie–Hellman key exchange to derive a shared secret between two users. That shared secret is then used as the AES key for secure transmission.

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/your-username/password_manager.git
cd password_manager
```

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Example dependencies may include:

```text
cryptography
pycryptodome
pytest
```

---

# Running the Application

```bash
python app.py
```

The CLI can be extended to support commands such as:

```text
1. Create user
2. Generate keys
3. Add password entry
4. View vault
5. Sign vault
6. Verify vault
7. Export vault
8. Import vault
```

---

# Example User Data Layout

```text
data/users/alice/
├── private_key.json
├── public_key.json
└── vault.json
```

Example `public_key.json`:

```json
{
  "p": "...",
  "g": "...",
  "y": "..."
}
```

Example `vault.json`:

```json
{
  "entries": [
    {
      "site": "example.com",
      "username": "alice@example.com",
      "password": "<encrypted>"
    }
  ],
  "signature": {
    "r": "...",
    "s": "..."
  }
}
```

---

# Running Tests

Run all tests:

```bash
pytest
```

Run a specific test module:

```bash
pytest tests/test_elgamal.py
```

---

# Module Responsibilities

| Module                   | Responsibility                          |
| ------------------------ | --------------------------------------- |
| `crypto/elgamal.py`      | Key generation, encryption, signatures  |
| `crypto/dh.py`           | Diffie–Hellman shared secret generation |
| `crypto/aes_helper.py`   | AES-GCM encryption and decryption       |
| `crypto/hash_helper.py`  | SHA-256 hashing                         |
| `crypto/math_utils.py`   | Number theory and helper functions      |
| `vault/vault_manager.py` | Vault creation and management           |
| `vault/storage.py`       | Reading and writing JSON files          |
| `vault/signer.py`        | Sign and verify vault contents          |
| `exchange/exporter.py`   | Secure sharing between users            |

---






