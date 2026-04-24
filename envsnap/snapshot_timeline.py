"""Timeline view of snapshot history with chronological ordering and event grouping."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from envsnap.history import get_history
from envsnap.storage import list_snapshots


@dataclass
class TimelineEntry:
    snapshot: str
    event: str
    timestamp: str
    details: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "snapshot": self.snapshot,
            "event": self.event,
            "timestamp": self.timestamp,
            "details": self.details,
        }


def build_timeline(
    snapshot: Optional[str] = None,
    event_filter: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[TimelineEntry]:
    """Build a chronological timeline of events.

    Args:
        snapshot: If given, restrict to events for this snapshot.
        event_filter: If given, restrict to events of this type.
        limit: Maximum number of entries to return.

    Returns:
        List of TimelineEntry sorted oldest-first.
    """
    if snapshot:
        names = [snapshot]
    else:
        names = list_snapshots()

    entries: List[TimelineEntry] = []
    for name in names:
        for record in get_history(name):
            ev = record.get("event", "")
            if event_filter and ev != event_filter:
                continue
            entries.append(
                TimelineEntry(
                    snapshot=name,
                    event=ev,
                    timestamp=record.get("timestamp", ""),
                    details={k: v for k, v in record.items() if k not in ("event", "timestamp")},
                )
            )

    entries.sort(key=lambda e: e.timestamp)

    if limit is not None:
        entries = entries[-limit:]

    return entries


def format_timeline(entries: List[TimelineEntry], fmt: str = "text") -> str:
    """Format timeline entries for display."""
    if fmt == "json":
        return json.dumps([e.as_dict() for e in entries], indent=2)

    if not entries:
        return "No timeline entries found."

    lines = []
    for e in entries:
        ts = e.timestamp[:19].replace("T", " ") if e.timestamp else "unknown"
        detail_str = ""
        if e.details:
            detail_str = "  " + "  ".join(f"{k}={v}" for k, v in e.details.items())
        lines.append(f"[{ts}] {e.snapshot:20s}  {e.event}{detail_str}")
    return "\n".join(lines)
