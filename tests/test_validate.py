"""Tests for envsnap.validate."""
import json
import pytest
from unittest.mock import patch

from envsnap.validate import (
    validate_snapshot,
    format_validation_report,
    ValidationIssue,
)


def _patch(data: dict):
    return patch("envsnap.validate.load_snapshot", return_value=data)


def test_no_issues_clean_snapshot():
    with _patch({"HOME": "/home/user", "PATH": "/usr/bin"}):
        issues = validate_snapshot("clean")
    assert issues == []


def test_empty_value_raises_error():
    with _patch({"DATABASE_URL": ""}):
        issues = validate_snapshot("s")
    errors = [i for i in issues if i.severity == "error"]
    assert any(i.key == "DATABASE_URL" for i in errors)


def test_whitespace_only_value_warning():
    with _patch({"SECRET": "   "}):
        issues = validate_snapshot("s")
    warnings = [i for i in issues if i.severity == "warning"]
    assert any(i.key == "SECRET" for i in warnings)


def test_lowercase_key_warning():
    with _patch({"my_var": "hello"}):
        issues = validate_snapshot("s")
    warnings = [i for i in issues if i.severity == "warning"]
    assert any(i.key == "my_var" for i in warnings)


def test_multiple_issues_multiple_keys():
    with _patch({"good": "", "BAD_KEY": "   "}):
        issues = validate_snapshot("s")
    keys = {i.key for i in issues}
    assert "good" in keys
    assert "BAD_KEY" in keys


def test_format_text_no_issues():
    result = format_validation_report([])
    assert result == "No issues found."


def test_format_text_with_issues():
    issues = [
        ValidationIssue(key="X", message="empty", severity="error"),
        ValidationIssue(key="y", message="lowercase", severity="warning"),
    ]
    result = format_validation_report(issues, fmt="text")
    assert "[ERROR] X: empty" in result
    assert "[WARNING] y: lowercase" in result


def test_format_json_output():
    issues = [ValidationIssue(key="A", message="msg", severity="error")]
    result = format_validation_report(issues, fmt="json")
    parsed = json.loads(result)
    assert parsed[0]["key"] == "A"
    assert parsed[0]["severity"] == "error"
