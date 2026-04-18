"""Scheduled auto-snapshot support for envsnap."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from envsnap.storage import get_snapshot_dir


def _schedule_path() -> Path:
    return get_snapshot_dir() / "schedules.json"


def _load_schedules() -> dict:
    p = _schedule_path()
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_schedules(data: dict) -> None:
    p = _schedule_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def set_schedule(name: str, interval: str, keys: Optional[list] = None) -> None:
    """Register an auto-snapshot schedule.

    Args:
        name: Snapshot name prefix.
        interval: One of 'hourly', 'daily', 'weekly'.
        keys: Optional list of env keys to capture.
    """
    valid = {"hourly", "daily", "weekly"}
    if interval not in valid:
        raise ValueError(f"interval must be one of {valid}")
    data = _load_schedules()
    data[name] = {
        "interval": interval,
        "keys": keys or [],
        "created_at": datetime.utcnow().isoformat(),
        "last_run": None,
    }
    _save_schedules(data)


def remove_schedule(name: str) -> None:
    data = _load_schedules()
    if name not in data:
        raise KeyError(f"No schedule found for '{name}'")
    del data[name]
    _save_schedules(data)


def get_schedule(name: str) -> dict:
    data = _load_schedules()
    if name not in data:
        raise KeyError(f"No schedule found for '{name}'")
    return data[name]


def list_schedules() -> dict:
    return _load_schedules()


def update_last_run(name: str, timestamp: Optional[str] = None) -> None:
    data = _load_schedules()
    if name not in data:
        raise KeyError(f"No schedule found for '{name}'")
    data[name]["last_run"] = timestamp or datetime.utcnow().isoformat()
    _save_schedules(data)
