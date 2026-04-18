"""Tests for envsnap.tags module."""

import pytest
from unittest.mock import patch
from pathlib import Path
import tempfile
import os


@pytest.fixture
def isolated_snapshot_dir(tmp_path):
    with patch("envsnap.tags.get_snapshot_dir", return_value=tmp_path):
        yield tmp_path


def test_add_and_get_tag(isolated_snapshot_dir):
    from envsnap.tags import add_tag, get_tags
    add_tag("mysnap", "production")
    assert "production" in get_tags("mysnap")


def test_add_tag_deduplicates(isolated_snapshot_dir):
    from envsnap.tags import add_tag, get_tags
    add_tag("mysnap", "staging")
    add_tag("mysnap", "staging")
    assert get_tags("mysnap").count("staging") == 1


def test_remove_tag(isolated_snapshot_dir):
    from envsnap.tags import add_tag, remove_tag, get_tags
    add_tag("mysnap", "dev")
    remove_tag("mysnap", "dev")
    assert "dev" not in get_tags("mysnap")


def test_remove_tag_cleans_empty_entry(isolated_snapshot_dir):
    from envsnap.tags import add_tag, remove_tag, list_all_tags
    add_tag("mysnap", "only")
    remove_tag("mysnap", "only")
    assert "mysnap" not in list_all_tags()


def test_get_tags_missing_snapshot(isolated_snapshot_dir):
    from envsnap.tags import get_tags
    assert get_tags("nonexistent") == []


def test_find_by_tag(isolated_snapshot_dir):
    from envsnap.tags import add_tag, find_by_tag
    add_tag("snap1", "prod")
    add_tag("snap2", "dev")
    add_tag("snap3", "prod")
    result = find_by_tag("prod")
    assert "snap1" in result
    assert "snap3" in result
    assert "snap2" not in result


def test_list_all_tags(isolated_snapshot_dir):
    from envsnap.tags import add_tag, list_all_tags
    add_tag("a", "x")
    add_tag("b", "y")
    all_tags = list_all_tags()
    assert all_tags["a"] == ["x"]
    assert all_tags["b"] == ["y"]
