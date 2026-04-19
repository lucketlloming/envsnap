"""Validate snapshot data against simple rule sets."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from envsnap.storage import load_snapshot


@dataclass
class ValidationIssue:
    key: str
    message: str
    severity: str = "error"  # error | warning


@dataclass
class ValidationRule:
    name: str
    check: Callable[[str, str], Optional[ValidationIssue]]


_rules: List[ValidationRule] = []


def rule(name: str) -> Callable:
    """Decorator to register a validation rule."""
    def decorator(fn: Callable) -> Callable:
        _rules.append(ValidationRule(name=name, check=fn))
        return fn
    return decorator


@rule("no_empty_value")
def check_empty(key: str, value: str) -> Optional[ValidationIssue]:
    if value == "":
        return ValidationIssue(key=key, message="Value is empty", severity="error")
    return None


@rule("no_whitespace_only")
def check_whitespace(key: str, value: str) -> Optional[ValidationIssue]:
    if value.strip() == "" and value != "":
        return ValidationIssue(key=key, message="Value is whitespace only", severity="warning")
    return None


@rule("key_uppercase")
def check_uppercase(key: str, value: str) -> Optional[ValidationIssue]:
    if key != key.upper():
        return ValidationIssue(key=key, message="Key is not uppercase", severity="warning")
    return None


def validate_snapshot(name: str) -> List[ValidationIssue]:
    """Run all rules against a named snapshot and return issues."""
    data = load_snapshot(name)
    issues: List[ValidationIssue] = []
    for key, value in data.items():
        for r in _rules:
            issue = r.check(key, value)
            if issue:
                issues.append(issue)
    return issues


def format_validation_report(issues: List[ValidationIssue], fmt: str = "text") -> str:
    if fmt == "json":
        import json
        return json.dumps([{"key": i.key, "message": i.message, "severity": i.severity} for i in issues], indent=2)
    if not issues:
        return "No issues found."
    lines = []
    for i in issues:
        lines.append(f"[{i.severity.upper()}] {i.key}: {i.message}")
    return "\n".join(lines)
