"""Snapshot maturity scoring based on age, activity, and metadata richness."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from envsnap.history import get_history
from envsnap.notes import get_note
from envsnap.pin import get_pin
from envsnap.storage import load_snapshot, list_snapshots


_MAX_SCORE = 100


@dataclass
class MaturityResult:
    name: str
    score: int
    level: str
    breakdown: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "score": self.score,
            "level": self.level,
            "breakdown": self.breakdown,
        }


def _level(score: int) -> str:
    if score >= 80:
        return "mature"
    if score >= 50:
        return "developing"
    return "nascent"


def score_maturity(name: str) -> MaturityResult:
    """Compute a maturity score for a snapshot."""
    data = load_snapshot(name)
    breakdown: dict[str, int] = {}

    # Key richness: up to 30 pts
    key_count = len(data)
    key_pts = min(key_count * 3, 30)
    breakdown["key_richness"] = key_pts

    # Activity: up to 30 pts (based on number of history events)
    events = get_history(name)
    activity_pts = min(len(events) * 5, 30)
    breakdown["activity"] = activity_pts

    # Has note: 15 pts
    note_pts = 15 if get_note(name) else 0
    breakdown["has_note"] = note_pts

    # Is pinned: 15 pts
    pin_pts = 15 if get_pin(name) else 0
    breakdown["is_pinned"] = pin_pts

    # Non-empty values: up to 10 pts
    non_empty = sum(1 for v in data.values() if v and v.strip())
    empty_ratio = non_empty / key_count if key_count else 0
    quality_pts = round(empty_ratio * 10)
    breakdown["value_quality"] = quality_pts

    total = sum(breakdown.values())
    total = min(total, _MAX_SCORE)
    return MaturityResult(name=name, score=total, level=_level(total), breakdown=breakdown)


def score_all_maturity() -> list[MaturityResult]:
    return [score_maturity(n) for n in list_snapshots()]


def format_maturity(result: MaturityResult) -> str:
    lines = [
        f"Snapshot : {result.name}",
        f"Score    : {result.score}/{_MAX_SCORE} ({result.level})",
        "Breakdown:",
    ]
    for key, pts in result.breakdown.items():
        lines.append(f"  {key:<20} {pts:>3} pts")
    return "\n".join(lines)
