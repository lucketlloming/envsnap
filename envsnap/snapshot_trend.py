"""Trend analysis for snapshot usage over time."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from envsnap.history import get_history
from envsnap.storage import list_snapshots


@dataclass
class TrendPoint:
    date: str  # ISO date YYYY-MM-DD
    count: int

    def as_dict(self) -> Dict:
        return {"date": self.date, "count": self.count}


@dataclass
class TrendResult:
    snapshot: Optional[str]
    event_type: str
    points: List[TrendPoint] = field(default_factory=list)
    peak_date: Optional[str] = None
    peak_count: int = 0
    total: int = 0

    def as_dict(self) -> Dict:
        return {
            "snapshot": self.snapshot,
            "event_type": self.event_type,
            "points": [p.as_dict() for p in self.points],
            "peak_date": self.peak_date,
            "peak_count": self.peak_count,
            "total": self.total,
        }


def build_trend(
    snapshot: Optional[str] = None,
    event_type: str = "snap",
) -> TrendResult:
    """Aggregate history events by day for the given snapshot and event type."""
    events = get_history(snapshot)
    daily: Dict[str, int] = {}
    for ev in events:
        if ev.get("action") != event_type:
            continue
        ts: str = ev.get("timestamp", "")
        date = ts[:10] if len(ts) >= 10 else "unknown"
        daily[date] = daily.get(date, 0) + 1

    points = [TrendPoint(date=d, count=c) for d, c in sorted(daily.items())]
    total = sum(p.count for p in points)
    peak = max(points, key=lambda p: p.count, default=None)

    return TrendResult(
        snapshot=snapshot,
        event_type=event_type,
        points=points,
        peak_date=peak.date if peak else None,
        peak_count=peak.count if peak else 0,
        total=total,
    )


def build_all_trends(event_type: str = "snap") -> List[TrendResult]:
    """Build trends for every known snapshot."""
    return [build_trend(name, event_type) for name in list_snapshots()]


def format_trend(result: TrendResult) -> str:
    lines = [
        f"Trend for: {result.snapshot or '(all)'} [{result.event_type}]",
        f"  Total events : {result.total}",
        f"  Peak date    : {result.peak_date or 'n/a'} ({result.peak_count})",
        "  Daily counts :",
    ]
    for p in result.points:
        bar = "#" * min(p.count, 40)
        lines.append(f"    {p.date}  {bar} {p.count}")
    if not result.points:
        lines.append("    (no data)")
    return "\n".join(lines)
