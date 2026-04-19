"""Tests for envsnap.rollback."""
import pytest
from unittest.mock import patch, MagicMock

from envsnap.rollback import get_rollback_points, rollback_snapshot, RollbackError


SNAP_NAME = "mysnap"

_HISTORY = [
    {"event": "snap", "snapshot": SNAP_NAME, "data": {"A": "1"}},
    {"event": "snap", "snapshot": SNAP_NAME, "data": {"A": "2", "B": "x"}},
    {"event": "snap", "snapshot": SNAP_NAME, "data": {"A": "3"}},
]


def _patch(history=None, snapshots=None, save=None):
    history = history if history is not None else _HISTORY
    snapshots = snapshots if snapshots is not None else [SNAP_NAME]
    ctx = [
        patch("envsnap.rollback.get_history", return_value=history),
        patch("envsnap.rollback.list_snapshots", return_value=snapshots),
        patch("envsnap.rollback.save_snapshot"),
        patch("envsnap.rollback.record_event"),
    ]
    return ctx


def test_get_rollback_points_filters_events():
    history = [
        {"event": "snap", "snapshot": SNAP_NAME, "data": {"A": "1"}},
        {"event": "delete", "snapshot": SNAP_NAME},
        {"event": "restore", "snapshot": SNAP_NAME, "data": {"A": "2"}},
    ]
    with patch("envsnap.rollback.get_history", return_value=history):
        pts = get_rollback_points(SNAP_NAME)
    assert len(pts) == 2
    assert all(e["event"] in ("snap", "restore") for e in pts)


def test_rollback_one_step():
    ctxs = _patch()
    from contextlib import ExitStack
    with ExitStack() as stack:
        mocks = [stack.enter_context(c) for c in ctxs]
        result = rollback_snapshot(SNAP_NAME, steps=1)
    assert result == {"A": "3"}
    mocks[2].assert_called_once_with(SNAP_NAME, {"A": "3"})


def test_rollback_two_steps():
    ctxs = _patch()
    from contextlib import ExitStack
    with ExitStack() as stack:
        mocks = [stack.enter_context(c) for c in ctxs]
        result = rollback_snapshot(SNAP_NAME, steps=2)
    assert result == {"A": "2", "B": "x"}


def test_rollback_missing_snapshot_raises():
    ctxs = _patch(snapshots=[])
    from contextlib import ExitStack
    with ExitStack() as stack:
        for c in ctxs:
            stack.enter_context(c)
        with pytest.raises(RollbackError, match="does not exist"):
            rollback_snapshot(SNAP_NAME)


def test_rollback_not_enough_history_raises():
    ctxs = _patch(history=[_HISTORY[0]])
    from contextlib import ExitStack
    with ExitStack() as stack:
        for c in ctxs:
            stack.enter_context(c)
        with pytest.raises(RollbackError, match="Not enough history"):
            rollback_snapshot(SNAP_NAME, steps=5)


def test_rollback_no_data_in_entry_raises():
    history = [{"event": "snap", "snapshot": SNAP_NAME}]  # no 'data' key
    ctxs = _patch(history=history)
    from contextlib import ExitStack
    with ExitStack() as stack:
        for c in ctxs:
            stack.enter_context(c)
        with pytest.raises(RollbackError, match="does not contain snapshot data"):
            rollback_snapshot(SNAP_NAME, steps=1)
