"""Snapshot risk assessment: evaluates risk level based on sensitivity, complexity, and health."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envsnap.snapshot_sensitivity import analyze_sensitivity, SensitivityResult
from envsnap.snapshot_complexity import compute_complexity, ComplexityResult
from envsnap.snapshot_health import check_health, HealthResult


@dataclass
class RiskResult:
    snapshot: str
    score: float  # 0.0 (no risk) to 1.0 (max risk)
    level: str   # "low", "medium", "high", "critical"
    factors: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "snapshot": self.snapshot,
            "score": round(self.score, 3),
            "level": self.level,
            "factors": self.factors,
        }


def _level(score: float) -> str:
    if score >= 0.75:
        return "critical"
    if score >= 0.5:
        return "high"
    if score >= 0.25:
        return "medium"
    return "low"


def assess_risk(snapshot_name: str) -> RiskResult:
    """Compute a composite risk score for the given snapshot."""
    factors: list[str] = []
    score = 0.0

    sensitivity: SensitivityResult = analyze_sensitivity(snapshot_name)
    high_sensitive = len(sensitivity.sensitive_keys)
    moderate_sensitive = len(sensitivity.moderate_keys)
    if high_sensitive > 0:
        contribution = min(0.4, high_sensitive * 0.1)
        score += contribution
        factors.append(f"{high_sensitive} sensitive key(s) detected")
    if moderate_sensitive > 0:
        contribution = min(0.15, moderate_sensitive * 0.05)
        score += contribution
        factors.append(f"{moderate_sensitive} moderate-sensitivity key(s) detected")

    complexity: ComplexityResult = compute_complexity(snapshot_name)
    if complexity.level == "high":
        score += 0.2
        factors.append("high complexity")
    elif complexity.level == "medium":
        score += 0.1
        factors.append("medium complexity")

    health: HealthResult = check_health(snapshot_name)
    if not health.healthy:
        error_count = sum(1 for i in health.issues if i.get("severity") == "error")
        warn_count = sum(1 for i in health.issues if i.get("severity") == "warning")
        score += min(0.25, error_count * 0.1 + warn_count * 0.05)
        if error_count:
            factors.append(f"{error_count} health error(s)")
        if warn_count:
            factors.append(f"{warn_count} health warning(s)")

    score = min(1.0, score)
    return RiskResult(
        snapshot=snapshot_name,
        score=score,
        level=_level(score),
        factors=factors,
    )


def assess_all_risk(snapshot_names: list[str]) -> list[RiskResult]:
    return [assess_risk(name) for name in snapshot_names]


def format_risk(result: RiskResult) -> str:
    lines = [
        f"Snapshot : {result.snapshot}",
        f"Risk     : {result.level.upper()} (score={result.score:.3f})",
    ]
    if result.factors:
        lines.append("Factors  :")
        for f in result.factors:
            lines.append(f"  - {f}")
    else:
        lines.append("Factors  : none")
    return "\n".join(lines)
