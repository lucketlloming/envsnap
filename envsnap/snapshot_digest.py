"""Compute and compare cryptographic digests for snapshots."""
from __future__ import annotations

import hashlib
import json
from typing import Optional

from envsnap.storage import load_snapshot, list_snapshots


class DigestError(Exception):
    """Raised when a digest operation fails."""


def compute_digest(name: str) -> str:
    """Return a SHA-256 hex digest for the named snapshot's key-value data.

    Keys are sorted before hashing so the digest is deterministic regardless
    of insertion order.
    """
    data = load_snapshot(name)
    serialised = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialised.encode()).hexdigest()


def verify_digest(name: str, expected: str) -> bool:
    """Return True if the snapshot's current digest matches *expected*."""
    return compute_digest(name) == expected


def digest_all() -> dict[str, str]:
    """Return a mapping of snapshot name -> digest for every snapshot."""
    return {name: compute_digest(name) for name in list_snapshots()}


def compare_digests(name_a: str, name_b: str) -> dict[str, Optional[str]]:
    """Compare digests of two snapshots.

    Returns a dict with keys ``a``, ``b``, and ``match``.
    """
    digest_a = compute_digest(name_a)
    digest_b = compute_digest(name_b)
    return {
        "a": digest_a,
        "b": digest_b,
        "match": digest_a == digest_b,
    }
