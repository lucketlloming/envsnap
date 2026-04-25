"""Tests for snapshot sensitivity analysis."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envsnap.snapshot_sensitivity import (
    _classify_key,
    analyze_sensitivity,
    analyze_all_sensitivity,
    format_sensitivity,
    LEVEL_SENSITIVE,
    LEVEL_MODERATE,
    LEVEL_PUBLIC,
)
from envsnap.cli_sensitivity import sensitivity_cmd


# ---------------------------------------------------------------------------
# Unit tests – _classify_key
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", ["API_KEY", "db_password", "SECRET_TOKEN", "private_key"])
def test_classify_sensitive(key):
    assert _classify_key(key) == LEVEL_SENSITIVE


@pytest.mark.parametrize("key", ["DB_HOST", "APP_URL", "DATABASE_NAME", "login_user"])
def test_classify_moderate(key):
    assert _classify_key(key) == LEVEL_MODERATE


@pytest.mark.parametrize("key", ["APP_ENV", "LOG_LEVEL", "WORKERS", "TIMEOUT"])
def test_classify_public(key):
    assert _classify_key(key) == LEVEL_PUBLIC


# ---------------------------------------------------------------------------
# Unit tests – analyze_sensitivity
# ---------------------------------------------------------------------------

def _patch(data):
    return patch("envsnap.snapshot_sensitivity.load_snapshot", return_value=data)


def test_analyze_all_sensitive():
    with _patch({"API_KEY": "abc", "DB_PASSWORD": "xyz"}):
        result = analyze_sensitivity("snap1")
    assert sorted(result.sensitive) == ["API_KEY", "DB_PASSWORD"]
    assert result.moderate == []
    assert result.public == []
    assert result.score == pytest.approx(1.0)


def test_analyze_mixed():
    with _patch({"API_KEY": "x", "DB_HOST": "localhost", "APP_ENV": "prod"}):
        result = analyze_sensitivity("snap2")
    assert "API_KEY" in result.sensitive
    assert "DB_HOST" in result.moderate
    assert "APP_ENV" in result.public
    assert 0.0 < result.score < 1.0


def test_analyze_empty_snapshot():
    with _patch({}):
        result = analyze_sensitivity("empty")
    assert result.score == 0.0
    assert result.sensitive == []


def test_format_sensitivity_contains_snapshot_name():
    with _patch({"TOKEN": "t", "APP_ENV": "dev"}):
        result = analyze_sensitivity("mysnap")
    text = format_sensitivity(result)
    assert "mysnap" in text
    assert "TOKEN" in text


def test_analyze_all_calls_each_snapshot():
    with patch("envsnap.snapshot_sensitivity.list_snapshots", return_value=["a", "b"]), \
         patch("envsnap.snapshot_sensitivity.load_snapshot", return_value={"KEY": "v"}):
        results = analyze_all_sensitivity()
    assert len(results) == 2
    assert {r.snapshot for r in results} == {"a", "b"}


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

runner = CliRunner()


def test_cli_sensitivity_show_text():
    with _patch({"API_KEY": "s", "APP_ENV": "prod"}):
        res = runner.invoke(sensitivity_cmd, ["show", "snap1"])
    assert res.exit_code == 0
    assert "snap1" in res.output


def test_cli_sensitivity_show_json():
    with _patch({"API_KEY": "s"}):
        res = runner.invoke(sensitivity_cmd, ["show", "snap1", "--format", "json"])
    import json
    data = json.loads(res.output)
    assert data["snapshot"] == "snap1"
    assert "API_KEY" in data["sensitive"]


def test_cli_sensitivity_show_missing_snapshot():
    with patch("envsnap.snapshot_sensitivity.load_snapshot", side_effect=FileNotFoundError):
        res = runner.invoke(sensitivity_cmd, ["show", "ghost"])
    assert res.exit_code != 0
    assert "not found" in res.output


def test_cli_sensitivity_all_min_score_filters():
    with patch("envsnap.snapshot_sensitivity.list_snapshots", return_value=["a"]), \
         patch("envsnap.snapshot_sensitivity.load_snapshot", return_value={"APP_ENV": "dev"}):
        res = runner.invoke(sensitivity_cmd, ["all", "--min-score", "0.5"])
    assert "No snapshots match" in res.output
