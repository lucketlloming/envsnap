"""Tests for envsnap.snapshot_report."""
from unittest.mock import patch, MagicMock

import pytest

from envsnap.snapshot_report import build_report, build_all_reports, format_report, SnapshotReport


ENV = {"FOO": "bar", "BAZ": "qux"}


def _patch(monkeypatch, snapshots=None, env=None, tags=None, pinned=False, locked=False, rating=None, note=None, stats=None):
    snapshots = snapshots or ["mysnap"]
    env = env or ENV
    monkeypatch.setattr("envsnap.snapshot_report.load_snapshot", lambda name: env)
    monkeypatch.setattr("envsnap.snapshot_report.list_snapshots", lambda: snapshots)
    monkeypatch.setattr("envsnap.snapshot_report.get_tags", lambda name: tags or [])
    monkeypatch.setattr("envsnap.snapshot_report.get_pin", lambda name: "v1" if pinned else None)
    monkeypatch.setattr("envsnap.snapshot_report.is_locked", lambda name: locked)
    monkeypatch.setattr("envsnap.snapshot_report.get_rating", lambda name: {"score": rating} if rating else None)
    monkeypatch.setattr("envsnap.snapshot_report.get_note", lambda name: note)
    monkeypatch.setattr("envsnap.snapshot_report.snapshot_stats", lambda name: stats or {"event_count": 3})


def test_build_report_basic_fields(monkeypatch):
    _patch(monkeypatch)
    r = build_report("mysnap")
    assert r.name == "mysnap"
    assert r.key_count == 2
    assert r.tags == []
    assert r.pinned is False
    assert r.locked is False
    assert r.rating is None
    assert r.note is None


def test_build_report_with_metadata(monkeypatch):
    _patch(monkeypatch, tags=["prod", "stable"], pinned=True, locked=True, rating=5, note="important")
    r = build_report("mysnap")
    assert r.tags == ["prod", "stable"]
    assert r.pinned is True
    assert r.locked is True
    assert r.rating == 5
    assert r.note == "important"


def test_build_all_reports(monkeypatch):
    _patch(monkeypatch, snapshots=["a", "b"])
    reports = build_all_reports()
    assert len(reports) == 2
    assert {r.name for r in reports} == {"a", "b"}


def test_format_report_text(monkeypatch):
    _patch(monkeypatch, tags=["dev"], pinned=True, stats={"event_count": 7})
    r = build_report("mysnap")
    out = format_report(r, fmt="text")
    assert "mysnap" in out
    assert "dev" in out
    assert "yes" in out  # pinned
    assert "7" in out


def test_format_report_json(monkeypatch):
    import json
    _patch(monkeypatch, rating=4, note="hi")
    r = build_report("mysnap")
    out = format_report(r, fmt="json")
    data = json.loads(out)
    assert data["name"] == "mysnap"
    assert data["rating"] == 4
    assert data["note"] == "hi"
    assert data["key_count"] == 2


def test_build_report_graceful_on_errors(monkeypatch):
    """Metadata helpers that raise should not crash build_report."""
    monkeypatch.setattr("envsnap.snapshot_report.load_snapshot", lambda name: ENV)
    monkeypatch.setattr("envsnap.snapshot_report.list_snapshots", lambda: ["mysnap"])
    monkeypatch.setattr("envsnap.snapshot_report.get_tags", lambda name: [])
    monkeypatch.setattr("envsnap.snapshot_report.get_pin", lambda name: (_ for _ in ()).throw(Exception("fail")))
    monkeypatch.setattr("envsnap.snapshot_report.is_locked", lambda name: (_ for _ in ()).throw(Exception("fail")))
    monkeypatch.setattr("envsnap.snapshot_report.get_rating", lambda name: (_ for _ in ()).throw(Exception("fail")))
    monkeypatch.setattr("envsnap.snapshot_report.get_note", lambda name: None)
    monkeypatch.setattr("envsnap.snapshot_report.snapshot_stats", lambda name: {})
    r = build_report("mysnap")
    assert r.pinned is False
    assert r.locked is False
    assert r.rating is None
