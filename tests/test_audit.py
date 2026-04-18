import pytest
from pathlib import Path
from unittest.mock import patch
import envsnap.audit as audit_mod


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.storage.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.audit.get_snapshot_dir", lambda: tmp_path)
    return tmp_path


def test_record_and_get_audit():
    auditsnap", "mysnap", user="alice")
    entries = audit_mod.get_audit()
    assert len(entries) == 1
    assert entries[snap"
    assert entries[0]["snapshot"] == "mysnap"
    assert entries[0]["user"] == "alice"


def test_get_audit_filtered():
    audit_mod.record_audit("snap", "a", user="u1")
    audit_mod.record_audit("restore", "b", user="u2")
    result = audit_mod.get_audit(snapshot="a")
    assert len(result) == 1
    assert result[0]["snapshot"] == "a"


def test_get_audit_all():
    audit_mod.record_audit("snap", "x")
    audit_mod.record_audit("delete", "y")
    assert len(audit_mod.get_audit()) == 2


def test_clear_audit_specific():
    audit_mod.record_audit("snap", "keep")
    audit_mod.record_audit("snap", "remove")
    removed = audit_mod.clear_audit(snapshot="remove")
    assert removed == 1
    remaining = audit_mod.get_audit()
    assert all(e["snapshot"] != "remove" for e in remaining)


def test_clear_audit_all():
    audit_mod.record_audit("snap", "a")
    audit_mod.record_audit("snap", "b")
    removed = audit_mod.clear_audit()
    assert removed == 2
    assert audit_mod.get_audit() == []


def test_record_detail():
    audit_mod.record_audit("export", "mysnap", detail="json format")
    e = audit_mod.get_audit()[0]
    assert e["detail"] == "json format"
