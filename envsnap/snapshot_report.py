"""Generate rich summary reports for one or all snapshots."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from envsnap.storage import load_snapshot, list_snapshots
from envsnap.stats import snapshot_stats
from envsnap.pin import get_pin
from envsnap.lock import is_locked
from envsnap.rating import get_rating
from envsnap.tags import get_tags
from envsnap.notes import get_note


@dataclass
class SnapshotReport:
    name: str
    key_count: int
    tags: list[str] = field(default_factory=list)
    pinned: bool = False
    locked: bool = False
    rating: int | None = None
    note: str | None = None
    stats: dict[str, Any] = field(default_factory=dict)


def build_report(name: str) -> SnapshotReport:
    """Build a SnapshotReport for a single snapshot."""
    data = load_snapshot(name)
    stats = snapshot_stats(name)

    try:
        pinned = get_pin(name) is not None
    except Exception:
        pinned = False

    try:
        locked = is_locked(name)
    except Exception:
        locked = False

    try:
        rating_entry = get_rating(name)
        rating = rating_entry["score"] if rating_entry else None
    except Exception:
        rating = None

    return SnapshotReport(
        name=name,
        key_count=len(data),
        tags=get_tags(name),
        pinned=pinned,
        locked=locked,
        rating=rating,
        note=get_note(name),
        stats=stats,
    )


def build_all_reports() -> list[SnapshotReport]:
    """Build reports for every snapshot."""
    return [build_report(n) for n in list_snapshots()]


def format_report(report: SnapshotReport, fmt: str = "text") -> str:
    if fmt == "json":
        return json.dumps(
            {
                "name": report.name,
                "key_count": report.key_count,
                "tags": report.tags,
                "pinned": report.pinned,
                "locked": report.locked,
                "rating": report.rating,
                "note": report.note,
                "stats": report.stats,
            },
            indent=2,
        )
    lines = [
        f"Snapshot : {report.name}",
        f"Keys     : {report.key_count}",
        f"Tags     : {', '.join(report.tags) if report.tags else '—'}",
        f"Pinned   : {'yes' if report.pinned else 'no'}",
        f"Locked   : {'yes' if report.locked else 'no'}",
        f"Rating   : {report.rating if report.rating is not None else '—'}",
        f"Note     : {report.note or '—'}",
    ]
    if report.stats:
        lines.append(f"Events   : {report.stats.get('event_count', 0)}")
    return "\n".join(lines)
