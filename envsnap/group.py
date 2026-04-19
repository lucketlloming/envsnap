"""Group multiple snapshots under a named group."""
from __future__ import annotations
import json
from pathlib import Path
from envsnap.storage import get_snapshot_dir, list_snapshots


def _groups_path() -> Path:
    return get_snapshot_dir() / "_groups.json"


def _load_groups() -> dict:
    p = _groups_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_groups(data: dict) -> None:
    _groups_path().write_text(json.dumps(data, indent=2))


def add_to_group(group: str, snapshot: str) -> None:
    existing = list_snapshots()
    if snapshot not in existing:
        raise KeyError(f"Snapshot '{snapshot}' does not exist.")
    data = _load_groups()
    members = data.setdefault(group, [])
    if snapshot not in members:
        members.append(snapshot)
    _save_groups(data)


def remove_from_group(group: str, snapshot: str) -> None:
    data = _load_groups()
    if group not in data:
        raise KeyError(f"Group '{group}' does not exist.")
    data[group] = [s for s in data[group] if s != snapshot]
    if not data[group]:
        del data[group]
    _save_groups(data)


def get_group(group: str) -> list[str]:
    data = _load_groups()
    if group not in data:
        raise KeyError(f"Group '{group}' does not exist.")
    return list(data[group])


def list_groups() -> list[str]:
    return list(_load_groups().keys())


def delete_group(group: str) -> None:
    data = _load_groups()
    if group not in data:
        raise KeyError(f"Group '{group}' does not exist.")
    del data[group]
    _save_groups(data)
