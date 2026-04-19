import pytest
from envsnap.remind import (
    set_reminder, get_reminder, remove_reminder,
    list_reminders, due_reminders,
    ReminderNotFoundError, SnapshotNotFoundError,
)
from envsnap.storage import save_snapshot
import envsnap.storage as _st


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(_st, "_SNAPSHOT_DIR", tmp_path)
    return tmp_path


def _make_snapshot(name):
    save_snapshot(name, {"K": "V"})


def test_set_and_get_reminder(isolated_snapshot_dir):
    _make_snapshot("dev")
    set_reminder("dev", "Update deps", "2099-01-01")
    r = get_reminder("dev")
    assert r["message"] == "Update deps"
    assert r["due"] == "2099-01-01"


def test_set_reminder_missing_snapshot_raises(isolated_snapshot_dir):
    with pytest.raises(SnapshotNotFoundError):
        set_reminder("ghost", "hello")


def test_set_reminder_invalid_date_raises(isolated_snapshot_dir):
    _make_snapshot("dev")
    with pytest.raises(ValueError):
        set_reminder("dev", "msg", "not-a-date")


def test_set_reminder_no_due(isolated_snapshot_dir):
    _make_snapshot("dev")
    set_reminder("dev", "No deadline")
    r = get_reminder("dev")
    assert r["due"] is None


def test_remove_reminder(isolated_snapshot_dir):
    _make_snapshot("dev")
    set_reminder("dev", "msg")
    remove_reminder("dev")
    with pytest.raises(ReminderNotFoundError):
        get_reminder("dev")


def test_remove_missing_raises(isolated_snapshot_dir):
    with pytest.raises(ReminderNotFoundError):
        remove_reminder("ghost")


def test_list_reminders(isolated_snapshot_dir):
    _make_snapshot("a")
    _make_snapshot("b")
    set_reminder("a", "A msg", "2099-01-01")
    set_reminder("b", "B msg")
    assert set(list_reminders().keys()) == {"a", "b"}


def test_due_reminders(isolated_snapshot_dir):
    _make_snapshot("old")
    _make_snapshot("future")
    _make_snapshot("nodue")
    set_reminder("old", "overdue", "2000-01-01")
    set_reminder("future", "later", "2099-12-31")
    set_reminder("nodue", "no date")
    result = due_reminders("2024-06-01")
    assert "old" in result
    assert "future" not in result
    assert "nodue" not in result
