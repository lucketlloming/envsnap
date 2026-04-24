"""Snapshot scoring: compute a quality/health score for a snapshot."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envsnap.storage import load_snapshot
from envsnap.lint import lint_snapshot
from envsnap.validate import validate_snapshot


@dataclass
class ScoreResult:
    snapshot: str
    score: int  # 0-100
    breakdown: Dict[str, int] = field(default_factory=dict)
    penalties: List[str] = field(default_factory=list)


_MAX = 100
_LINT_PENALTY = 5      # per lint issue
_VALIDATE_PENALTY = 10  # per validation error
_EMPTY_PENALTY = 3      # per empty value
_MAX_PENALTY = 80


def score_snapshot(name: str) -> ScoreResult:
    """Compute a 0-100 quality score for the named snapshot."""
    data = load_snapshot(name)
    penalties: List[str] = []
    total_penalty = 0

    # --- lint issues ---
    lint_issues = lint_snapshot(name)
    lint_pen = len(lint_issues) * _LINT_PENALTY
    for issue in lint_issues:
        penalties.append(f"lint:{issue.key}:{issue.message}")

    # --- validation issues ---
    val_issues = validate_snapshot(name)
    val_pen = len([i for i in val_issues if i.level == "error"]) * _VALIDATE_PENALTY
    for issue in val_issues:
        if issue.level == "error":
            penalties.append(f"validate:{issue.key}:{issue.message}")

    # --- empty values ---
    empty_keys = [k for k, v in data.items() if v == ""]
    empty_pen = len(empty_keys) * _EMPTY_PENALTY
    for k in empty_keys:
        penalties.append(f"empty:{k}")

    total_penalty = min(lint_pen + val_pen + empty_pen, _MAX_PENALTY)
    score = max(0, _MAX - total_penalty)

    return ScoreResult(
        snapshot=name,
        score=score,
        breakdown={
            "lint_penalty": lint_pen,
            "validate_penalty": val_pen,
            "empty_penalty": empty_pen,
        },
        penalties=penalties,
    )


def format_score(result: ScoreResult) -> str:
    lines = [
        f"Snapshot : {result.snapshot}",
        f"Score    : {result.score}/100",
        "Breakdown:",
    ]
    for k, v in result.breakdown.items():
        lines.append(f"  {k}: -{v}")
    if result.penalties:
        lines.append("Penalties:")
        for p in result.penalties:
            lines.append(f"  - {p}")
    return "\n".join(lines)
