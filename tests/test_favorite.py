"""Tests for envsnap.favorite and envsnap.cli_favorite."""

from __future__ import annotations

import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch

from envsnap.cli_favorite import favorite_cmd


SNAPS = ["dev", "prod", "staging"]


def _patch(tmp_path, favs=None):
    """Return context managers to isolate storage."""
    favs_data = favs or []
    return (
        patch("envsnap.favorite.get_snapshot_dir", return_value=tmp_path),
        patch("envsnap.favorite.list_snapshots", return_value=SNAPS),
    )


@pytest.fixture()
def runner():
    return CliRunner()


def test_add_and_list_favorite(tmp_path):
    from envsnap.favorite import add_favorite, list_favorites
    p1, p2 = _patch(tmp_path)
    with p1, p2:
        add_favorite("dev")
        add_favorite("prod")
        assert list_favorites() == ["dev", "prod"]


def test_add_favorite_deduplicates(tmp_path):
    from envsnap.favorite import add_favorite, list_favorites
    p1, p2 = _patch(tmp_path)
    with p1, p2:
        add_favorite("dev")
        add_favorite("dev")
        assert list_favorites().count("dev") == 1


def test_add_favorite_missing_snapshot_raises(tmp_path):
    from envsnap.favorite import add_favorite
    p1, p2 = _patch(tmp_path)
    with p1, p2:
        with pytest.raises(ValueError, match="does not exist"):
            add_favorite("ghost")


def test_remove_favorite(tmp_path):
    from envsnap.favorite import add_favorite, remove_favorite, list_favorites
    p1, p2 = _patch(tmp_path)
    with p1, p2:
        add_favorite("dev")
        remove_favorite("dev")
        assert "dev" not in list_favorites()


def test_remove_favorite_not_set_raises(tmp_path):
    from envsnap.favorite import remove_favorite
    p1, p2 = _patch(tmp_path)
    with p1, p2:
        with pytest.raises(ValueError, match="not a favorite"):
            remove_favorite("dev")


def test_is_favorite(tmp_path):
    from envsnap.favorite import add_favorite, is_favorite
    p1, p2 = _patch(tmp_path)
    with p1, p2:
        assert not is_favorite("dev")
        add_favorite("dev")
        assert is_favorite("dev")


def test_cli_favorite_list_json(tmp_path, runner):
    with patch("envsnap.favorite.get_snapshot_dir", return_value=tmp_path), \
         patch("envsnap.favorite.list_snapshots", return_value=SNAPS):
        from envsnap.favorite import add_favorite
        add_favorite("staging")

    with patch("envsnap.favorite.get_snapshot_dir", return_value=tmp_path):
        result = runner.invoke(favorite_cmd, ["list", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "staging" in data


def test_cli_favorite_add_missing(tmp_path, runner):
    with patch("envsnap.favorite.get_snapshot_dir", return_value=tmp_path), \
         patch("envsnap.favorite.list_snapshots", return_value=SNAPS):
        result = runner.invoke(favorite_cmd, ["add", "ghost"])
        assert result.exit_code == 1
