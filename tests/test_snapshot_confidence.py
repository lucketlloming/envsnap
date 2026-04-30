"""Tests for envsnap.snapshot_confidence."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from envsnap.snapshot_confidence import (
    ConfidenceResult,
    _level,
    compute_confidence,
    format_confidence,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _health(healthy: bool):
    m = MagicMock()
    m.healthy = healthy
    return m


def _freshness(level: str):
    m = MagicMock()
    m.level = level
    return m


def _stability(level: str):
    m = MagicMock()
    m.level = level
    return m


def _quality(score: float):
    m = MagicMock()
    m.score = score
    return m


def _patch(health=True, fresh="fresh", stable="stable", quality=90.0):
    return [
        patch("envsnap.snapshot_confidence.check_health", return_value=_health(health)),
        patch("envsnap.snapshot_confidence.compute_freshness", return_value=_freshness(fresh)),
        patch("envsnap.snapshot_confidence.compute_stability", return_value=_stability(stable)),
        patch("envsnap.snapshot_confidence.score_snapshot", return_value=_quality(quality)),
    ]


# ---------------------------------------------------------------------------
# _level
# ---------------------------------------------------------------------------

def test_level_high():
    assert _level(0.80) == "high"

def test_level_medium():
    assert _level(0.60) == "medium"

def test_level_low():
    assert _level(0.20) == "low"

def test_level_boundary_high():
    assert _level(0.75) == "high"

def test_level_boundary_medium():
    assert _level(0.45) == "medium"


# ---------------------------------------------------------------------------
# compute_confidence
# ---------------------------------------------------------------------------

def test_high_confidence_all_green():
    patches = _patch(health=True, fresh="fresh", stable="stable", quality=100.0)
    with patches[0], patches[1], patches[2], patches[3]:
        result = compute_confidence("mysnap")
    assert result.name == "mysnap"
    assert result.level == "high"
    assert result.health_ok is True
    assert result.freshness_level == "fresh"
    assert result.stability_level == "stable"
    assert result.notes == []


def test_low_confidence_all_bad():
    patches = _patch(health=False, fresh="aged", stable="unstable", quality=10.0)
    with patches[0], patches[1], patches[2], patches[3]:
        result = compute_confidence("badsnap")
    assert result.level == "low"
    assert result.health_ok is False
    assert "Health checks failed" in result.notes
    assert any("aged" in n for n in result.notes)
    assert any("unstable" in n for n in result.notes)


def test_medium_confidence_stale_moderate():
    patches = _patch(health=True, fresh="stale", stable="moderate", quality=60.0)
    with patches[0], patches[1], patches[2], patches[3]:
        result = compute_confidence("midsnap")
    assert result.level == "medium"
    assert any("stale" in n for n in result.notes)


def test_score_clamped_to_one():
    patches = _patch(health=True, fresh="fresh", stable="stable", quality=100.0)
    with patches[0], patches[1], patches[2], patches[3]:
        result = compute_confidence("snap")
    assert result.score <= 1.0


# ---------------------------------------------------------------------------
# format_confidence
# ---------------------------------------------------------------------------

def test_format_confidence_text():
    r = ConfidenceResult(
        name="demo",
        score=0.82,
        level="high",
        health_ok=True,
        freshness_level="fresh",
        stability_level="stable",
        quality_score=95.0,
        notes=[],
    )
    text = format_confidence(r)
    assert "demo" in text
    assert "HIGH" in text
    assert "82%" in text
    assert "fresh" in text


def test_format_confidence_includes_notes():
    r = ConfidenceResult(
        name="old",
        score=0.30,
        level="low",
        health_ok=False,
        freshness_level="aged",
        stability_level="unstable",
        quality_score=20.0,
        notes=["Health checks failed", "Freshness is aged"],
    )
    text = format_confidence(r)
    assert "Health checks failed" in text
