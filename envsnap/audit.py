"""Audit log for envsnap: records who/when snapshots were accessed or modified."""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from envsnap.storage import get_snapshot_dir

_AUDIT_FILE = "audit.json"


def _audit_path() -> Path:
    return get_snapshot_dir() / _AUDIT_FILE


def _load_audit() -> List[dict]:
    p = _audit_path()
    if not p.exists():
        return []
    with p.open() as f:
        return json.load(f)


def _save_audit(entries: List[dict]) -> None:
    with _audit_path().open("w") as f:
        json.dump(entries, f, indent=2)


def record_audit(action: str, snapshot: str, user: Optional[str] = None, detail: Optional[str] = None) -> None:
    """Append an audit entry."""
    entries = _load_audit()
    entries.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "snapshot": snapshot,
        "user": user or os.environ.get("USER", "unknown"),
        "detail": detail,
    })
    _save_audit(entries)


def get_audit(snapshot: Optional[str] = None) -> List[dict]:
    """Return audit entries, optionally filtered by snapshot name."""
    entries = _load_audit()
    if snapshot:
        entries = [e for e in entries if e["snapshot"] == snapshot]
    return entries


def clear_audit(snapshot: Optional[str] = None) -> int:
    """Clear audit entries. Returns number removed."""
    entries = _load_audit()
    if snapshot:
        kept = [e for e in entries if e["snapshot"] != snapshot]
    else:
        kept = []
    removed = len(entries) - len(kept)
    _save_audit(kept)
    return removed
