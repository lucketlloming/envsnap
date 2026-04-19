"""Expiry management for snapshots."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envsnap.storage import get_snapshot_dir, list_snapshots, snapshot_path


class ExpiryNotFoundError(Exception):
    pass


class SnapshotNotFoundError(Exception):
    pass


DATE_FMT = "%Y-%m-%d"


def _expiry_path(snapshot_dir: Optional[Path] = None) -> Path:
    return (snapshot_dir or get_snapshot_dir()) / "expiry.json"


def _load_expiry(snapshot_dir: Optional[Path] = None) -> dict:
    p = _expiry_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_expiry(data: dict, snapshot_dir: Optional[Path] = None) -> None:
    _expiry_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def set_expiry(name: str, date: str, snapshot_dir: Optional[Path] = None) -> None:
    """Set an expiry date (YYYY-MM-DD) for a snapshot."""
    if not snapshot_path(name, snapshot_dir).exists():
        raise SnapshotNotFoundError(name)
    try:
        datetime.strptime(date, DATE_FMT)
    except ValueError:
        raise ValueError(f"Invalid date format: {date!r}. Expected YYYY-MM-DD.")
    data = _load_expiry(snapshot_dir)
    data[name] = date
    _save_expiry(data, snapshot_dir)


def get_expiry(name: str, snapshot_dir: Optional[Path] = None) -> Optional[str]:
    return _load_expiry(snapshot_dir).get(name)


def remove_expiry(name: str, snapshot_dir: Optional[Path] = None) -> None:
    data = _load_expiry(snapshot_dir)
    if name not in data:
        raise ExpiryNotFoundError(name)
    del data[name]
    _save_expiry(data, snapshot_dir)


def list_expiry(snapshot_dir: Optional[Path] = None) -> dict:
    """Return all name -> date mappings."""
    return dict(_load_expiry(snapshot_dir))


def get_expired(snapshot_dir: Optional[Path] = None) -> list[str]:
    """Return names of snapshots whose expiry date has passed."""
    today = datetime.now(timezone.utc).date()
    result = []
    for name, date_str in _load_expiry(snapshot_dir).items():
        if datetime.strptime(date_str, DATE_FMT).date() <= today:
            result.append(name)
    return result
