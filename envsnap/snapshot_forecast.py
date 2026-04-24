"""Forecast future snapshot growth and usage trends based on history."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envsnap.history import get_history
from envsnap.storage import list_snapshots


@dataclass
class ForecastResult:
    snapshot_name: str
    total_events: int
    snap_count: int
    restore_count: int
    delete_count: int
    avg_events_per_day: float
    projected_30d_events: int
    trend: str  # "growing", "stable", "declining"
    notes: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "snapshot": self.snapshot_name,
            "total_events": self.total_events,
            "snap_count": self.snap_count,
            "restore_count": self.restore_count,
            "delete_count": self.delete_count,
            "avg_events_per_day": round(self.avg_events_per_day, 3),
            "projected_30d_events": self.projected_30d_events,
            "trend": self.trend,
            "notes": self.notes,
        }


def forecast_snapshot(name: str, window_days: int = 30) -> ForecastResult:
    """Analyse history for *name* and return a ForecastResult."""
    events = get_history(snapshot=name)
    total = len(events)
    snap_count = sum(1 for e in events if e["event"] == "snap")
    restore_count = sum(1 for e in events if e["event"] == "restore")
    delete_count = sum(1 for e in events if e["event"] == "delete")

    avg = total / window_days if window_days > 0 else 0.0
    projected = round(avg * 30)

    if avg > 2:
        trend = "growing"
    elif avg > 0.5:
        trend = "stable"
    else:
        trend = "declining"

    notes: List[str] = []
    if delete_count > snap_count:
        notes.append("More deletes than snaps — snapshot may be volatile.")
    if restore_count == 0 and snap_count > 0:
        notes.append("Never restored — consider whether this snapshot is useful.")

    return ForecastResult(
        snapshot_name=name,
        total_events=total,
        snap_count=snap_count,
        restore_count=restore_count,
        delete_count=delete_count,
        avg_events_per_day=avg,
        projected_30d_events=projected,
        trend=trend,
        notes=notes,
    )


def forecast_all(window_days: int = 30) -> List[ForecastResult]:
    """Return forecasts for every known snapshot."""
    return [forecast_snapshot(name, window_days) for name in list_snapshots()]


def format_forecast(result: ForecastResult) -> str:
    lines = [
        f"Snapshot : {result.snapshot_name}",
        f"Trend    : {result.trend}",
        f"Events   : {result.total_events} total  "
        f"(snap={result.snap_count}, restore={result.restore_count}, delete={result.delete_count})",
        f"Avg/day  : {result.avg_events_per_day:.3f}",
        f"30-day   : ~{result.projected_30d_events} events projected",
    ]
    if result.notes:
        lines.append("Notes    :")
        for note in result.notes:
            lines.append(f"  - {note}")
    return "\n".join(lines)
