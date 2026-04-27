"""Detect redundant snapshots — snapshots whose key/value sets are identical or near-identical."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envsnap.storage import list_snapshots, load_snapshot


@dataclass
class RedundancyResult:
    snapshot: str
    duplicate_of: Optional[str]
    similarity: float          # 0.0 – 1.0
    is_exact: bool

    def as_dict(self) -> dict:
        return {
            "snapshot": self.snapshot,
            "duplicate_of": self.duplicate_of,
            "similarity": round(self.similarity, 4),
            "is_exact": self.is_exact,
        }


def _jaccard(a: dict, b: dict) -> float:
    keys_a = set(f"{k}={v}" for k, v in a.items())
    keys_b = set(f"{k}={v}" for k, v in b.items())
    if not keys_a and not keys_b:
        return 1.0
    union = keys_a | keys_b
    inter = keys_a & keys_b
    return len(inter) / len(union)


def find_redundant(
    threshold: float = 0.95,
    snapshot_name: str | None = None,
) -> list[RedundancyResult]:
    """Return snapshots that are duplicates or near-duplicates of an earlier snapshot.

    For each snapshot (or just *snapshot_name* when provided), compare against
    all snapshots that appear earlier in the sorted list.  If the Jaccard
    similarity of their key=value pairs meets *threshold* the snapshot is
    flagged as redundant.
    """
    names = sorted(list_snapshots())
    if not names:
        return []

    cache: dict[str, dict] = {}

    def _load(name: str) -> dict:
        if name not in cache:
            cache[name] = load_snapshot(name)
        return cache[name]

    targets = [snapshot_name] if snapshot_name else names
    results: list[RedundancyResult] = []

    for name in targets:
        data = _load(name)
        best_sim = 0.0
        best_match: str | None = None
        for other in names:
            if other == name:
                continue
            sim = _jaccard(data, _load(other))
            if sim > best_sim:
                best_sim = sim
                best_match = other
        if best_sim >= threshold:
            results.append(
                RedundancyResult(
                    snapshot=name,
                    duplicate_of=best_match,
                    similarity=best_sim,
                    is_exact=best_sim == 1.0,
                )
            )

    return results


def format_redundancy(results: list[RedundancyResult]) -> str:
    if not results:
        return "No redundant snapshots found."
    lines = []
    for r in results:
        tag = "EXACT" if r.is_exact else f"{r.similarity:.0%} similar"
        lines.append(f"  {r.snapshot!r:30s} -> {r.duplicate_of!r}  [{tag}]")
    return "Redundant snapshots:\n" + "\n".join(lines)
