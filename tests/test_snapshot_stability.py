"""Tests for envsnap.snapshot_stability."""
import pytest
from unittest.mock import patch

from envsnap.snapshot_stability import (
    StabilityResult,
    compute_stability,
    compute_all_stability,
    format_stability,
    _level,
)


def _patch(history_map: dict, snapshots: list):
    """Return a context manager that mocks history and list_snapshots."""
    import contextlib

    @contextlib.contextmanager
    def _ctx():
        with patch(
            "envsnap.snapshot_stability.get_history",
            side_effect=lambda name: history_map.get(name, []),
        ), patch(
            "envsnap.snapshot_stability.list_snapshots",
            return_value=snapshots,
        ):
            yield

    return _ctx()


def test_level_stable():
    assert _level(1.0)[0] == "stable"
    assert _level(0.85)[0] == "stable"


def test_level_moderate():
    assert _level(0.84)[0] == "moderate"
    assert _level(0.50)[0] == "moderate"


def test_level_unstable():
    assert _level(0.49)[0] == "unstable"
    assert _level(0.0)[0] == "unstable"


def test_compute_stability_no_history():
    with _patch({}, ["snap1"]):
        result = compute_stability("snap1")
    assert result.total_events == 0
    assert result.change_events == 0
    assert result.stability_score == 1.0
    assert result.level == "stable"


def test_compute_stability_all_changes():
    history = [
        {"event": "snap"},
        {"event": "patch"},
        {"event": "restore"},
    ]
    with _patch({"mysnap": history}, ["mysnap"]):
        result = compute_stability("mysnap")
    assert result.total_events == 3
    assert result.change_events == 3
    assert result.stability_score == 0.0
    assert result.level == "unstable"


def test_compute_stability_mixed_events():
    history = [
        {"event": "snap"},
        {"event": "read"},
        {"event": "read"},
        {"event": "read"},
    ]
    with _patch({"s": history}, ["s"]):
        result = compute_stability("s")
    assert result.change_events == 1
    assert result.total_events == 4
    assert pytest.approx(result.stability_score, 0.001) == 0.75
    assert result.level == "moderate"


def test_compute_all_stability_returns_list():
    snaps = ["a", "b"]
    with _patch({"a": [{"event": "snap"}], "b": []}, snaps):
        results = compute_all_stability()
    assert len(results) == 2
    names = {r.name for r in results}
    assert names == {"a", "b"}


def test_format_stability_contains_fields():
    result = StabilityResult(
        name="proj",
        total_events=10,
        change_events=2,
        stability_score=0.8,
        level="moderate",
        note="Snapshot changes occasionally.",
    )
    text = format_stability(result)
    assert "proj" in text
    assert "moderate" in text
    assert "80.00%" in text
    assert "2 / 10" in text
