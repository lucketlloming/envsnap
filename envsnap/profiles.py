"""Profile management: group snapshots under named profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envsnap.storage import get_snapshot_dir


def _profiles_path() -> Path:
    return get_snapshot_dir() / "profiles.json"


def _load_profiles() -> Dict[str, List[str]]:
    p = _profiles_path()
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_profiles(data: Dict[str, List[str]]) -> None:
    with _profiles_path().open("w") as f:
        json.dump(data, f, indent=2)


def add_to_profile(profile: str, snapshot_name: str) -> None:
    """Add a snapshot to a profile."""
    data = _load_profiles()
    entries = data.setdefault(profile, [])
    if snapshot_name not in entries:
        entries.append(snapshot_name)
    _save_profiles(data)


def remove_from_profile(profile: str, snapshot_name: str) -> None:
    """Remove a snapshot from a profile."""
    data = _load_profiles()
    if profile in data:
        data[profile] = [s for s in data[profile] if s != snapshot_name]
        if not data[profile]:
            del data[profile]
    _save_profiles(data)


def get_profile(profile: str) -> List[str]:
    """Return snapshot names belonging to a profile."""
    return _load_profiles().get(profile, [])


def list_profiles() -> List[str]:
    """Return all profile names."""
    return list(_load_profiles().keys())


def delete_profile(profile: str) -> None:
    """Delete an entire profile."""
    data = _load_profiles()
    data.pop(profile, None)
    _save_profiles(data)
