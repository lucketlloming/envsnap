"""Compute and report entropy metrics for snapshots."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envsnap.storage import load_snapshot, list_snapshots


@dataclass
class EntropyResult:
    name: str
    key_count: int
    unique_values: int
    value_entropy: float  # Shannon entropy over value distribution
    avg_value_length: float
    level: str  # 'high' | 'medium' | 'low'

    def as_dict(self) -> Dict:
        return {
            "name": self.name,
            "key_count": self.key_count,
            "unique_values": self.unique_values,
            "value_entropy": round(self.value_entropy, 4),
            "avg_value_length": round(self.avg_value_length, 2),
            "level": self.level,
        }


def _shannon_entropy(values: List[str]) -> float:
    """Compute Shannon entropy of a list of string values."""
    if not values:
        return 0.0
    freq: Dict[str, int] = {}
    for v in values:
        freq[v] = freq.get(v, 0) + 1
    total = len(values)
    return -sum((c / total) * math.log2(c / total) for c in freq.values())


def _level(entropy: float) -> str:
    if entropy >= 3.0:
        return "high"
    if entropy >= 1.0:
        return "medium"
    return "low"


def compute_entropy(name: str) -> EntropyResult:
    """Compute entropy metrics for a single snapshot."""
    data = load_snapshot(name)
    values = list(data.values())
    key_count = len(values)
    unique_values = len(set(values))
    entropy = _shannon_entropy(values)
    avg_len = (sum(len(v) for v in values) / key_count) if key_count else 0.0
    return EntropyResult(
        name=name,
        key_count=key_count,
        unique_values=unique_values,
        value_entropy=entropy,
        avg_value_length=avg_len,
        level=_level(entropy),
    )


def compute_all_entropy() -> List[EntropyResult]:
    """Compute entropy metrics for all snapshots."""
    return [compute_entropy(n) for n in list_snapshots()]


def format_entropy(result: EntropyResult) -> str:
    lines = [
        f"Snapshot : {result.name}",
        f"Keys     : {result.key_count}",
        f"Unique V : {result.unique_values}",
        f"Entropy  : {result.value_entropy:.4f}  [{result.level}]",
        f"Avg Len  : {result.avg_value_length:.2f}",
    ]
    return "\n".join(lines)
