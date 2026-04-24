"""Tests for envsnap.snapshot_recommendation."""
from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from envsnap.snapshot_recommendation import (
    recommend,
    recommend_all,
    format_recommendations,
    Recommendation,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _patch(data: dict, score: int = 90, healthy: bool = True,
           expiry=None, locked: bool = False):
    health_mock = MagicMock(healthy=healthy, issues=["bad value"] if not healthy else [])
    score_mock = MagicMock(score=score)
    return [
        patch("envsnap.snapshot_recommendation.load_snapshot", return_value=data),
        patch("envsnap.snapshot_recommendation.check_health", return_value=health_mock),
        patch("envsnap.snapshot_recommendation.score_snapshot", return_value=score_mock),
        patch("envsnap.snapshot_recommendation.get_expiry", return_value=expiry),
        patch("envsnap.snapshot_recommendation.is_locked", return_value=locked),
    ]


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_no_recommendations_for_healthy_snapshot():
    data = {"KEY1": "val1", "KEY2": "val2", "KEY3": "val3"}
    patches = _patch(data, score=95, healthy=True)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        recs = recommend("mysnap")
    assert recs == []


def test_empty_snapshot_warning():
    patches = _patch({}, score=0, healthy=False)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        recs = recommend("empty")
    codes = [r.code for r in recs]
    assert "EMPTY_SNAPSHOT" in codes


def test_low_key_count_info():
    patches = _patch({"A": "1"}, score=85, healthy=True)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        recs = recommend("tiny")
    codes = [r.code for r in recs]
    assert "LOW_KEY_COUNT" in codes


def test_health_issue_adds_recommendation():
    data = {"K1": "v1", "K2": "v2", "K3": "v3"}
    patches = _patch(data, score=80, healthy=False)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        recs = recommend("sick")
    codes = [r.code for r in recs]
    assert "HEALTH_ISSUE" in codes


def test_low_score_action():
    data = {"K1": "v1", "K2": "v2", "K3": "v3"}
    patches = _patch(data, score=40, healthy=True)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        recs = recommend("poor")
    codes = [r.code for r in recs]
    assert "LOW_SCORE" in codes
    assert any(r.level == "action" for r in recs if r.code == "LOW_SCORE")


def test_expiry_info():
    data = {"K1": "v1", "K2": "v2", "K3": "v3"}
    patches = _patch(data, score=90, healthy=True, expiry="2099-12-31")
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        recs = recommend("expiring")
    codes = [r.code for r in recs]
    assert "HAS_EXPIRY" in codes


def test_locked_info():
    data = {"K1": "v1", "K2": "v2", "K3": "v3"}
    patches = _patch(data, score=90, healthy=True, locked=True)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        recs = recommend("locked")
    codes = [r.code for r in recs]
    assert "IS_LOCKED" in codes


def test_recommend_all_aggregates():
    data = {"K": "v", "K2": "v2", "K3": "v3"}
    with patch("envsnap.snapshot_recommendation.list_snapshots", return_value=["a", "b"]), \
         patch("envsnap.snapshot_recommendation.load_snapshot", return_value=data), \
         patch("envsnap.snapshot_recommendation.check_health", return_value=MagicMock(healthy=True, issues=[])), \
         patch("envsnap.snapshot_recommendation.score_snapshot", return_value=MagicMock(score=95)), \
         patch("envsnap.snapshot_recommendation.get_expiry", return_value=None), \
         patch("envsnap.snapshot_recommendation.is_locked", return_value=False):
        recs = recommend_all()
    snapshots = {r.snapshot for r in recs}
    assert snapshots == set()  # no issues expected for healthy snapshots


def test_format_text_no_recs():
    assert format_recommendations([]) == "No recommendations."


def test_format_text_with_recs():
    recs = [Recommendation("s", "warning", "LOW_SCORE", "Score is low.")]
    out = format_recommendations(recs, fmt="text")
    assert "LOW_SCORE" in out
    assert "Score is low." in out


def test_format_json():
    import json
    recs = [Recommendation("s", "info", "HAS_EXPIRY", "Expires soon.")]
    out = format_recommendations(recs, fmt="json")
    parsed = json.loads(out)
    assert parsed[0]["code"] == "HAS_EXPIRY"
    assert parsed[0]["level"] == "info"
