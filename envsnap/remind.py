"""Reminders: attach a reminder message and due date to a snapshot."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Optional

from envsnap.storage import get_snapshot_dir, list_snapshots


class ReminderNotFoundError(KeyError):
    pass


class SnapshotNotFoundError(KeyError):
    pass


def _reminders_path() -> Path:
    return get_snapshot_dir() / "reminders.json"


def _load_reminders() -> dict:
    p = _reminders_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_reminders(data: dict) -> None:
    _reminders_path().write_text(json.dumps(data, indent=2))


def set_reminder(snapshot: str, message: str, due: Optional[str] = None) -> None:
    """Attach a reminder to a snapshot. due should be ISO date string (YYYY-MM-DD)."""
    if snapshot not in list_snapshots():
        raise SnapshotNotFoundError(snapshot)
    if due is not None:
        date.fromisoformat(due)  # validate
    data = _load_reminders()
    data[snapshot] = {"message": message, "due": due}
    _save_reminders(data)


def get_reminder(snapshot: str) -> dict:
    data = _load_reminders()
    if snapshot not in data:
        raise ReminderNotFoundError(snapshot)
    return data[snapshot]


def remove_reminder(snapshot: str) -> None:
    data = _load_reminders()
    if snapshot not in data:
        raise ReminderNotFoundError(snapshot)
    del data[snapshot]
    _save_reminders(data)


def list_reminders() -> dict:
    return _load_reminders()


def due_reminders(as_of: Optional[str] = None) -> dict:
    """Return reminders whose due date <= as_of (defaults to today)."""
    today = date.fromisoformat(as_of) if as_of else date.today()
    result = {}
    for snap, info in _load_reminders().items():
        if info.get("due") is None:
            continue
        if date.fromisoformat(info["due"]) <= today:
            result[snap] = info
    return result
