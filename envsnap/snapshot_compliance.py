"""Snapshot compliance checking — validates snapshots against a defined policy."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from envsnap.storage import load_snapshot, list_snapshots


@dataclass
class ComplianceViolation:
    rule: str
    severity: str  # "error" | "warning"
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"rule": self.rule, "severity": self.severity, "message": self.message}


@dataclass
class ComplianceResult:
    snapshot: str
    violations: list[ComplianceViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(v.severity == "error" for v in self.violations)

    def as_dict(self) -> dict[str, Any]:
        return {
            "snapshot": self.snapshot,
            "passed": self.passed,
            "violations": [v.as_dict() for v in self.violations],
        }


def _check_no_empty_values(name: str, data: dict[str, str]) -> list[ComplianceViolation]:
    return [
        ComplianceViolation("no_empty_values", "error", f"Key '{k}' has an empty value")
        for k, v in data.items()
        if v == ""
    ]


def _check_uppercase_keys(name: str, data: dict[str, str]) -> list[ComplianceViolation]:
    return [
        ComplianceViolation("uppercase_keys", "warning", f"Key '{k}' is not uppercase")
        for k in data
        if k != k.upper()
    ]


def _check_minimum_keys(name: str, data: dict[str, str], minimum: int = 1) -> list[ComplianceViolation]:
    if len(data) < minimum:
        return [
            ComplianceViolation(
                "minimum_keys",
                "error",
                f"Snapshot has {len(data)} key(s); minimum required is {minimum}",
            )
        ]
    return []


_CHECKS = [_check_no_empty_values, _check_uppercase_keys, _check_minimum_keys]


def check_compliance(snapshot_name: str) -> ComplianceResult:
    """Run all compliance checks against a single snapshot."""
    data = load_snapshot(snapshot_name)
    result = ComplianceResult(snapshot=snapshot_name)
    for check in _CHECKS:
        result.violations.extend(check(snapshot_name, data))
    return result


def check_all_compliance() -> list[ComplianceResult]:
    """Run compliance checks against every stored snapshot."""
    return [check_compliance(name) for name in list_snapshots()]


def format_compliance(result: ComplianceResult) -> str:
    lines = [f"Snapshot : {result.snapshot}", f"Status   : {'PASS' if result.passed else 'FAIL'}"]
    if result.violations:
        lines.append("Violations:")
        for v in result.violations:
            lines.append(f"  [{v.severity.upper()}] {v.rule}: {v.message}")
    else:
        lines.append("No violations found.")
    return "\n".join(lines)
