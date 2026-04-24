"""Tests for envsnap.snapshot_chain."""
import pytest

from envsnap.snapshot_chain import (
    ChainError,
    SnapshotNotFoundError,
    append_to_chain,
    create_chain,
    delete_chain,
    get_chain,
    list_chains,
)


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.snapshot_chain.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr(
        "envsnap.snapshot_chain.list_snapshots",
        lambda: ["snap_a", "snap_b", "snap_c"],
    )


def test_create_and_get_chain():
    create_chain("mychain", ["snap_a", "snap_b"])
    result = get_chain("mychain")
    assert result == ["snap_a", "snap_b"]


def test_create_chain_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        create_chain("bad", ["snap_a", "missing_snap"])


def test_get_chain_missing_raises():
    with pytest.raises(ChainError):
        get_chain("nonexistent")


def test_list_chains_empty():
    assert list_chains() == []


def test_list_chains_returns_names():
    create_chain("alpha", ["snap_a"])
    create_chain("beta", ["snap_b"])
    assert list_chains() == ["alpha", "beta"]


def test_delete_chain():
    create_chain("temp", ["snap_a"])
    delete_chain("temp")
    assert "temp" not in list_chains()


def test_delete_missing_chain_raises():
    with pytest.raises(ChainError):
        delete_chain("ghost")


def test_append_to_chain():
    create_chain("seq", ["snap_a"])
    append_to_chain("seq", "snap_b")
    assert get_chain("seq") == ["snap_a", "snap_b"]


def test_append_deduplicates():
    create_chain("seq", ["snap_a", "snap_b"])
    append_to_chain("seq", "snap_b")
    assert get_chain("seq").count("snap_b") == 1


def test_append_missing_snapshot_raises():
    create_chain("seq", ["snap_a"])
    with pytest.raises(SnapshotNotFoundError):
        append_to_chain("seq", "no_such_snap")


def test_create_chain_overwrites_existing():
    create_chain("ow", ["snap_a", "snap_b"])
    create_chain("ow", ["snap_c"])
    assert get_chain("ow") == ["snap_c"]
