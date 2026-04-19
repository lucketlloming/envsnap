"""Snapshot annotation support — attach arbitrary key/value metadata to snapshots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envsnap.storage import get_snapshot_dir, list_snapshots


def _annotations_path() -> Path:
    return get_snapshot_dir() / "annotations.json"


def _load_annotations() -> Dict[str, Dict[str, str]]:
    p = _annotations_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_annotations(data: Dict[str, Dict[str, str]]) -> None:
    _annotations_path().write_text(json.dumps(data, indent=2))


def set_annotation(snapshot: str, key: str, value: str) -> None:
    """Set a metadata annotation on a snapshot."""
    known = list_snapshots()
    if snapshot not in known:
        raise KeyError(f"Snapshot '{snapshot}' not found.")
    data = _load_annotations()
    data.setdefault(snapshot, {})[key] = value
    _save_annotations(data)


def get_annotations(snapshot: str) -> Dict[str, str]:
    """Return all annotations for a snapshot."""
    return _load_annotations().get(snapshot, {})


def remove_annotation(snapshot: str, key: str) -> None:
    """Remove a single annotation key from a snapshot."""
    data = _load_annotations()
    if snapshot in data and key in data[snapshot]:
        del data[snapshot][key]
        if not data[snapshot]:
            del data[snapshot]
        _save_annotations(data)


def clear_annotations(snapshot: str) -> None:
    """Remove all annotations for a snapshot."""
    data = _load_annotations()
    if snapshot in data:
        del data[snapshot]
        _save_annotations(data)


def all_annotations() -> Dict[str, Dict[str, str]]:
    """Return all annotations across all snapshots."""
    return _load_annotations()
