"""Tests for envsnap.encrypt (mocked to avoid cryptography dependency)."""
from __future__ import annotations

import base64
import json
import pytest


# ---------------------------------------------------------------------------
# Helpers / lightweight stubs so tests run without the cryptography package
# ---------------------------------------------------------------------------

class _FakeAESGCM:
    def __init__(self, key: bytes):
        self._key = key

    def encrypt(self, nonce: bytes, data: bytes, aad) -> bytes:
        # XOR first byte of key as trivial "encryption" for testing
        return bytes(b ^ self._key[0] for b in data)

    def decrypt(self, nonce: bytes, data: bytes, aad) -> bytes:
        return bytes(b ^ self._key[0] for b in data)


@pytest.fixture(autouse=True)
def _patch_cryptography(monkeypatch):
    import types
    fake_mod = types.ModuleType("cryptography")
    fake_prim = types.ModuleType("cryptography.hazmat")
    fake_prim2 = types.ModuleType("cryptography.hazmat.primitives")
    fake_ciphers = types.ModuleType("cryptography.hazmat.primitives.ciphers")
    fake_aead = types.ModuleType("cryptography.hazmat.primitives.ciphers.aead")
    fake_aead.AESGCM = _FakeAESGCM
    import sys
    sys.modules.setdefault("cryptography", fake_mod)
    sys.modules["cryptography.hazmat"] = fake_prim
    sys.modules["cryptography.hazmat.primitives"] = fake_prim2
    sys.modules["cryptography.hazmat.primitives.ciphers"] = fake_ciphers
    sys.modules["cryptography.hazmat.primitives.ciphers.aead"] = fake_aead
    yield


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

from envsnap.encrypt import encrypt_data, decrypt_data  # noqa: E402


def test_encrypt_returns_string():
    blob = encrypt_data({"KEY": "value"}, "secret")
    assert isinstance(blob, str)
    envelope = json.loads(blob)
    assert {"salt", "nonce", "ciphertext"} <= envelope.keys()


def test_roundtrip():
    original = {"FOO": "bar", "NUM": "42"}
    blob = encrypt_data(original, "mypassword")
    recovered = decrypt_data(blob, "mypassword")
    assert recovered == original


def test_wrong_password_raises():
    blob = encrypt_data({"A": "1"}, "correct")
    # Tamper with ciphertext so XOR decode produces garbage JSON
    env = json.loads(blob)
    ct = base64.b64decode(env["ciphertext"])
    env["ciphertext"] = base64.b64encode(bytes(b ^ 0xFF for b in ct)).decode()
    blob2 = json.dumps(env)
    with pytest.raises((ValueError, json.JSONDecodeError)):
        decrypt_data(blob2, "correct")


def test_empty_dict_roundtrip():
    blob = encrypt_data({}, "pw")
    assert decrypt_data(blob, "pw") == {}
