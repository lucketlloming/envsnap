"""Priority management for snapshots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envsnap.storage import get_snapshot_dir, list_snapshots

VALID_PRIORITIES = {"low", "normal", "high", "critical"}
DEFAULT_PRIORITY = "normal"


class InvalidPriorityError(ValueError):
    pass


class SnapshotNotFoundError(KeyError):
    pass


def _priorities_path() -> Path:
    return get_snapshot_dir() / "priorities.json"


def _load_priorities() -> Dict[str, str]:
    p = _priorities_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_priorities(data: Dict[str, str]) -> None:
    _priorities_path().write_text(json.dumps(data, indent=2))


def set_priority(snapshot: str, priority: str) -> None:
    """Set the priority of a snapshot."""
    if priority not in VALID_PRIORITIES:
        raise InvalidPriorityError(
            f"Invalid priority '{priority}'. Choose from: {sorted(VALID_PRIORITIES)}"
        )
    if snapshot not in list_snapshots():
        raise SnapshotNotFoundError(f"Snapshot '{snapshot}' not found.")
    data = _load_priorities()
    data[snapshot] = priority
    _save_priorities(data)


def get_priority(snapshot: str) -> str:
    """Return the priority of a snapshot, defaulting to 'normal'."""
    return _load_priorities().get(snapshot, DEFAULT_PRIORITY)


def remove_priority(snapshot: str) -> None:
    """Remove explicit priority for a snapshot (resets to default)."""
    data = _load_priorities()
    data.pop(snapshot, None)
    _save_priorities(data)


def list_by_priority(priority: Optional[str] = None) -> Dict[str, List[str]]:
    """Return snapshots grouped by priority, optionally filtered."""
    all_snapshots = list_snapshots()
    data = _load_priorities()
    result: Dict[str, List[str]] = {p: [] for p in VALID_PRIORITIES}
    for snap in all_snapshots:
        p = data.get(snap, DEFAULT_PRIORITY)
        result[p].append(snap)
    if priority:
        return {priority: result.get(priority, [])}
    return result
