"""Retention policy management for snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envsnap.storage import get_snapshot_dir, list_snapshots


class RetentionError(Exception):
    """Raised when a retention policy operation fails."""


VALID_ACTIONS = ("warn", "delete")


def _retention_path() -> Path:
    return get_snapshot_dir() / "retention.json"


def _load_retention() -> dict:
    p = _retention_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_retention(data: dict) -> None:
    _retention_path().write_text(json.dumps(data, indent=2))


def set_retention(
    name: str,
    max_count: Optional[int] = None,
    max_age_days: Optional[int] = None,
    action: str = "warn",
) -> None:
    """Set a retention policy for a snapshot group or named snapshot."""
    if action not in VALID_ACTIONS:
        raise RetentionError(f"Invalid action '{action}'. Must be one of {VALID_ACTIONS}.")
    if max_count is not None and max_count < 1:
        raise RetentionError("max_count must be at least 1.")
    if max_age_days is not None and max_age_days < 1:
        raise RetentionError("max_age_days must be at least 1.")
    if max_count is None and max_age_days is None:
        raise RetentionError("At least one of max_count or max_age_days must be specified.")

    data = _load_retention()
    data[name] = {
        "max_count": max_count,
        "max_age_days": max_age_days,
        "action": action,
    }
    _save_retention(data)


def get_retention(name: str) -> Optional[dict]:
    """Return the retention policy for a name, or None if not set."""
    return _load_retention().get(name)


def remove_retention(name: str) -> None:
    """Remove a retention policy by name."""
    data = _load_retention()
    if name not in data:
        raise RetentionError(f"No retention policy found for '{name}'.")
    del data[name]
    _save_retention(data)


def list_retention() -> dict:
    """Return all retention policies."""
    return _load_retention()
