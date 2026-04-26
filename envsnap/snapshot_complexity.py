"""Snapshot complexity analysis — measures structural complexity of a snapshot."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from envsnap.storage import load_snapshot, list_snapshots


@dataclass
class ComplexityResult:
    name: str
    key_count: int
    unique_value_count: int
    avg_key_length: float
    avg_value_length: float
    duplication_ratio: float  # 0.0 = all unique values, 1.0 = all duplicates
    score: float              # 0.0 (simple) .. 100.0 (complex)
    level: str                # "low" | "medium" | "high"

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "key_count": self.key_count,
            "unique_value_count": self.unique_value_count,
            "avg_key_length": round(self.avg_key_length, 2),
            "avg_value_length": round(self.avg_value_length, 2),
            "duplication_ratio": round(self.duplication_ratio, 4),
            "score": round(self.score, 2),
            "level": self.level,
        }


def _level(score: float) -> str:
    if score >= 60:
        return "high"
    if score >= 30:
        return "medium"
    return "low"


def compute_complexity(name: str) -> ComplexityResult:
    data: dict = load_snapshot(name)

    key_count = len(data)
    if key_count == 0:
        return ComplexityResult(
            name=name,
            key_count=0,
            unique_value_count=0,
            avg_key_length=0.0,
            avg_value_length=0.0,
            duplication_ratio=0.0,
            score=0.0,
            level="low",
        )

    keys = list(data.keys())
    values = list(data.values())
    unique_values = set(values)

    avg_key_len = sum(len(k) for k in keys) / key_count
    avg_val_len = sum(len(v) for v in values) / key_count
    duplication_ratio = 1.0 - (len(unique_values) / key_count)

    # Score: weighted combination of key count, lengths, and duplication
    count_component = min(key_count / 50.0, 1.0) * 40
    length_component = min((avg_key_len + avg_val_len) / 80.0, 1.0) * 40
    dup_component = duplication_ratio * 20
    score = count_component + length_component + dup_component

    return ComplexityResult(
        name=name,
        key_count=key_count,
        unique_value_count=len(unique_values),
        avg_key_length=avg_key_len,
        avg_value_length=avg_val_len,
        duplication_ratio=duplication_ratio,
        score=score,
        level=_level(score),
    )


def compute_all_complexity() -> list[ComplexityResult]:
    return [compute_complexity(name) for name in list_snapshots()]


def format_complexity(result: ComplexityResult) -> str:
    lines = [
        f"Snapshot : {result.name}",
        f"Keys     : {result.key_count}",
        f"Unique V : {result.unique_value_count}",
        f"Avg Key  : {result.avg_key_length:.2f} chars",
        f"Avg Val  : {result.avg_value_length:.2f} chars",
        f"Dup Ratio: {result.duplication_ratio:.2%}",
        f"Score    : {result.score:.2f} / 100",
        f"Level    : {result.level.upper()}",
    ]
    return "\n".join(lines)
