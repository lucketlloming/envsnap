"""Snapshot freshness analysis — how recently a snapshot was created or modified."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from envsnap.storage import list_snapshots, snapshot_path
from envsnap.history import get_history


@dataclass
class FreshnessResult:
    name: str
    last_event: Optional[str]        # ISO timestamp of most recent history event
    age_days: Optional[float]        # days since last_event (None if no history)
    level: str                       # "fresh" | "stale" | "aged" | "unknown"

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "last_event": self.last_event,
            "age_days": round(self.age_days, 2) if self.age_days is not None else None,
            "level": self.level,
        }


def _level(age_days: Optional[float]) -> str:
    if age_days is None:
        return "unknown"
    if age_days <= 7:
        return "fresh"
    if age_days <= 30:
        return "stale"
    return "aged"


def compute_freshness(name: str) -> FreshnessResult:
    """Compute freshness for a single snapshot."""
    p = snapshot_path(name)
    if not p.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found.")

    events = get_history(name)
    if not events:
        return FreshnessResult(name=name, last_event=None, age_days=None, level="unknown")

    latest_ts = max(e["timestamp"] for e in events)
    last_dt = datetime.fromisoformat(latest_ts)
    if last_dt.tzinfo is None:
        last_dt = last_dt.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    age_days = (now - last_dt).total_seconds() / 86400.0
    return FreshnessResult(
        name=name,
        last_event=latest_ts,
        age_days=age_days,
        level=_level(age_days),
    )


def compute_all_freshness() -> list[FreshnessResult]:
    return [compute_freshness(n) for n in list_snapshots()]


def format_freshness(result: FreshnessResult) -> str:
    lines = [
        f"Snapshot : {result.name}",
        f"Level    : {result.level}",
        f"Last event: {result.last_event or 'N/A'}",
        f"Age (days): {round(result.age_days, 2) if result.age_days is not None else 'N/A'}",
    ]
    return "\n".join(lines)
