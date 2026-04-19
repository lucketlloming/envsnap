"""Rollback support: restore a snapshot to a previous state using history."""
from __future__ import annotations

from typing import Optional

from envsnap.history import get_history, record_event
from envsnap.storage import load_snapshot, save_snapshot, list_snapshots


class RollbackError(Exception):
    pass


def get_rollback_points(name: str) -> list[dict]:
    """Return history entries for *name* that recorded a previous env state."""
    events = get_history(name)
    return [e for e in events if e.get("event") in ("snap", "restore", "import")]


def rollback_snapshot(name: str, steps: int = 1) -> dict:
    """Overwrite *name* with its state *steps* saves ago.

    Returns the restored data dict.
    Raises RollbackError if there are not enough history points.
    """
    if name not in list_snapshots():
        raise RollbackError(f"Snapshot '{name}' does not exist.")

    points = get_rollback_points(name)
    if len(points) < steps:
        raise RollbackError(
            f"Not enough history to roll back {steps} step(s) "
            f"(only {len(points)} point(s) available)."
        )

    target = points[-(steps)]
    previous_data: Optional[dict] = target.get("data")
    if previous_data is None:
        raise RollbackError(
            "History entry does not contain snapshot data. "
            "Re-snap the environment to build rollback-capable history."
        )

    save_snapshot(name, previous_data)
    record_event(name, "rollback", data=previous_data)
    return previous_data
