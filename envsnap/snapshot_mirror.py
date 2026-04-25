"""Snapshot mirroring: sync snapshots to/from a remote directory."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import List, Tuple

from envsnap.storage import list_snapshots, snapshot_path, get_snapshot_dir


class MirrorError(Exception):
    pass


def _remote_path(remote_dir: str, name: str) -> Path:
    return Path(remote_dir) / f"{name}.json"


def push_snapshot(name: str, remote_dir: str, overwrite: bool = False) -> Path:
    """Copy a local snapshot to remote_dir."""
    src = snapshot_path(name)
    if not src.exists():
        raise MirrorError(f"Snapshot '{name}' not found.")
    dest_dir = Path(remote_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = _remote_path(remote_dir, name)
    if dest.exists() and not overwrite:
        raise MirrorError(f"Remote snapshot '{name}' already exists. Use overwrite=True.")
    shutil.copy2(src, dest)
    return dest


def pull_snapshot(name: str, remote_dir: str, overwrite: bool = False) -> Path:
    """Copy a snapshot from remote_dir to local storage."""
    src = _remote_path(remote_dir, name)
    if not src.exists():
        raise MirrorError(f"Remote snapshot '{name}' not found in '{remote_dir}'.")
    dest = snapshot_path(name)
    if dest.exists() and not overwrite:
        raise MirrorError(f"Local snapshot '{name}' already exists. Use overwrite=True.")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return dest


def sync_status(remote_dir: str) -> List[Tuple[str, str]]:
    """Return list of (name, status) tuples: 'local-only', 'remote-only', 'synced', 'diverged'."""
    local_names = set(list_snapshots())
    remote_dir_path = Path(remote_dir)
    remote_names = {
        p.stem for p in remote_dir_path.glob("*.json")
    } if remote_dir_path.exists() else set()

    results = []
    for name in local_names | remote_names:
        local = snapshot_path(name)
        remote = _remote_path(remote_dir, name)
        if name in local_names and name not in remote_names:
            results.append((name, "local-only"))
        elif name in remote_names and name not in local_names:
            results.append((name, "remote-only"))
        else:
            local_data = json.loads(local.read_text())
            remote_data = json.loads(remote.read_text())
            status = "synced" if local_data == remote_data else "diverged"
            results.append((name, status))
    return sorted(results)
