"""Tests for envsnap.snapshot_readiness."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from envsnap.snapshot_readiness import (
    ReadinessResult,
    _level,
    assess_readiness,
    format_readiness,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _health(healthy: bool, issues=None):
    h = MagicMock()
    h.healthy = healthy
    h.issues = issues or []
    return h


def _maturity(level: str):
    m = MagicMock()
    m.level = level
    return m


def _compliance(passed: bool, violations=None):
    c = MagicMock()
    c.passed = passed
    c.violations = violations or []
    return c


def _patch(health=None, maturity=None, compliance=None):
    return patch.multiple(
        "envsnap.snapshot_readiness",
        check_health=MagicMock(return_value=health or _health(True)),
        score_maturity=MagicMock(return_value=maturity or _maturity("mature")),
        check_compliance=MagicMock(return_value=compliance or _compliance(True)),
    )


# ---------------------------------------------------------------------------
# unit tests
# ---------------------------------------------------------------------------

def test_level_boundaries():
    assert _level(100) == "ready"
    assert _level(80) == "ready"
    assert _level(79) == "nearly-ready"
    assert _level(50) == "nearly-ready"
    assert _level(49) == "not-ready"
    assert _level(0) == "not-ready"


def test_healthy_mature_compliant_snapshot_is_ready():
    with _patch():
        result = assess_readiness("snap1")
    assert result.level == "ready"
    assert result.score == 100.0
    assert result.blockers == []
    assert result.warnings == []


def test_health_error_reduces_score_and_adds_blocker():
    issue = {"severity": "error", "message": "critical problem"}
    with _patch(health=_health(False, [issue])):
        result = assess_readiness("snap1")
    assert "critical problem" in result.blockers
    assert result.score == 80.0


def test_health_warning_reduces_score_and_adds_warning():
    issue = {"severity": "warning", "message": "minor issue"}
    with _patch(health=_health(False, [issue])):
        result = assess_readiness("snap1")
    assert "minor issue" in result.warnings
    assert result.score == 95.0


def test_nascent_maturity_is_blocker():
    with _patch(maturity=_maturity("nascent")):
        result = assess_readiness("snap1")
    assert any("nascent" in b for b in result.blockers)
    assert result.score == 80.0


def test_developing_maturity_is_warning():
    with _patch(maturity=_maturity("developing")):
        result = assess_readiness("snap1")
    assert any("developing" in w for w in result.warnings)
    assert result.score == 90.0


def test_compliance_failure_adds_blocker():
    v = MagicMock()
    v.severity = "error"
    v.message = "compliance error"
    with _patch(compliance=_compliance(False, [v])):
        result = assess_readiness("snap1")
    assert "compliance error" in result.blockers
    assert result.score == 85.0


def test_score_does_not_go_below_zero():
    issues = [{"severity": "error", "message": f"e{i}"} for i in range(10)]
    with _patch(health=_health(False, issues), maturity=_maturity("nascent")):
        result = assess_readiness("snap1")
    assert result.score == 0.0


def test_format_readiness_contains_key_fields():
    result = ReadinessResult(
        snapshot="mysnap",
        score=72.5,
        level="nearly-ready",
        blockers=["one blocker"],
        warnings=["one warning"],
    )
    text = format_readiness(result)
    assert "mysnap" in text
    assert "72.5" in text
    assert "nearly-ready" in text
    assert "one blocker" in text
    assert "one warning" in text
