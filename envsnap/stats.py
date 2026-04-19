"""Snapshot statistics and usage analytics."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from envsnap.storage import list_snapshots, load_snapshot
from envsnap.history import get_history
from envsnap.tags import get_tags
from envsnap.pin import get_pin


def snapshot_stats(name: str) -> dict[str, Any]:
    """Return statistics for a single snapshot."""
    data = load_snapshot(name)
    history = get_history(name)
    tags = get_tags(name)
    pin = get_pin(name)

    snap_events = [e for e in history if e["event"] == "snap"]
    restore_events = [e for e in history if e["event"] == "restore"]

    created_at = snap_events[0]["timestamp"] if snap_events else None
    last_restored = restore_events[-1]["timestamp"] if restore_events else None

    return {
        "name": name,
        "key_count": len(data),
        "tags": tags,
        "pinned": pin is not None,
        "created_at": created_at,
        "last_restored": last_restored,
        "restore_count": len(restore_events),
    }


def global_stats() -> dict[str, Any]:
    """Return aggregate statistics across all snapshots."""
    names = list_snapshots()
    if not names:
        return {
            "total_snapshots": 0,
            "total_keys": 0,
            "most_restored": None,
            "pinned_count": 0,
            "tagged_count": 0,
        }

    all_stats = [snapshot_stats(n) for n in names]
    total_keys = sum(s["key_count"] for s in all_stats)
    pinned_count = sum(1 for s in all_stats if s["pinned"])
    tagged_count = sum(1 for s in all_stats if s["tags"])
    most_restored = max(all_stats, key=lambda s: s["restore_count"])

    return {
        "total_snapshots": len(names),
        "total_keys": total_keys,
        "most_restored": most_restored["name"] if most_restored["restore_count"] > 0 else None,
        "pinned_count": pinned_count,
        "tagged_count": tagged_count,
    }


def format_stats(stats: dict[str, Any]) -> str:
    lines = []
    for k, v in stats.items():
        label = k.replace("_", " ").capitalize()
        lines.append(f"  {label}: {v}")
    return "\n".join(lines)
