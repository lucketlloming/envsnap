"""Tests for envsnap.lint."""
import pytest
from unittest.mock import patch
from click.testing import CliRunner
from envsnap.lint import lint_snapshot, format_lint_report
from envsnap.cli_lint import lint_cmd


def _patch(data):
    return patch("envsnap.lint.load_snapshot", return_value=data)


def test_no_issues():
    with _patch({"HOME": "/home/user", "SHELL": "/bin/bash"}):
        issues = lint_snapshot("snap")
    assert issues == []


def test_empty_value_warning():
    with _patch({"MY_VAR": ""}):
        issues = lint_snapshot("snap")
    assert any(i["key"] == "MY_VAR" and i["severity"] == "warning" for i in issues)


def test_whitespace_value_warning():
    with _patch({"MY_VAR": "  hello  "}):
        issues = lint_snapshot("snap")
    assert any(i["key"] == "MY_VAR" and "whitespace" in i["message"] for i in issues)


def test_sensitive_key_info():
    with _patch({"DB_PASSWORD": "secret123"}):
        issues = lint_snapshot("snap")
    assert any(i["key"] == "DB_PASSWORD" and i["severity"] == "info" for i in issues)


def test_format_no_issues():
    report = format_lint_report("snap", [])
    assert "no issues" in report


def test_format_with_issues():
    issues = [{"key": "X", "severity": "warning", "message": "Empty value"}]
    report = format_lint_report("snap", issues)
    assert "WARNING" in report
    assert "X" in report


def test_cli_lint_run_clean():
    runner = CliRunner()
    with _patch({"HOME": "/home/user"}):
        result = runner.invoke(lint_cmd, ["run", "snap"])
    assert result.exit_code == 0
    assert "no issues" in result.output


def test_cli_lint_run_json():
    runner = CliRunner()
    with _patch({"API_TOKEN": "abc"}):
        result = runner.invoke(lint_cmd, ["run", "snap", "--format", "json"])
    import json
    out = json.loads(result.output)
    assert out["snapshot"] == "snap"
    assert isinstance(out["issues"], list)


def test_cli_lint_run_missing_snapshot():
    from envsnap.storage import StorageError
    runner = CliRunner()
    with patch("envsnap.lint.load_snapshot", side_effect=StorageError("not found")):
        result = runner.invoke(lint_cmd, ["run", "missing"])
    assert result.exit_code != 0
    assert "not found" in result.output
