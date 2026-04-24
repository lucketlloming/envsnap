"""Compute similarity scores between snapshots based on shared keys/values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envsnap.storage import load_snapshot, list_snapshots


@dataclass
class SimilarityResult:
    snapshot_a: str
    snapshot_b: str
    shared_keys: List[str] = field(default_factory=list)
    shared_key_value_pairs: List[str] = field(default_factory=list)
    key_similarity: float = 0.0
    value_similarity: float = 0.0
    overall_score: float = 0.0

    def as_dict(self) -> dict:
        return {
            "snapshot_a": self.snapshot_a,
            "snapshot_b": self.snapshot_b,
            "shared_keys": self.shared_keys,
            "shared_key_value_pairs": self.shared_key_value_pairs,
            "key_similarity": round(self.key_similarity, 4),
            "value_similarity": round(self.value_similarity, 4),
            "overall_score": round(self.overall_score, 4),
        }


def _jaccard(set_a: set, set_b: set) -> float:
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)


def compute_similarity(name_a: str, name_b: str) -> SimilarityResult:
    """Compute similarity between two named snapshots."""
    data_a = load_snapshot(name_a)
    data_b = load_snapshot(name_b)

    keys_a = set(data_a.keys())
    keys_b = set(data_b.keys())
    shared_keys = sorted(keys_a & keys_b)

    pairs_a = {(k, v) for k, v in data_a.items()}
    pairs_b = {(k, v) for k, v in data_b.items()}
    shared_pairs = sorted(f"{k}={v}" for k, v in pairs_a & pairs_b)

    key_sim = _jaccard(keys_a, keys_b)
    val_sim = _jaccard(pairs_a, pairs_b)
    overall = (key_sim + val_sim) / 2.0

    return SimilarityResult(
        snapshot_a=name_a,
        snapshot_b=name_b,
        shared_keys=shared_keys,
        shared_key_value_pairs=shared_pairs,
        key_similarity=key_sim,
        value_similarity=val_sim,
        overall_score=overall,
    )


def find_similar(
    name: str,
    threshold: float = 0.3,
    top_n: Optional[int] = None,
) -> List[SimilarityResult]:
    """Find snapshots similar to *name* above *threshold* overall score."""
    others = [n for n in list_snapshots() if n != name]
    results = []
    for other in others:
        try:
            result = compute_similarity(name, other)
        except Exception:
            continue
        if result.overall_score >= threshold:
            results.append(result)
    results.sort(key=lambda r: r.overall_score, reverse=True)
    if top_n is not None:
        results = results[:top_n]
    return results


def format_similarity(result: SimilarityResult) -> str:
    lines = [
        f"Similarity: {result.snapshot_a} <-> {result.snapshot_b}",
        f"  Overall score : {result.overall_score:.2%}",
        f"  Key similarity: {result.key_similarity:.2%}",
        f"  Val similarity: {result.value_similarity:.2%}",
        f"  Shared keys   : {', '.join(result.shared_keys) or '(none)'}",
    ]
    if result.shared_key_value_pairs:
        lines.append(f"  Shared kv pairs: {', '.join(result.shared_key_value_pairs)}")
    return "\n".join(lines)
