"""Tests for envsnap.snapshot_complexity."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envsnap.snapshot_complexity import (
    ComplexityResult,
    _level,
    compute_complexity,
    compute_all_complexity,
    format_complexity,
)
from envsnap.cli_complexity import complexity_cmd


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _patch(snapshot_data: dict, names: list[str] | None = None):
    """Context manager that stubs load_snapshot and list_snapshots."""
    _names = names or list(snapshot_data.keys())
    return patch.multiple(
        "envsnap.snapshot_complexity",
        load_snapshot=lambda name: snapshot_data[name],
        list_snapshots=lambda: _names,
    )


# ---------------------------------------------------------------------------
# unit tests
# ---------------------------------------------------------------------------

def test_level_low():
    assert _level(0.0) == "low"
    assert _level(29.9) == "low"


def test_level_medium():
    assert _level(30.0) == "medium"
    assert _level(59.9) == "medium"


def test_level_high():
    assert _level(60.0) == "high"
    assert _level(100.0) == "high"


def test_compute_complexity_empty_snapshot():
    with _patch({"empty": {}}):
        result = compute_complexity("empty")
    assert result.key_count == 0
    assert result.score == 0.0
    assert result.level == "low"


def test_compute_complexity_basic_fields():
    data = {"snap": {"FOO": "bar", "BAZ": "qux", "QUX": "bar"}}
    with _patch(data):
        result = compute_complexity("snap")
    assert result.name == "snap"
    assert result.key_count == 3
    assert result.unique_value_count == 2  # "bar" duplicated
    assert result.duplication_ratio == pytest.approx(1 / 3, rel=1e-3)


def test_compute_complexity_no_duplicates():
    data = {"snap": {"A": "1", "B": "2", "C": "3"}}
    with _patch(data):
        result = compute_complexity("snap")
    assert result.duplication_ratio == pytest.approx(0.0)
    assert result.unique_value_count == 3


def test_compute_all_complexity_returns_list():
    data = {
        "alpha": {"X": "1"},
        "beta": {"Y": "2", "Z": "3"},
    }
    with _patch(data):
        results = compute_all_complexity()
    assert len(results) == 2
    names = {r.name for r in results}
    assert names == {"alpha", "beta"}


def test_format_complexity_contains_key_fields():
    data = {"snap": {"MY_VAR": "hello"}}
    with _patch(data):
        result = compute_complexity("snap")
    text = format_complexity(result)
    assert "snap" in text
    assert "Score" in text
    assert "Level" in text


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

runner = CliRunner()


def test_cli_complexity_show_text():
    data = {"mysnap": {"KEY": "val"}}
    with patch("envsnap.cli_complexity.compute_complexity", return_value=compute_complexity.__wrapped__("mysnap") if hasattr(compute_complexity, "__wrapped__") else None) as mock_cc:
        # Use a real result object instead
        with _patch(data):
            result_obj = compute_complexity("mysnap")
        with patch("envsnap.cli_complexity.compute_complexity", return_value=result_obj):
            res = runner.invoke(complexity_cmd, ["show", "mysnap"])
    assert res.exit_code == 0
    assert "mysnap" in res.output


def test_cli_complexity_show_json():
    data = {"mysnap": {"KEY": "val"}}
    with _patch(data):
        result_obj = compute_complexity("mysnap")
    with patch("envsnap.cli_complexity.compute_complexity", return_value=result_obj):
        res = runner.invoke(complexity_cmd, ["show", "mysnap", "--format", "json"])
    assert res.exit_code == 0
    import json
    parsed = json.loads(res.output)
    assert parsed["name"] == "mysnap"
    assert "score" in parsed


def test_cli_complexity_show_missing_snapshot():
    with patch("envsnap.cli_complexity.compute_complexity", side_effect=FileNotFoundError):
        res = runner.invoke(complexity_cmd, ["show", "ghost"])
    assert res.exit_code != 0
    assert "not found" in res.output.lower()


def test_cli_complexity_all_no_snapshots():
    with patch("envsnap.cli_complexity.list_snapshots", return_value=[]):
        res = runner.invoke(complexity_cmd, ["all"])
    assert res.exit_code == 0
    assert "No snapshots" in res.output
