"""Snapshot readiness assessment — evaluates whether a snapshot is ready for production use."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envsnap.snapshot_health import check_health
from envsnap.snapshot_maturity import score_maturity
from envsnap.snapshot_compliance import check_compliance
from envsnap.storage import list_snapshots


@dataclass
class ReadinessResult:
    snapshot: str
    score: float          # 0.0 – 100.0
    level: str            # "ready" | "nearly-ready" | "not-ready"
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "snapshot": self.snapshot,
            "score": round(self.score, 2),
            "level": self.level,
            "blockers": self.blockers,
            "warnings": self.warnings,
        }


def _level(score: float) -> str:
    if score >= 80:
        return "ready"
    if score >= 50:
        return "nearly-ready"
    return "not-ready"


def assess_readiness(snapshot_name: str) -> ReadinessResult:
    blockers: list[str] = []
    warnings: list[str] = []
    score = 100.0

    health = check_health(snapshot_name)
    if not health.healthy:
        for issue in health.issues:
            if issue.get("severity") == "error":
                blockers.append(issue["message"])
                score -= 20
            else:
                warnings.append(issue["message"])
                score -= 5

    maturity = score_maturity(snapshot_name)
    if maturity.level == "nascent":
        blockers.append("Snapshot maturity is nascent — needs more history.")
        score -= 20
    elif maturity.level == "developing":
        warnings.append("Snapshot maturity is developing.")
        score -= 10

    compliance = check_compliance(snapshot_name)
    if not compliance.passed:
        for v in compliance.violations:
            if v.severity == "error":
                blockers.append(v.message)
                score -= 15
            else:
                warnings.append(v.message)
                score -= 5

    score = max(0.0, score)
    return ReadinessResult(
        snapshot=snapshot_name,
        score=score,
        level=_level(score),
        blockers=blockers,
        warnings=warnings,
    )


def assess_all_readiness() -> list[ReadinessResult]:
    return [assess_readiness(name) for name in list_snapshots()]


def format_readiness(result: ReadinessResult) -> str:
    lines = [
        f"Snapshot : {result.snapshot}",
        f"Score    : {result.score:.1f}/100",
        f"Level    : {result.level}",
    ]
    if result.blockers:
        lines.append("Blockers :")
        for b in result.blockers:
            lines.append(f"  [!] {b}")
    if result.warnings:
        lines.append("Warnings :")
        for w in result.warnings:
            lines.append(f"  [~] {w}")
    return "\n".join(lines)
