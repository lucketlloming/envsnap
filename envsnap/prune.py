"""Prune old or unused snapshots based on age or count limits."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from envsnap.storage import list_snapshots, load_snapshot, snapshot_path
from envsnap.history import get_history


class PruneError(Exception):
    pass


def _snapshot_age_days(name: str) -> Optional[float]:
    """Return age in days based on last recorded history event, or None."""
    events = get_history(name)
    if not events:
        return None
    latest = max(events, key=lambda e: e.get("timestamp", ""))
    ts = latest.get("timestamp")
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - dt).total_seconds() / 86400
        return age
    except ValueError:
        return None


def prune_by_age(max_age_days: float, dry_run: bool = False) -> list[str]:
    """Delete snapshots older than max_age_days. Returns list of pruned names."""
    pruned = []
    for name in list_snapshots():
        age = _snapshot_age_days(name)
        if age is not None and age > max_age_days:
            if not dry_run:
                p = snapshot_path(name)
                p.unlink(missing_ok=True)
            pruned.append(name)
    return pruned


def prune_by_count(keep: int, dry_run: bool = False) -> list[str]:
    """Keep only the most recent `keep` snapshots. Returns list of pruned names."""
    if keep < 1:
        raise PruneError("keep must be >= 1")
    names = list_snapshots()

    def _latest_ts(name: str) -> str:
        events = get_history(name)
        if not events:
            return ""
        return max(e.get("timestamp", "") for e in events)

    sorted_names = sorted(names, key=_latest_ts, reverse=True)
    to_prune = sorted_names[keep:]
    if not dry_run:
        for name in to_prune:
            snapshot_path(name).unlink(missing_ok=True)
    return to_prune
