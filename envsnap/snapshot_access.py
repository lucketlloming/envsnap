"""Track and report snapshot access (read) events."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from envsnap.storage import get_snapshot_dir, list_snapshots


def _access_path() -> Path:
    return get_snapshot_dir() / "_access_log.json"


def _load_access() -> dict:
    p = _access_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_access(data: dict) -> None:
    _access_path().write_text(json.dumps(data, indent=2))


def record_access(snapshot_name: str, action: str = "read") -> None:
    """Record an access event for *snapshot_name*."""
    data = _load_access()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
    }
    data.setdefault(snapshot_name, []).append(entry)
    _save_access(data)


def get_access_log(snapshot_name: str) -> List[dict]:
    """Return all access events for *snapshot_name*."""
    return _load_access().get(snapshot_name, [])


def get_last_accessed(snapshot_name: str) -> Optional[str]:
    """Return ISO timestamp of the most recent access, or None."""
    log = get_access_log(snapshot_name)
    if not log:
        return None
    return log[-1]["timestamp"]


def access_summary() -> List[dict]:
    """Return a summary row per snapshot with access count and last access."""
    data = _load_access()
    all_names = list_snapshots()
    rows = []
    for name in all_names:
        events = data.get(name, [])
        rows.append({
            "snapshot": name,
            "access_count": len(events),
            "last_accessed": events[-1]["timestamp"] if events else None,
        })
    return rows


def clear_access_log(snapshot_name: str) -> None:
    """Remove all access records for *snapshot_name*."""
    data = _load_access()
    data.pop(snapshot_name, None)
    _save_access(data)
