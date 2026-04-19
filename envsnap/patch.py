"""Apply a partial update (patch) to an existing snapshot."""
from __future__ import annotations

from typing import Optional

from envsnap.storage import load_snapshot, save_snapshot, list_snapshots


class SnapshotNotFoundError(KeyError):
    pass


def patch_snapshot(
    name: str,
    updates: dict[str, str],
    delete_keys: Optional[list[str]] = None,
) -> dict[str, str]:
    """Merge *updates* into snapshot *name*, optionally removing *delete_keys*.

    Returns the resulting env dict.
    """
    if name not in list_snapshots():
        raise SnapshotNotFoundError(f"Snapshot '{name}' not found.")

    data = load_snapshot(name)

    data.update(updates)

    for key in delete_keys or []:
        data.pop(key, None)

    save_snapshot(name, data)
    return data


def set_key(name: str, key: str, value: str) -> dict[str, str]:
    """Convenience wrapper to set a single key in snapshot *name*."""
    return patch_snapshot(name, {key: value})


def unset_key(name: str, key: str) -> dict[str, str]:
    """Convenience wrapper to remove a single key from snapshot *name*."""
    return patch_snapshot(name, {}, delete_keys=[key])
