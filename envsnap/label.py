"""Label management for snapshots.

Labels are free-form string tags that can be attached to snapshots
for quick categorisation (e.g. 'production', 'staging', 'wip').
Unlike tags (which live in tags.py and support structured queries),
labels are intended as lightweight, human-readable markers.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envsnap.storage import get_snapshot_dir, list_snapshots


class SnapshotNotFoundError(Exception):
    pass


def _labels_path() -> Path:
    return get_snapshot_dir() / "labels.json"


def _load_labels() -> Dict[str, List[str]]:
    p = _labels_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_labels(data: Dict[str, List[str]]) -> None:
    _labels_path().write_text(json.dumps(data, indent=2))


def add_label(snapshot: str, label: str) -> None:
    """Attach *label* to *snapshot* (idempotent)."""
    if snapshot not in list_snapshots():
        raise SnapshotNotFoundError(snapshot)
    data = _load_labels()
    existing = data.get(snapshot, [])
    if label not in existing:
        existing.append(label)
    data[snapshot] = existing
    _save_labels(data)


def remove_label(snapshot: str, label: str) -> None:
    """Detach *label* from *snapshot*.  No-op if label not present."""
    data = _load_labels()
    existing = data.get(snapshot, [])
    data[snapshot] = [l for l in existing if l != label]
    if not data[snapshot]:
        del data[snapshot]
    _save_labels(data)


def get_labels(snapshot: str) -> List[str]:
    """Return all labels attached to *snapshot*."""
    return _load_labels().get(snapshot, [])


def snapshots_with_label(label: str) -> List[str]:
    """Return all snapshot names that carry *label*."""
    return [name for name, labels in _load_labels().items() if label in labels]


def clear_labels(snapshot: str) -> None:
    """Remove every label from *snapshot*."""
    data = _load_labels()
    data.pop(snapshot, None)
    _save_labels(data)
