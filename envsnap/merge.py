"""Merge two snapshots into a new one."""
from __future__ import annotations
from typing import Literal
from envsnap.storage import load_snapshot, save_snapshot

Strategy = Literal["ours", "theirs", "union"]


class MergeConflictError(Exception):
    """Raised when keys conflict and strategy is not set to resolve them."""


def merge_snapshots(
    name_a: str,
    name_b: str,
    output: str,
    strategy: Strategy = "union",
) -> dict[str, str]:
    """Merge snapshot *name_a* and *name_b* into *output*.

    Strategies
    ----------
    union  – keep all keys; conflicts resolved by preferring *name_a*.
    ours   – start with *name_a*, add keys only present in *name_b*.
    theirs – start with *name_b*, add keys only present in *name_a*.
    """
    data_a: dict[str, str] = load_snapshot(name_a)
    data_b: dict[str, str] = load_snapshot(name_b)

    if strategy == "union":
        merged = {**data_b, **data_a}  # a wins on conflict
    elif strategy == "ours":
        extra = {k: v for k, v in data_b.items() if k not in data_a}
        merged = {**data_a, **extra}
    elif strategy == "theirs":
        extra = {k: v for k, v in data_a.items() if k not in data_b}
        merged = {**data_b, **extra}
    else:
        raise ValueError(f"Unknown strategy: {strategy!r}")

    save_snapshot(output, merged)
    return merged


def conflicts(name_a: str, name_b: str) -> dict[str, tuple[str, str]]:
    """Return keys that exist in both snapshots but have different values."""
    data_a = load_snapshot(name_a)
    data_b = load_snapshot(name_b)
    return {
        k: (data_a[k], data_b[k])
        for k in data_a.keys() & data_b.keys()
        if data_a[k] != data_b[k]
    }
