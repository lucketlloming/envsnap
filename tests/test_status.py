"""Tests for envsnap.status module."""
from __future__ import annotations

import json
import pytest
from unittest.mock import patch

from envsnap.status import snapshot_status, format_status


SNAP_DATA = {"KEY": "value", "OTHER": "123"}


def _patch(load_return=None, pin=None, locked=False, fav=False,
           expiry=None, rating=3, note="hi", tags=None):
    """Return a context-manager stack that patches all side-modules."""
    import contextlib

    @contextlib.contextmanager
    def _ctx():
        with patch("envsnap.status.storage.load_snapshot", return_value=load_return or SNAP_DATA), \
             patch("envsnap.status.get_pin", return_value=pin), \
             patch("envsnap.status.is_locked", return_value=locked), \
             patch("envsnap.status.is_favorite", return_value=fav), \
             patch("envsnap.status.get_expiry", return_value=expiry), \
             patch("envsnap.status.get_rating", return_value=rating), \
             patch("envsnap.status.get_note", return_value=note), \
             patch("envsnap.status.get_tags", return_value=tags or []):
            yield

    return _ctx()


def test_snapshot_status_basic_fields():
    with _patch():
        s = snapshot_status("mysnap")
    assert s["name"] == "mysnap"
    assert s["key_count"] == 2
    assert s["pinned"] is False  # pin returns None -> False
    assert s["locked"] is False
    assert s["favorite"] is False
    assert s["expiry"] is None
    assert s["rating"] == 3
    assert s["note"] == "hi"
    assert s["tags"] == []


def test_snapshot_status_pinned_and_locked():
    with _patch(pin="v1", locked=True, fav=True, tags=["prod", "stable"]):
        s = snapshot_status("mysnap")
    assert s["pinned"] is True
    assert s["locked"] is True
    assert s["favorite"] is True
    assert s["tags"] == ["prod", "stable"]


def test_snapshot_status_missing_raises():
    with patch("envsnap.status.storage.load_snapshot", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            snapshot_status("ghost")


def test_format_status_text():
    with _patch(rating=5, note="important", tags=["dev"]):
        s = snapshot_status("mysnap")
    out = format_status(s, fmt="text")
    assert "mysnap" in out
    assert "Keys     : 2" in out
    assert "Rating   : 5" in out
    assert "Note     : important" in out
    assert "Tags     : dev" in out


def test_format_status_json():
    with _patch(rating=None, note=None):
        s = snapshot_status("mysnap")
    out = format_status(s, fmt="json")
    parsed = json.loads(out)
    assert parsed["name"] == "mysnap"
    assert parsed["key_count"] == 2
    assert parsed["rating"] is None
    assert parsed["note"] is None


def test_format_status_text_no_rating_no_note():
    with _patch(rating=None, note=None):
        s = snapshot_status("mysnap")
    out = format_status(s)
    assert "unrated" in out
    assert "none" in out
