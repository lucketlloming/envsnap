"""Clone an existing snapshot under a new name, optionally overriding keys."""

from __future__ import annotations

from typing import Dict, Optional

from envsnap.storage import load_snapshot, save_snapshot, list_snapshots


class SnapshotNotFoundError(Exception):
    pass


class SnapshotAlreadyExistsError(Exception):
    pass


def clone_snapshot(
    source: str,
    destination: str,
    overrides: Optional[Dict[str, str]] = None,
    overwrite: bool = False,
) -> Dict[str, str]:
    """Clone *source* snapshot to *destination*.

    Args:
        source: Name of the snapshot to clone.
        destination: Name for the new snapshot.
        overrides: Optional key/value pairs to merge into the clone.
        overwrite: If True, overwrite destination if it already exists.

    Returns:
        The data written to the new snapshot.

    Raises:
        SnapshotNotFoundError: If *source* does not exist.
        SnapshotAlreadyExistsError: If *destination* exists and *overwrite* is False.
    """
    existing = list_snapshots()

    if source not in existing:
        raise SnapshotNotFoundError(f"Snapshot '{source}' not found.")

    if destination in existing and not overwrite:
        raise SnapshotAlreadyExistsError(
            f"Snapshot '{destination}' already exists. Use --overwrite to replace it."
        )

    data: Dict[str, str] = dict(load_snapshot(source))

    if overrides:
        data.update(overrides)

    save_snapshot(destination, data)
    return data
