"""Tests for envsnap.snapshot_risk."""
from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from envsnap.snapshot_risk import assess_risk, assess_all_risk, format_risk, _level, RiskResult


def _sensitivity(sensitive=(), moderate=(), public=()):
    m = MagicMock()
    m.sensitive_keys = list(sensitive)
    m.moderate_keys = list(moderate)
    m.public_keys = list(public)
    return m


def _complexity(level="low"):
    m = MagicMock()
    m.level = level
    return m


def _health(healthy=True, issues=()):
    m = MagicMock()
    m.healthy = healthy
    m.issues = list(issues)
    return m


def _patch(sens, comp, hlth):
    return [
        patch("envsnap.snapshot_risk.analyze_sensitivity", return_value=sens),
        patch("envsnap.snapshot_risk.compute_complexity", return_value=comp),
        patch("envsnap.snapshot_risk.check_health", return_value=hlth),
    ]


def test_level_boundaries():
    assert _level(0.0) == "low"
    assert _level(0.24) == "low"
    assert _level(0.25) == "medium"
    assert _level(0.5) == "high"
    assert _level(0.75) == "critical"
    assert _level(1.0) == "critical"


def test_no_risk_clean_snapshot():
    patches = _patch(_sensitivity(), _complexity("low"), _health(True))
    with patches[0], patches[1], patches[2]:
        result = assess_risk("clean")
    assert result.level == "low"
    assert result.score == 0.0
    assert result.factors == []


def test_sensitive_keys_raise_score():
    patches = _patch(_sensitivity(sensitive=["SECRET", "TOKEN"]), _complexity("low"), _health(True))
    with patches[0], patches[1], patches[2]:
        result = assess_risk("snap")
    assert result.score > 0
    assert any("sensitive" in f for f in result.factors)


def test_high_complexity_adds_factor():
    patches = _patch(_sensitivity(), _complexity("high"), _health(True))
    with patches[0], patches[1], patches[2]:
        result = assess_risk("snap")
    assert any("complexity" in f for f in result.factors)
    assert result.score >= 0.2


def test_health_errors_add_to_score():
    issues = [{"severity": "error"}, {"severity": "error"}]
    patches = _patch(_sensitivity(), _complexity("low"), _health(False, issues))
    with patches[0], patches[1], patches[2]:
        result = assess_risk("snap")
    assert result.score >= 0.2
    assert any("error" in f for f in result.factors)


def test_score_capped_at_one():
    sensitive = [f"KEY{i}" for i in range(20)]
    issues = [{"severity": "error"}] * 10
    patches = _patch(_sensitivity(sensitive=sensitive), _complexity("high"), _health(False, issues))
    with patches[0], patches[1], patches[2]:
        result = assess_risk("snap")
    assert result.score <= 1.0


def test_assess_all_risk_returns_list():
    patches = _patch(_sensitivity(), _complexity("low"), _health(True))
    with patches[0], patches[1], patches[2]:
        results = assess_all_risk(["a", "b", "c"])
    assert len(results) == 3


def test_format_risk_text():
    r = RiskResult(snapshot="mysnap", score=0.6, level="high", factors=["2 sensitive key(s) detected"])
    text = format_risk(r)
    assert "mysnap" in text
    assert "HIGH" in text
    assert "sensitive" in text


def test_as_dict_structure():
    r = RiskResult(snapshot="s", score=0.333, level="medium", factors=["x"])
    d = r.as_dict()
    assert d["snapshot"] == "s"
    assert d["level"] == "medium"
    assert isinstance(d["score"], float)
    assert d["factors"] == ["x"]
