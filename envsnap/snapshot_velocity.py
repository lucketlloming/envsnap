"""Snapshot velocity: measures rate of change over time."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from envsnap.history import get_history
from envsnap.storage import list_snapshots


@dataclass
class VelocityResult:
    snapshot: str
    total_events: int
    events_last_7d: int
    events_last_30d: int
    avg_events_per_day: float
    level: str  # "high" | "moderate" | "low" | "idle"

    def as_dict(self) -> dict:
        return {
            "snapshot": self.snapshot,
            "total_events": self.total_events,
            "events_last_7d": self.events_last_7d,
            "events_last_30d": self.events_last_30d,
            "avg_events_per_day": round(self.avg_events_per_day, 3),
            "level": self.level,
        }


def _level(avg: float) -> str:
    if avg >= 2.0:
        return "high"
    if avg >= 0.5:
        return "moderate"
    if avg > 0.0:
        return "low"
    return "idle"


def _count_since(events: list, days: int) -> int:
    now = datetime.now(tz=timezone.utc)
    cutoff = now.timestamp() - days * 86400
    return sum(1 for e in events if e.get("ts", 0) >= cutoff)


def compute_velocity(snapshot: str) -> VelocityResult:
    events = get_history(snapshot)
    total = len(events)
    last_7 = _count_since(events, 7)
    last_30 = _count_since(events, 30)
    avg = last_30 / 30.0 if total else 0.0
    return VelocityResult(
        snapshot=snapshot,
        total_events=total,
        events_last_7d=last_7,
        events_last_30d=last_30,
        avg_events_per_day=avg,
        level=_level(avg),
    )


def compute_all_velocity() -> List[VelocityResult]:
    return [compute_velocity(name) for name in list_snapshots()]


def format_velocity(result: VelocityResult) -> str:
    lines = [
        f"Snapshot : {result.snapshot}",
        f"Level    : {result.level}",
        f"Total    : {result.total_events} events",
        f"Last 7d  : {result.events_last_7d} events",
        f"Last 30d : {result.events_last_30d} events",
        f"Avg/day  : {result.avg_events_per_day:.3f}",
    ]
    return "\n".join(lines)
