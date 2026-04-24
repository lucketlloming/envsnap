"""Snapshot ownership tracking — assign and query owners for snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envsnap.storage import get_snapshot_dir, list_snapshots


class OwnershipError(Exception):
    """Raised for general ownership operation failures."""


class SnapshotNotFoundError(OwnershipError):
    """Raised when the target snapshot does not exist."""


def _ownership_path() -> Path:
    return get_snapshot_dir() / "_ownership.json"


def _load_ownership() -> dict[str, str]:
    p = _ownership_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ownership(data: dict[str, str]) -> None:
    _ownership_path().write_text(json.dumps(data, indent=2))


def set_owner(snapshot_name: str, owner: str) -> None:
    """Assign *owner* to *snapshot_name*.

    Raises SnapshotNotFoundError if the snapshot does not exist.
    """
    if snapshot_name not in list_snapshots():
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    data = _load_ownership()
    data[snapshot_name] = owner
    _save_ownership(data)


def get_owner(snapshot_name: str) -> Optional[str]:
    """Return the owner of *snapshot_name*, or None if unset."""
    return _load_ownership().get(snapshot_name)


def remove_owner(snapshot_name: str) -> None:
    """Remove the ownership record for *snapshot_name*.

    Raises OwnershipError if no record exists.
    """
    data = _load_ownership()
    if snapshot_name not in data:
        raise OwnershipError(f"No ownership record for '{snapshot_name}'.")
    del data[snapshot_name]
    _save_ownership(data)


def list_owned(owner: str) -> list[str]:
    """Return all snapshot names owned by *owner*."""
    return [name for name, o in _load_ownership().items() if o == owner]


def all_ownership() -> dict[str, str]:
    """Return the full ownership mapping."""
    return _load_ownership()
