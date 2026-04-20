"""Snapshot dependency tracking: define which snapshots depend on others."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envsnap.storage import get_snapshot_dir, list_snapshots


class DependencyError(Exception):
    pass


class SnapshotNotFoundError(DependencyError):
    pass


class CircularDependencyError(DependencyError):
    pass


def _deps_path() -> Path:
    return get_snapshot_dir() / "dependencies.json"


def _load_deps() -> Dict[str, List[str]]:
    p = _deps_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_deps(data: Dict[str, List[str]]) -> None:
    _deps_path().write_text(json.dumps(data, indent=2))


def _has_cycle(graph: Dict[str, List[str]], start: str, target: str) -> bool:
    """Return True if adding start -> target would create a cycle."""
    visited: set = set()
    stack = [target]
    while stack:
        node = stack.pop()
        if node == start:
            return True
        if node in visited:
            continue
        visited.add(node)
        stack.extend(graph.get(node, []))
    return False


def add_dependency(snapshot: str, depends_on: str) -> None:
    existing = list_snapshots()
    if snapshot not in existing:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot}' not found")
    if depends_on not in existing:
        raise SnapshotNotFoundError(f"Snapshot '{depends_on}' not found")
    data = _load_deps()
    if _has_cycle(data, snapshot, depends_on):
        raise CircularDependencyError(
            f"Adding '{depends_on}' as dependency of '{snapshot}' would create a cycle"
        )
    deps = data.setdefault(snapshot, [])
    if depends_on not in deps:
        deps.append(depends_on)
    _save_deps(data)


def remove_dependency(snapshot: str, depends_on: str) -> None:
    data = _load_deps()
    deps = data.get(snapshot, [])
    if depends_on not in deps:
        raise DependencyError(f"'{depends_on}' is not a dependency of '{snapshot}'")
    deps.remove(depends_on)
    if not deps:
        del data[snapshot]
    _save_deps(data)


def get_dependencies(snapshot: str) -> List[str]:
    return _load_deps().get(snapshot, [])


def get_dependents(snapshot: str) -> List[str]:
    """Return snapshots that depend on the given snapshot."""
    return [k for k, v in _load_deps().items() if snapshot in v]


def all_dependencies() -> Dict[str, List[str]]:
    return _load_deps()
