"""Snapshot recommendation engine — suggests actions based on snapshot state."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envsnap.storage import load_snapshot, list_snapshots
from envsnap.snapshot_health import check_health
from envsnap.snapshot_score import score_snapshot
from envsnap.expire import get_expiry
from envsnap.lock import is_locked


@dataclass
class Recommendation:
    snapshot: str
    level: str          # "info" | "warning" | "action"
    code: str
    message: str

    def as_dict(self) -> dict:
        return {
            "snapshot": self.snapshot,
            "level": self.level,
            "code": self.code,
            "message": self.message,
        }


def recommend(snapshot_name: str) -> List[Recommendation]:
    """Return a list of recommendations for a single snapshot."""
    recs: List[Recommendation] = []

    data = load_snapshot(snapshot_name)

    # Low key count
    if len(data) == 0:
        recs.append(Recommendation(snapshot_name, "warning", "EMPTY_SNAPSHOT",
                                   "Snapshot has no keys — consider deleting or repopulating it."))
    elif len(data) < 3:
        recs.append(Recommendation(snapshot_name, "info", "LOW_KEY_COUNT",
                                   f"Snapshot has only {len(data)} key(s); it may be incomplete."))

    # Health check
    health = check_health(snapshot_name)
    if not health.healthy:
        for issue in health.issues:
            recs.append(Recommendation(snapshot_name, "warning", "HEALTH_ISSUE",
                                       f"Health issue: {issue}"))

    # Score check
    result = score_snapshot(snapshot_name)
    if result.score < 50:
        recs.append(Recommendation(snapshot_name, "action", "LOW_SCORE",
                                   f"Score is {result.score}/100 — review lint and validation issues."))
    elif result.score < 75:
        recs.append(Recommendation(snapshot_name, "info", "MODERATE_SCORE",
                                   f"Score is {result.score}/100 — minor improvements possible."))

    # Expiry check
    try:
        expiry = get_expiry(snapshot_name)
        if expiry is not None:
            recs.append(Recommendation(snapshot_name, "info", "HAS_EXPIRY",
                                       f"Snapshot expires on {expiry} — ensure it is still needed."))
    except Exception:
        pass

    # Lock check
    try:
        if is_locked(snapshot_name):
            recs.append(Recommendation(snapshot_name, "info", "IS_LOCKED",
                                       "Snapshot is locked; unlock before making changes."))
    except Exception:
        pass

    return recs


def recommend_all() -> List[Recommendation]:
    """Return recommendations for every snapshot."""
    results: List[Recommendation] = []
    for name in list_snapshots():
        results.extend(recommend(name))
    return results


def format_recommendations(recs: List[Recommendation], fmt: str = "text") -> str:
    if fmt == "json":
        import json
        return json.dumps([r.as_dict() for r in recs], indent=2)

    if not recs:
        return "No recommendations."

    lines = []
    for r in recs:
        icon = {"info": "ℹ", "warning": "⚠", "action": "✖"}.get(r.level, "•")
        lines.append(f"{icon} [{r.snapshot}] {r.code}: {r.message}")
    return "\n".join(lines)
