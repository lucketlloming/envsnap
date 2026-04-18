"""Tests for envsnap.rename."""
import pytest
from unittest.mock import patch, MagicMock
from envsnap.rename import rename_snapshot, SnapshotNotFoundError, SnapshotAlreadyExistsError


def _patch(src_exists=True, dst_exists=False, data=None):
    if data is None:
        data = {"KEY": "val"}

    def _mock_path(name):
        p = MagicMock()
        p.exists.return_value = src_exists if name == "old" else dst_exists
        return p

    return (
        patch("envsnap.rename.snapshot_path", side_effect=_mock_path),
        patch("envsnap.rename.load_snapshot", return_value=data),
        patch("envsnap.rename.save_snapshot"),
        patch("envsnap.rename.delete_snapshot"),
        patch("envsnap.rename._update_aliases"),
        patch("envsnap.rename._update_tags"),
        patch("envsnap.rename._update_pins"),
        patch("envsnap.rename._update_profiles"),
    )


def test_rename_success():
    patches = _patch()
    with patches[0], patches[1], patches[2] as mock_save, patches[3] as mock_del, \
         patches[4], patches[5], patches[6], patches[7]:
        rename_snapshot("old", "new")
        mock_save.assert_called_once_with("new", {"KEY": "val"})
        mock_del.assert_called_once_with("old")


def test_rename_missing_source():
    patches = _patch(src_exists=False)
    with patches[0], patches[1], patches[2], patches[3], \
         patches[4], patches[5], patches[6], patches[7]:
        with pytest.raises(SnapshotNotFoundError):
            rename_snapshot("old", "new")


def test_rename_destination_exists():
    patches = _patch(dst_exists=True)
    with patches[0], patches[1], patches[2], patches[3], \
         patches[4], patches[5], patches[6], patches[7]:
        with pytest.raises(SnapshotAlreadyExistsError):
            rename_snapshot("old", "new")


def test_rename_same_name_raises():
    """Renaming a snapshot to its own name should raise SnapshotAlreadyExistsError."""
    patches = _patch(src_exists=True, dst_exists=True)
    with patches[0], patches[1], patches[2], patches[3], \
         patches[4], patches[5], patches[6], patches[7]:
        with pytest.raises(SnapshotAlreadyExistsError):
            rename_snapshot("old", "old")


def test_update_aliases_renames_target():
    from envsnap.rename import _update_aliases
    aliases = {"a": "old", "b": "other"}
    with patch("envsnap.rename._load_aliases", return_value=aliases), \
         patch("envsnap.rename._save_aliases") as mock_save:
        _update_aliases("old", "new")
        assert aliases["a"] == "new"
        assert aliases["b"] == "other"
        mock_save.assert_called_once()


def test_update_aliases_no_match_does_not_save():
    """_update_aliases should not save when no alias points to the old name."""
    from envsnap.rename import _update_aliases
    aliases = {"a": "other", "b": "unrelated"}
    with patch("envsnap.rename._load_aliases", return_value=aliases), \
         patch("envsnap.rename._save_aliases") as mock_save:
        _update_aliases("old", "new")
        mock_save.assert_not_called()


def test_update_profiles_renames_member():
    from envsnap.rename import _update_profiles
    profiles = {"dev": ["old", "base"], "prod": ["base"]}
    with patch("envsnap.rename._load_profiles", return_value=profiles), \
         patch("envsnap.rename._save_profiles") as mock_save:
        _update_profiles("old", "new")
        assert "new" in profiles["dev"]
        assert "old" not in profiles["dev"]
        mock_save.assert_called_once()
