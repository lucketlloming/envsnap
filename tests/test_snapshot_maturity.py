"""Tests for envsnap.snapshot_maturity."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from envsnap.snapshot_maturity import (
    MaturityResult,
    _level,
    format_maturity,
    score_maturity,
    score_all_maturity,
)


def _patch(data=None, history=None, note=None, pin=None, snapshots=None):
    """Helper to patch all external dependencies."""
    data = data or {"KEY": "val"}
    history = history or []
    snapshots = snapshots or ["snap1"]
    return [
        patch("envsnap.snapshot_maturity.load_snapshot", return_value=data),
        patch("envsnap.snapshot_maturity.get_history", return_value=history),
        patch("envsnap.snapshot_maturity.get_note", return_value=note),
        patch("envsnap.snapshot_maturity.get_pin", return_value=pin),
        patch("envsnap.snapshot_maturity.list_snapshots", return_value=snapshots),
    ]


def test_level_mature():
    assert _level(80) == "mature"
    assert _level(100) == "mature"


def test_level_developing():
    assert _level(50) == "developing"
    assert _level(79) == "developing"


def test_level_nascent():
    assert _level(0) == "nascent"
    assert _level(49) == "nascent"


def test_score_maturity_basic():
    data = {"A": "1", "B": "2"}
    patches = _patch(data=data, history=[], note=None, pin=None)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = score_maturity("mysnap")
    assert isinstance(result, MaturityResult)
    assert result.name == "mysnap"
    assert 0 <= result.score <= 100
    assert result.level in ("mature", "developing", "nascent")


def test_score_maturity_pinned_and_noted_boosts_score():
    data = {f"K{i}": f"v{i}" for i in range(5)}
    history = [{"event": "snap"} for _ in range(6)]
    patches = _patch(data=data, history=history, note="some note", pin="1.0")
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = score_maturity("richsnap")
    assert result.breakdown["has_note"] == 15
    assert result.breakdown["is_pinned"] == 15
    assert result.breakdown["activity"] == 30


def test_score_maturity_empty_snapshot():
    patches = _patch(data={}, history=[], note=None, pin=None)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = score_maturity("empty")
    assert result.score == 0
    assert result.level == "nascent"


def test_score_all_maturity_returns_list():
    data = {"X": "y"}
    patches = _patch(data=data, history=[], note=None, pin=None, snapshots=["a", "b"])
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        results = score_all_maturity()
    assert len(results) == 2
    assert all(isinstance(r, MaturityResult) for r in results)


def test_format_maturity_contains_name_and_score():
    result = MaturityResult(
        name="mysnap",
        score=72,
        level="developing",
        breakdown={"key_richness": 30, "activity": 20, "has_note": 15, "is_pinned": 0, "value_quality": 7},
    )
    text = format_maturity(result)
    assert "mysnap" in text
    assert "72" in text
    assert "developing" in text
    assert "key_richness" in text
