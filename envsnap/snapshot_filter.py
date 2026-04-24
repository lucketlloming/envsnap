"""Filter snapshots by various criteria."""
from __future__ import annotations

from typing import Callable

from envsnap.storage import list_snapshots, load_snapshot


FilterFn = Callable[[str], bool]


def filter_by_key_prefix(prefix: str) -> list[str]:
    """Return snapshot names that contain at least one key with the given prefix."""
    results = []
    for name in list_snapshots():
        data = load_snapshot(name)
        if any(k.startswith(prefix) for k in data):
            results.append(name)
    return results


def filter_by_key_count(min_keys: int = 0, max_keys: int | None = None) -> list[str]:
    """Return snapshot names whose key count falls within [min_keys, max_keys]."""
    results = []
    for name in list_snapshots():
        data = load_snapshot(name)
        count = len(data)
        if count < min_keys:
            continue
        if max_keys is not None and count > max_keys:
            continue
        results.append(name)
    return results


def filter_by_value_pattern(pattern: str) -> list[str]:
    """Return snapshot names that contain at least one value matching a substring."""
    results = []
    for name in list_snapshots():
        data = load_snapshot(name)
        if any(pattern in v for v in data.values()):
            results.append(name)
    return results


def filter_snapshots(
    key_prefix: str | None = None,
    min_keys: int = 0,
    max_keys: int | None = None,
    value_pattern: str | None = None,
) -> list[str]:
    """Combine multiple filters and return matching snapshot names."""
    candidates = set(list_snapshots())

    if key_prefix is not None:
        candidates &= set(filter_by_key_prefix(key_prefix))
    if min_keys > 0 or max_keys is not None:
        candidates &= set(filter_by_key_count(min_keys, max_keys))
    if value_pattern is not None:
        candidates &= set(filter_by_value_pattern(value_pattern))

    return sorted(candidates)
