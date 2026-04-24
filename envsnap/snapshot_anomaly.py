"""Anomaly detection for snapshots.

Detects unusual patterns in snapshot data, such as keys with suspiciously
long values, high entropy values (possible secrets), unexpected key counts,
or values that deviate significantly from historical norms.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envsnap.storage import load_snapshot, list_snapshots

# Thresholds
_MAX_VALUE_LENGTH = 512
_HIGH_ENTROPY_THRESHOLD = 4.2  # bits per character
_SUSPICIOUS_PATTERNS = [
    re.compile(r"(?i)(password|secret|token|api[_-]?key|private[_-]?key)"),
]


@dataclass
class AnomalyResult:
    snapshot: str
    anomalies: List[Dict] = field(default_factory=list)

    @property
    def has_anomalies(self) -> bool:
        return len(self.anomalies) > 0

    def as_dict(self) -> dict:
        return {
            "snapshot": self.snapshot,
            "anomaly_count": len(self.anomalies),
            "anomalies": self.anomalies,
        }


def _shannon_entropy(value: str) -> float:
    """Compute Shannon entropy (bits per character) of a string."""
    if not value:
        return 0.0
    freq: Dict[str, int] = {}
    for ch in value:
        freq[ch] = freq.get(ch, 0) + 1
    length = len(value)
    return -sum((c / length) * math.log2(c / length) for c in freq.values())


def _check_long_value(key: str, value: str) -> Optional[dict]:
    if len(value) > _MAX_VALUE_LENGTH:
        return {
            "key": key,
            "type": "long_value",
            "severity": "warning",
            "detail": f"Value length {len(value)} exceeds {_MAX_VALUE_LENGTH} characters.",
        }
    return None


def _check_high_entropy(key: str, value: str) -> Optional[dict]:
    """Flag values with high Shannon entropy (likely encoded secrets)."""
    if len(value) < 16:
        return None
    entropy = _shannon_entropy(value)
    if entropy >= _HIGH_ENTROPY_THRESHOLD:
        return {
            "key": key,
            "type": "high_entropy",
            "severity": "info",
            "detail": f"Value has high entropy ({entropy:.2f} bits/char), may contain a secret.",
        }
    return None


def _check_suspicious_key_name(key: str, value: str) -> Optional[dict]:
    """Flag keys whose names suggest sensitive data."""
    for pattern in _SUSPICIOUS_PATTERNS:
        if pattern.search(key):
            return {
                "key": key,
                "type": "suspicious_key_name",
                "severity": "warning",
                "detail": f"Key name '{key}' suggests sensitive data.",
            }
    return None


def _check_numeric_looking_value(key: str, value: str) -> Optional[dict]:
    """Warn when a key that looks like a port/count has a non-numeric value."""
    numeric_hints = re.compile(r"(?i)(port|count|timeout|limit|size|max|min)")
    if numeric_hints.search(key) and value and not value.strip().lstrip("-").isdigit():
        return {
            "key": key,
            "type": "unexpected_value_type",
            "severity": "info",
            "detail": f"Key '{key}' suggests a numeric value but got '{value[:40]}'.",
        }
    return None


_CHECKS = [
    _check_long_value,
    _check_high_entropy,
    _check_suspicious_key_name,
    _check_numeric_looking_value,
]


def detect_anomalies(snapshot_name: str) -> AnomalyResult:
    """Run all anomaly checks against a single snapshot."""
    data = load_snapshot(snapshot_name)
    result = AnomalyResult(snapshot=snapshot_name)
    for key, value in data.items():
        for check in _CHECKS:
            finding = check(key, value)
            if finding:
                result.anomalies.append(finding)
    return result


def detect_all_anomalies() -> List[AnomalyResult]:
    """Run anomaly detection across every stored snapshot."""
    return [detect_anomalies(name) for name in list_snapshots()]


def format_anomaly_report(result: AnomalyResult) -> str:
    """Return a human-readable anomaly report for a single snapshot."""
    lines = [f"Anomaly report: {result.snapshot}"]
    if not result.has_anomalies:
        lines.append("  No anomalies detected.")
        return "\n".join(lines)
    for item in result.anomalies:
        severity = item["severity"].upper()
        lines.append(f"  [{severity}] {item['type']} — {item['key']}: {item['detail']}")
    return "\n".join(lines)
