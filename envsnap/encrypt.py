"""Optional AES-GCM encryption for snapshot files."""
from __future__ import annotations

import base64
import json
import os

SALT_SIZE = 16
NONCE_SIZE = 12


def _derive_key(password: str, salt: bytes) -> bytes:
    from hashlib import pbkdf2_hmac
    return pbkdf2_hmac("sha256", password.encode(), salt, 100_000, dklen=32)


def encrypt_data(data: dict, password: str) -> str:
    """Encrypt a dict to a base64-encoded JSON envelope."""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        raise RuntimeError("cryptography package required: pip install cryptography")

    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = _derive_key(password, salt)
    plaintext = json.dumps(data).encode()
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)
    envelope = {
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
    }
    return json.dumps(envelope)


def decrypt_data(blob: str, password: str) -> dict:
    """Decrypt a base64-encoded JSON envelope back to a dict."""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        raise RuntimeError("cryptography package required: pip install cryptography")

    envelope = json.loads(blob)
    salt = base64.b64decode(envelope["salt"])
    nonce = base64.b64decode(envelope["nonce"])
    ciphertext = base64.b64decode(envelope["ciphertext"])
    key = _derive_key(password, salt)
    try:
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
    except Exception:
        raise ValueError("Decryption failed: wrong password or corrupted data")
    return json.loads(plaintext.decode())
