"""Lint snapshots for common issues like empty values, duplicates, or suspicious keys."""
from __future__ import annotations
from typing import Any
from envsnap.storage import load_snapshot

LINT_RULES = []


def rule(fn):
    LINT_RULES.append(fn)
    return fn


@rule
def check_empty_values(data: dict[str, str]) -> list[dict[str, Any]]:
    return [
        {"key": k, "severity": "warning", "message": "Empty value"}
        for k, v in data.items()
        if v == ""
    ]


@rule
def check_suspicious_keys(data: dict[str, str]) -> list[dict[str, Any]]:
    suspicious = ["PASSWORD", "SECRET", "TOKEN", "API_KEY"]
    issues = []
    for k in data:
        for s in suspicious:
            if s in k.upper():
                issues.append({"key": k, "severity": "info", "message": f"Sensitive key pattern '{s}' detected"})
                break
    return issues


@rule
def check_whitespace_values(data: dict[str, str]) -> list[dict[str, Any]]:
    return [
        {"key": k, "severity": "warning", "message": "Value contains leading/trailing whitespace"}
        for k, v in data.items()
        if v != v.strip()
    ]


def lint_snapshot(name: str) -> list[dict[str, Any]]:
    """Run all lint rules against a snapshot. Returns list of issues."""
    data = load_snapshot(name)
    issues = []
    for rule_fn in LINT_RULES:
        issues.extend(rule_fn(data))
    return issues


def format_lint_report(name: str, issues: list[dict[str, Any]]) -> str:
    if not issues:
        return f"Snapshot '{name}': no issues found."
    lines = [f"Snapshot '{name}' — {len(issues)} issue(s):"]
    for issue in issues:
        lines.append(f"  [{issue['severity'].upper()}] {issue['key']}: {issue['message']}")
    return "\n".join(lines)
