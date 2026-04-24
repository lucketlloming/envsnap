"""Lifecycle state management for snapshots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envsnap.storage import get_snapshot_dir, list_snapshots

VALID_STATES = ("draft", "active", "deprecated", "archived")
VALID_TRANSITIONS = {
    "draft": {"active"},
    "active": {"deprecated", "archived"},
    "deprecated": {"archived", "active"},
    "archived": set(),
}


class LifecycleError(Exception):
    pass


class SnapshotNotFoundError(Exception):
    pass


def _lifecycle_path() -> Path:
    return get_snapshot_dir() / "lifecycle.json"


def _load_lifecycle() -> dict:
    p = _lifecycle_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_lifecycle(data: dict) -> None:
    _lifecycle_path().write_text(json.dumps(data, indent=2))


def set_state(snapshot: str, state: str) -> None:
    """Force-set the lifecycle state (admin use)."""
    if state not in VALID_STATES:
        raise LifecycleError(f"Invalid state '{state}'. Choose from {VALID_STATES}.")
    if snapshot not in list_snapshots():
        raise SnapshotNotFoundError(f"Snapshot '{snapshot}' not found.")
    data = _load_lifecycle()
    data[snapshot] = state
    _save_lifecycle(data)


def transition(snapshot: str, new_state: str) -> None:
    """Transition snapshot to a new state, enforcing valid transitions."""
    if new_state not in VALID_STATES:
        raise LifecycleError(f"Invalid state '{new_state}'.")
    if snapshot not in list_snapshots():
        raise SnapshotNotFoundError(f"Snapshot '{snapshot}' not found.")
    data = _load_lifecycle()
    current = data.get(snapshot, "draft")
    if new_state not in VALID_TRANSITIONS[current]:
        raise LifecycleError(
            f"Cannot transition '{snapshot}' from '{current}' to '{new_state}'."
        )
    data[snapshot] = new_state
    _save_lifecycle(data)


def get_state(snapshot: str) -> str:
    """Return the current lifecycle state (default: 'draft')."""
    data = _load_lifecycle()
    return data.get(snapshot, "draft")


def list_by_state(state: str) -> list[str]:
    """Return all snapshots in the given state."""
    data = _load_lifecycle()
    all_snaps = list_snapshots()
    return [s for s in all_snaps if data.get(s, "draft") == state]
