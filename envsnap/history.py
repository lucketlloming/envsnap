"""Track snapshot creation and access history."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from envsnap.storage import get_snapshot_dir

_HISTORY_FILE = "history.json"


def _history_path() -> Path:
    return get_snapshot_dir() / _HISTORY_FILE


def _load_history() -> List[Dict[str, Any]]:
    path = _history_path()
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save_history(entries: List[Dict[str, Any]]) -> None:
    path = _history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)


def record_event(snapshot_name: str, action: str) -> None:
    """Record an action (create, restore, delete) for a snapshot."""
    entries = _load_history()
    entries.append({
        "snapshot": snapshot_name,
        "action": action,
        "timestamp": datetime.utcnow().isoformat()
    })
    _save_history(entries)


def get_history(snapshot_name: str = None) -> List[Dict[str, Any]]:
    """Return history entries, optionally filtered by snapshot name."""
    entries = _load_history()
    if snapshot_name:
        entries = [e for e in entries if e["snapshot"] == snapshot_name]
    return entries


def clear_history(snapshot_name: str = None) -> int:
    """Clear history entries. Returns number of entries removed."""
    entries = _load_history()
    if snapshot_name:
        remaining = [e for e in entries if e["snapshot"] != snapshot_name]
    else:
        remaining = []
    removed = len(entries) - len(remaining)
    _save_history(remaining)
    return removed


def format_history_report(entries: List[Dict[str, Any]]) -> str:
    if not entries:
        return "No history found."
    lines = []
    for e in entries:
        lines.append(f"[{e['timestamp']}] {e['action']:10s} {e['snapshot']}")
    return "\n".join(lines)
