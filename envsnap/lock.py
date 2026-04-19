"""Snapshot locking — prevent modifications to a snapshot."""
from __future__ import annotations

import json
from pathlib import Path

from envsnap.storage import get_snapshot_dir, list_snapshots


class SnapshotNotFoundError(Exception):
    pass


class SnapshotLockedError(Exception):
    pass


def _locks_path() -> Path:
    return get_snapshot_dir() / "locks.json"


def _load_locks() -> dict:
    p = _locks_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_locks(data: dict) -> None:
    _locks_path().write_text(json.dumps(data, indent=2))


def lock_snapshot(name: str) -> None:
    """Lock a snapshot so it cannot be modified or deleted."""
    if name not in list_snapshots():
        raise SnapshotNotFoundError(f"Snapshot '{name}' not found.")
    locks = _load_locks()
    locks[name] = True
    _save_locks(locks)


def unlock_snapshot(name: str) -> None:
    """Remove the lock from a snapshot."""
    locks = _load_locks()
    if name not in locks:
        raise SnapshotNotFoundError(f"No lock found for snapshot '{name}'.")
    del locks[name]
    _save_locks(locks)


def is_locked(name: str) -> bool:
    """Return True if the snapshot is locked."""
    return _load_locks().get(name, False)


def assert_not_locked(name: str) -> None:
    """Raise SnapshotLockedError if the snapshot is locked."""
    if is_locked(name):
        raise SnapshotLockedError(
            f"Snapshot '{name}' is locked. Unlock it before making changes."
        )


def list_locked() -> list[str]:
    """Return all currently locked snapshot names."""
    return [k for k, v in _load_locks().items() if v]
