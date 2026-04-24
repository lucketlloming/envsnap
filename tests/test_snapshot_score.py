"""Tests for envsnap.snapshot_score."""
from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from envsnap.snapshot_score import score_snapshot, ScoreResult, format_score


def _patch(data, lint_issues=None, val_issues=None):
    """Helper: patch load_snapshot, lint_snapshot, validate_snapshot."""
    lint_issues = lint_issues or []
    val_issues = val_issues or []
    return (
        patch("envsnap.snapshot_score.load_snapshot", return_value=data),
        patch("envsnap.snapshot_score.lint_snapshot", return_value=lint_issues),
        patch("envsnap.snapshot_score.validate_snapshot", return_value=val_issues),
    )


def test_perfect_score_clean_snapshot():
    p1, p2, p3 = _patch({"KEY": "value", "OTHER": "data"})
    with p1, p2, p3:
        result = score_snapshot("mysnap")
    assert result.score == 100
    assert result.penalties == []
    assert result.snapshot == "mysnap"


def test_score_reduced_by_empty_values():
    p1, p2, p3 = _patch({"KEY": "", "OTHER": ""})
    with p1, p2, p3:
        result = score_snapshot("mysnap")
    # 2 empty keys * 3 penalty = 6
    assert result.score == 94
    assert result.breakdown["empty_penalty"] == 6
    assert any("empty:KEY" in p for p in result.penalties)
    assert any("empty:OTHER" in p for p in result.penalties)


def test_score_reduced_by_lint_issues():
    issue = MagicMock(key="BAD_KEY", message="suspicious")
    p1, p2, p3 = _patch({"BAD_KEY": "x"}, lint_issues=[issue])
    with p1, p2, p3:
        result = score_snapshot("mysnap")
    assert result.breakdown["lint_penalty"] == 5
    assert result.score == 95


def test_score_reduced_by_validation_errors():
    issue = MagicMock(key="K", message="error!", level="error")
    p1, p2, p3 = _patch({"K": "v"}, val_issues=[issue])
    with p1, p2, p3:
        result = score_snapshot("mysnap")
    assert result.breakdown["validate_penalty"] == 10
    assert result.score == 90


def test_score_capped_at_zero():
    lint_issues = [MagicMock(key=f"K{i}", message="x") for i in range(20)]
    p1, p2, p3 = _patch({f"K{i}": "" for i in range(20)}, lint_issues=lint_issues)
    with p1, p2, p3:
        result = score_snapshot("mysnap")
    assert result.score == 0


def test_format_score_contains_name_and_score():
    result = ScoreResult(
        snapshot="demo",
        score=72,
        breakdown={"lint_penalty": 10, "empty_penalty": 18},
        penalties=["empty:FOO"],
    )
    text = format_score(result)
    assert "demo" in text
    assert "72/100" in text
    assert "lint_penalty" in text
    assert "empty:FOO" in text
