"""Tests for envsnap.snapshot_compliance."""
from unittest.mock import patch

import pytest

from envsnap.snapshot_compliance import (
    ComplianceResult,
    ComplianceViolation,
    check_all_compliance,
    check_compliance,
    format_compliance,
)

_MOD = "envsnap.snapshot_compliance"


def _patch(snapshots: dict[str, dict]):
    """Context manager that patches load_snapshot and list_snapshots."""
    names = list(snapshots.keys())

    def _load(name):
        if name not in snapshots:
            raise FileNotFoundError(name)
        return snapshots[name]

    return (
        patch(f"{_MOD}.list_snapshots", return_value=names),
        patch(f"{_MOD}.load_snapshot", side_effect=_load),
    )


def test_passes_clean_snapshot():
    p_list, p_load = _patch({"prod": {"APP_ENV": "production", "PORT": "8080"}})
    with p_list, p_load:
        result = check_compliance("prod")
    assert result.passed
    assert result.violations == []


def test_fails_on_empty_value():
    p_list, p_load = _patch({"prod": {"APP_ENV": ""}})
    with p_list, p_load:
        result = check_compliance("prod")
    assert not result.passed
    errors = [v for v in result.violations if v.severity == "error"]
    assert any("APP_ENV" in v.message for v in errors)


def test_warning_on_lowercase_key():
    p_list, p_load = _patch({"dev": {"app_env": "dev"}})
    with p_list, p_load:
        result = check_compliance("dev")
    warnings = [v for v in result.violations if v.severity == "warning"]
    assert any("app_env" in v.message for v in warnings)


def test_fails_on_empty_snapshot():
    p_list, p_load = _patch({"empty": {}})
    with p_list, p_load:
        result = check_compliance("empty")
    assert not result.passed
    assert any(v.rule == "minimum_keys" for v in result.violations)


def test_check_all_compliance_returns_all():
    snaps = {
        "a": {"KEY": "val"},
        "b": {"OTHER": ""},
    }
    p_list, p_load = _patch(snaps)
    with p_list, p_load:
        results = check_all_compliance()
    assert len(results) == 2
    names = {r.snapshot for r in results}
    assert names == {"a", "b"}


def test_format_compliance_pass():
    result = ComplianceResult(snapshot="prod", violations=[])
    text = format_compliance(result)
    assert "PASS" in text
    assert "No violations" in text


def test_format_compliance_fail():
    v = ComplianceViolation("no_empty_values", "error", "Key 'X' has an empty value")
    result = ComplianceResult(snapshot="dev", violations=[v])
    text = format_compliance(result)
    assert "FAIL" in text
    assert "[ERROR]" in text
    assert "Key 'X'" in text


def test_as_dict_structure():
    v = ComplianceViolation("uppercase_keys", "warning", "Key 'x' is not uppercase")
    result = ComplianceResult(snapshot="s", violations=[v])
    d = result.as_dict()
    assert d["snapshot"] == "s"
    assert isinstance(d["violations"], list)
    assert d["violations"][0]["severity"] == "warning"
