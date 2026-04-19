import pytest
from pathlib import Path
from envsnap import group as grp
from envsnap.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.storage.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.group.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.group.list_snapshots", lambda: ["snap1", "snap2", "snap3"])
    return tmp_path


def test_add_and_get_group(isolated_snapshot_dir):
    grp.add_to_group("mygroup", "snap1")
    grp.add_to_group("mygroup", "snap2")
    assert grp.get_group("mygroup") == ["snap1", "snap2"]


def test_add_deduplicates(isolated_snapshot_dir):
    grp.add_to_group("mygroup", "snap1")
    grp.add_to_group("mygroup", "snap1")
    assert grp.get_group("mygroup") == ["snap1"]


def test_add_missing_snapshot_raises(isolated_snapshot_dir):
    with pytest.raises(KeyError, match="does not exist"):
        grp.add_to_group("mygroup", "ghost")


def test_remove_from_group(isolated_snapshot_dir):
    grp.add_to_group("mygroup", "snap1")
    grp.add_to_group("mygroup", "snap2")
    grp.remove_from_group("mygroup", "snap1")
    assert grp.get_group("mygroup") == ["snap2"]


def test_remove_cleans_empty_group(isolated_snapshot_dir):
    grp.add_to_group("mygroup", "snap1")
    grp.remove_from_group("mygroup", "snap1")
    assert "mygroup" not in grp.list_groups()


def test_list_groups(isolated_snapshot_dir):
    grp.add_to_group("g1", "snap1")
    grp.add_to_group("g2", "snap2")
    assert set(grp.list_groups()) == {"g1", "g2"}


def test_delete_group(isolated_snapshot_dir):
    grp.add_to_group("mygroup", "snap1")
    grp.delete_group("mygroup")
    assert "mygroup" not in grp.list_groups()


def test_delete_missing_group_raises(isolated_snapshot_dir):
    with pytest.raises(KeyError, match="does not exist"):
        grp.delete_group("nope")
