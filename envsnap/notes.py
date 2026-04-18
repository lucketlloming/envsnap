"""Attach and retrieve notes for snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envsnap.storage import get_snapshot_dir, snapshot_path


def _notes_path(snapshot_dir: Optional[Path] = None) -> Path:
    return (snapshot_dir or get_snapshot_dir()) / "notes.json"


def _load_notes(snapshot_dir: Optional[Path] = None) -> dict:
    p = _notes_path(snapshot_dir)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_notes(data: dict, snapshot_dir: Optional[Path] = None) -> None:
    p = _notes_path(snapshot_dir)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def set_note(name: str, note: str, snapshot_dir: Optional[Path] = None) -> None:
    """Attach a note to a snapshot. Raises FileNotFoundError if snapshot missing."""
    snap = snapshot_path(name, snapshot_dir)
    if not snap.exists():
        raise FileNotFoundError(f"Snapshot '{name}' does not exist.")
    data = _load_notes(snapshot_dir)
    data[name] = note
    _save_notes(data, snapshot_dir)


def get_note(name: str, snapshot_dir: Optional[Path] = None) -> Optional[str]:
    """Return the note for a snapshot, or None if not set."""
    return _load_notes(snapshot_dir).get(name)


def remove_note(name: str, snapshot_dir: Optional[Path] = None) -> None:
    """Remove a note from a snapshot. Raises KeyError if no note exists."""
    data = _load_notes(snapshot_dir)
    if name not in data:
        raise KeyError(f"No note found for snapshot '{name}'.")
    del data[name]
    _save_notes(data, snapshot_dir)


def list_notes(snapshot_dir: Optional[Path] = None) -> dict:
    """Return all snapshot notes as a dict."""
    return _load_notes(snapshot_dir)
