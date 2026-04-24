"""Snapshot chaining: link snapshots into ordered sequences."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from envsnap.storage import get_snapshot_dir, list_snapshots


class ChainError(Exception):
    pass


class SnapshotNotFoundError(ChainError):
    pass


def _chains_path() -> Path:
    return get_snapshot_dir() / "chains.json"


def _load_chains() -> dict:
    p = _chains_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_chains(data: dict) -> None:
    _chains_path().write_text(json.dumps(data, indent=2))


def create_chain(chain_name: str, snapshot_names: List[str]) -> None:
    """Create or overwrite a named chain of snapshots."""
    existing = list_snapshots()
    for name in snapshot_names:
        if name not in existing:
            raise SnapshotNotFoundError(f"Snapshot not found: {name}")
    chains = _load_chains()
    chains[chain_name] = list(snapshot_names)
    _save_chains(chains)


def get_chain(chain_name: str) -> List[str]:
    """Return the ordered list of snapshot names for a chain."""
    chains = _load_chains()
    if chain_name not in chains:
        raise ChainError(f"Chain not found: {chain_name}")
    return chains[chain_name]


def delete_chain(chain_name: str) -> None:
    chains = _load_chains()
    if chain_name not in chains:
        raise ChainError(f"Chain not found: {chain_name}")
    del chains[chain_name]
    _save_chains(chains)


def list_chains() -> List[str]:
    return sorted(_load_chains().keys())


def append_to_chain(chain_name: str, snapshot_name: str) -> None:
    existing = list_snapshots()
    if snapshot_name not in existing:
        raise SnapshotNotFoundError(f"Snapshot not found: {snapshot_name}")
    chains = _load_chains()
    if chain_name not in chains:
        raise ChainError(f"Chain not found: {chain_name}")
    if snapshot_name not in chains[chain_name]:
        chains[chain_name].append(snapshot_name)
    _save_chains(chains)
