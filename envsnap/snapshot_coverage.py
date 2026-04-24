"""Snapshot coverage: measure how many expected keys are present in a snapshot."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envsnap.storage import load_snapshot, list_snapshots


@dataclass
class CoverageResult:
    snapshot: str
    expected: List[str]
    present: List[str]
    missing: List[str]
    coverage_pct: float

    def as_dict(self) -> dict:
        return {
            "snapshot": self.snapshot,
            "expected": self.expected,
            "present": self.present,
            "missing": self.missing,
            "coverage_pct": round(self.coverage_pct, 2),
        }


def compute_coverage(snapshot_name: str, expected_keys: List[str]) -> CoverageResult:
    """Compute how many of the expected_keys are present in the snapshot."""
    data = load_snapshot(snapshot_name)
    present = [k for k in expected_keys if k in data]
    missing = [k for k in expected_keys if k not in data]
    total = len(expected_keys)
    pct = (len(present) / total * 100.0) if total > 0 else 100.0
    return CoverageResult(
        snapshot=snapshot_name,
        expected=list(expected_keys),
        present=present,
        missing=missing,
        coverage_pct=pct,
    )


def coverage_all(expected_keys: List[str]) -> List[CoverageResult]:
    """Compute coverage for every snapshot against the expected key list."""
    return [compute_coverage(name, expected_keys) for name in list_snapshots()]


def format_coverage(result: CoverageResult, fmt: str = "text") -> str:
    if fmt == "json":
        import json
        return json.dumps(result.as_dict(), indent=2)

    lines = [
        f"Snapshot : {result.snapshot}",
        f"Coverage : {result.coverage_pct:.1f}%  "
        f"({len(result.present)}/{len(result.expected)} keys)",
    ]
    if result.missing:
        lines.append("Missing  : " + ", ".join(result.missing))
    else:
        lines.append("Missing  : (none)")
    return "\n".join(lines)
