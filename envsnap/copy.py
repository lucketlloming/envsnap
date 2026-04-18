"""Copy selected keys from one snapshot into another (merging or creating)."""

from __future__ import annotations

from typing import List, Optional

from envsnap.storage import load_snapshot, save_snapshot, list_snapshots


class SnapshotNotFoundError(Exception):
    pass


def copy_keys(
    src: str,
    dst: str,
    keys: List[str],
    overwrite: bool = False,
) -> dict:
    """Copy *keys* from snapshot *src* into snapshot *dst*.

    Parameters
    ----------
    src:       source snapshot name
    dst:       destination snapshot name (created if missing)
    keys:      list of env-var names to copy
    overwrite: if False, existing keys in *dst* are kept unchanged

    Returns the updated data written to *dst*.
    """
    existing = list_snapshots()

    if src not in existing:
        raise SnapshotNotFoundError(f"Source snapshot '{src}' not found.")

    src_data: dict = load_snapshot(src)

    dst_data: dict = {}
    if dst in existing:
        dst_data = load_snapshot(dst)

    missing = [k for k in keys if k not in src_data]
    if missing:
        raise KeyError(f"Keys not found in '{src}': {missing}")

    for key in keys:
        if overwrite or key not in dst_data:
            dst_data[key] = src_data[key]

    save_snapshot(dst, dst_data)
    return dst_data
