"""Snapshot health check: aggregates lint, validation, expiry, and lock status."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envsnap.storage import load_snapshot, list_snapshots
from envsnap.lint import lint_snapshot
from envsnap.validate import validate_snapshot
from envsnap.expire import get_expiry, ExpiryNotFoundError
from envsnap.lock import is_locked


@dataclass
class HealthResult:
    name: str
    key_count: int
    lint_warnings: int
    lint_errors: int
    validation_warnings: int
    validation_errors: int
    is_locked: bool
    expiry_date: Optional[str]
    score: int  # 0-100
    status: str  # healthy / warning / critical
    issues: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "key_count": self.key_count,
            "lint_warnings": self.lint_warnings,
            "lint_errors": self.lint_errors,
            "validation_warnings": self.validation_warnings,
            "validation_errors": self.validation_errors,
            "is_locked": self.is_locked,
            "expiry_date": self.expiry_date,
            "score": self.score,
            "status": self.status,
            "issues": self.issues,
        }


def check_health(name: str) -> HealthResult:
    data = load_snapshot(name)
    issues: list[str] = []

    lint_results = lint_snapshot(name)
    lint_warnings = sum(1 for r in lint_results if r.level == "warning")
    lint_errors = sum(1 for r in lint_results if r.level == "error")
    for r in lint_results:
        issues.append(f"[lint/{r.level}] {r.message}")

    val_results = validate_snapshot(name)
    val_warnings = sum(1 for r in val_results if r.level == "warning")
    val_errors = sum(1 for r in val_results if r.level == "error")
    for r in val_results:
        issues.append(f"[validate/{r.level}] {r.message}")

    locked = is_locked(name)
    expiry: Optional[str] = None
    try:
        expiry_info = get_expiry(name)
        expiry = expiry_info.get("expires_at")
    except ExpiryNotFoundError:
        pass

    penalty = (lint_errors * 15) + (lint_warnings * 5) + (val_errors * 20) + (val_warnings * 5)
    score = max(0, 100 - penalty)

    if score >= 80:
        status = "healthy"
    elif score >= 50:
        status = "warning"
    else:
        status = "critical"

    return HealthResult(
        name=name,
        key_count=len(data),
        lint_warnings=lint_warnings,
        lint_errors=lint_errors,
        validation_warnings=val_warnings,
        validation_errors=val_errors,
        is_locked=locked,
        expiry_date=expiry,
        score=score,
        status=status,
        issues=issues,
    )


def check_all_health() -> list[HealthResult]:
    return [check_health(name) for name in list_snapshots()]


def format_health(result: HealthResult) -> str:
    lines = [
        f"Snapshot : {result.name}",
        f"Status   : {result.status.upper()}",
        f"Score    : {result.score}/100",
        f"Keys     : {result.key_count}",
        f"Locked   : {'yes' if result.is_locked else 'no'}",
        f"Expires  : {result.expiry_date or 'never'}",
    ]
    if result.issues:
        lines.append("Issues:")
        for issue in result.issues:
            lines.append(f"  - {issue}")
    return "\n".join(lines)
