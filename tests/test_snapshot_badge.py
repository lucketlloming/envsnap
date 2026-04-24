"""Tests for envsnap.snapshot_badge."""
from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from envsnap.snapshot_badge import (
    generate_badge,
    _level_from_score,
    Badge,
    _LEVEL_COLOR,
)
from envsnap.snapshot_score import ScoreResult


def _fake_score(score: int) -> ScoreResult:
    return ScoreResult(
        snapshot="mysnap",
        score=score,
        lint_issues=[],
        validation_errors=[],
        empty_keys=[],
    )


def _patch(score: int):
    return patch(
        "envsnap.snapshot_badge.score_snapshot",
        return_value=_fake_score(score),
    )


# --- _level_from_score ---

def test_level_excellent():
    assert _level_from_score(95) == "excellent"


def test_level_good():
    assert _level_from_score(75) == "good"


def test_level_fair():
    assert _level_from_score(55) == "fair"


def test_level_poor():
    assert _level_from_score(30) == "poor"


def test_level_boundary_90():
    assert _level_from_score(90) == "excellent"


def test_level_boundary_70():
    assert _level_from_score(70) == "good"


# --- generate_badge ---

def test_generate_badge_fields():
    with _patch(85):
        badge = generate_badge("mysnap")
    assert badge.snapshot == "mysnap"
    assert badge.score == 85
    assert badge.level == "good"
    assert badge.color == _LEVEL_COLOR["good"]
    assert badge.label == "85/100"


def test_generate_badge_poor():
    with _patch(20):
        badge = generate_badge("mysnap")
    assert badge.level == "poor"
    assert badge.color == _LEVEL_COLOR["poor"]


def test_badge_as_dict():
    with _patch(92):
        badge = generate_badge("mysnap")
    d = badge.as_dict()
    assert d["snapshot"] == "mysnap"
    assert d["score"] == 92
    assert d["level"] == "excellent"


def test_badge_as_svg_contains_score():
    with _patch(77):
        badge = generate_badge("mysnap")
    svg = badge.as_svg()
    assert "77/100" in svg
    assert "<svg" in svg


def test_badge_as_markdown():
    with _patch(60):
        badge = generate_badge("mysnap")
    md = badge.as_markdown()
    assert "mysnap" in md
    assert md.startswith("![") 
