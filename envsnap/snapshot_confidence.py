"""Compute a confidence score for a snapshot based on multiple quality signals."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envsnap.storage import load_snapshot, list_snapshots
from envsnap.snapshot_health import check_health
from envsnap.snapshot_freshness import compute_freshness
from envsnap.snapshot_stability import compute_stability
from envsnap.snapshot_score import score_snapshot


@dataclass
class ConfidenceResult:
    name: str
    score: float          # 0.0 – 1.0
    level: str            # high / medium / low
    health_ok: bool
    freshness_level: str
    stability_level: str
    quality_score: float
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "score": round(self.score, 4),
            "level": self.level,
            "health_ok": self.health_ok,
            "freshness_level": self.freshness_level,
            "stability_level": self.stability_level,
            "quality_score": self.quality_score,
            "notes": self.notes,
        }


def _level(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def compute_confidence(name: str) -> ConfidenceResult:
    """Aggregate multiple signals into a single confidence score."""
    health = check_health(name)
    freshness = compute_freshness(name)
    stability = compute_stability(name)
    quality = score_snapshot(name)

    health_ok = health.healthy
    notes: list[str] = []

    # Weighted contributions
    health_contrib = 0.30 if health_ok else 0.0
    if not health_ok:
        notes.append("Health checks failed")

    freshness_weight = {"fresh": 0.25, "stale": 0.15, "aged": 0.05, "unknown": 0.10}
    freshness_contrib = freshness_weight.get(freshness.level, 0.10)
    if freshness.level in ("stale", "aged"):
        notes.append(f"Freshness is {freshness.level}")

    stability_weight = {"stable": 0.25, "moderate": 0.15, "unstable": 0.05}
    stability_contrib = stability_weight.get(stability.level, 0.10)
    if stability.level == "unstable":
        notes.append("Snapshot is unstable (high churn)")

    quality_norm = (quality.score / 100.0) * 0.20

    total = health_contrib + freshness_contrib + stability_contrib + quality_norm
    total = max(0.0, min(1.0, total))

    return ConfidenceResult(
        name=name,
        score=total,
        level=_level(total),
        health_ok=health_ok,
        freshness_level=freshness.level,
        stability_level=stability.level,
        quality_score=quality.score,
        notes=notes,
    )


def compute_all_confidence() -> list[ConfidenceResult]:
    return [compute_confidence(n) for n in list_snapshots()]


def format_confidence(result: ConfidenceResult) -> str:
    lines = [
        f"Snapshot : {result.name}",
        f"Confidence: {result.level.upper()} ({result.score:.0%})",
        f"  Health    : {'ok' if result.health_ok else 'FAIL'}",
        f"  Freshness : {result.freshness_level}",
        f"  Stability : {result.stability_level}",
        f"  Quality   : {result.quality_score}/100",
    ]
    if result.notes:
        lines.append("  Notes     : " + "; ".join(result.notes))
    return "\n".join(lines)
