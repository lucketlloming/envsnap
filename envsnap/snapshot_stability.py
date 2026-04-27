"""Snapshot stability analysis: measures how often a snapshot changes over time."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envsnap.history import get_history
from envsnap.storage import list_snapshots


@dataclass
class StabilityResult:
    name: str
    total_events: int
    change_events: int
    stability_score: float  # 0.0 (very unstable) – 1.0 (perfectly stable)
    level: str
    note: str

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "total_events": self.total_events,
            "change_events": self.change_events,
            "stability_score": round(self.stability_score, 4),
            "level": self.level,
            "note": self.note,
        }


_CHANGE_EVENT_TYPES = {"snap", "restore", "patch", "rollback", "clone", "merge"}


def _level(score: float) -> tuple[str, str]:
    if score >= 0.85:
        return "stable", "Snapshot changes infrequently."
    if score >= 0.50:
        return "moderate", "Snapshot changes occasionally."
    return "unstable", "Snapshot changes very frequently."


def compute_stability(name: str) -> StabilityResult:
    """Compute stability for a single snapshot."""
    history = get_history(name)
    total = len(history)
    changes = sum(1 for e in history if e.get("event") in _CHANGE_EVENT_TYPES)

    if total == 0:
        score = 1.0
    else:
        score = max(0.0, 1.0 - (changes / total))

    lvl, note = _level(score)
    return StabilityResult(
        name=name,
        total_events=total,
        change_events=changes,
        stability_score=score,
        level=lvl,
        note=note,
    )


def compute_all_stability() -> list[StabilityResult]:
    """Compute stability for every known snapshot."""
    return [compute_stability(n) for n in list_snapshots()]


def format_stability(result: StabilityResult) -> str:
    lines = [
        f"Snapshot : {result.name}",
        f"Level    : {result.level}",
        f"Score    : {result.stability_score:.2%}",
        f"Changes  : {result.change_events} / {result.total_events} events",
        f"Note     : {result.note}",
    ]
    return "\n".join(lines)
