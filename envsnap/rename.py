"""Rename snapshots, updating all cross-references."""
from __future__ import annotations

from envsnap.storage import snapshot_path, load_snapshot, save_snapshot, delete_snapshot
from envsnap.alias import _load_aliases, _save_aliases
from envsnap.tags import _load_tags, _save_tags
from envsnap.pin import _load_pins, _save_pins
from envsnap.profiles import _load_profiles, _save_profiles


class SnapshotNotFoundError(FileNotFoundError):
    pass


class SnapshotAlreadyExistsError(FileExistsError):
    pass


def rename_snapshot(old_name: str, new_name: str) -> None:
    """Rename a snapshot from old_name to new_name."""
    src = snapshot_path(old_name)
    dst = snapshot_path(new_name)

    if not src.exists():
        raise SnapshotNotFoundError(f"Snapshot '{old_name}' not found.")
    if dst.exists():
        raise SnapshotAlreadyExistsError(f"Snapshot '{new_name}' already exists.")

    data = load_snapshot(old_name)
    save_snapshot(new_name, data)
    delete_snapshot(old_name)

    _update_aliases(old_name, new_name)
    _update_tags(old_name, new_name)
    _update_pins(old_name, new_name)
    _update_profiles(old_name, new_name)


def _update_aliases(old: str, new: str) -> None:
    aliases = _load_aliases()
    changed = False
    for alias, target in list(aliases.items()):
        if target == old:
            aliases[alias] = new
            changed = True
    if changed:
        _save_aliases(aliases)


def _update_tags(old: str, new: str) -> None:
    tags = _load_tags()
    if old in tags:
        tags[new] = tags.pop(old)
        _save_tags(tags)


def _update_pins(old: str, new: str) -> None:
    pins = _load_pins()
    if old in pins:
        pins[new] = pins.pop(old)
        _save_pins(pins)


def _update_profiles(old: str, new: str) -> None:
    profiles = _load_profiles()
    changed = False
    for profile, members in profiles.items():
        if old in members:
            profiles[profile] = [new if m == old else m for m in members]
            changed = True
    if changed:
        _save_profiles(profiles)
