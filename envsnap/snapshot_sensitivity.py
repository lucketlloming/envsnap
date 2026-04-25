"""Snapshot sensitivity analysis — classify keys by sensitivity level."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

from envsnap.storage import load_snapshot, list_snapshots

# Patterns that suggest a key holds sensitive data
_SENSITIVE_PATTERNS: List[re.Pattern] = [
    re.compile(r"(password|passwd|secret|token|api[_-]?key|private[_-]?key)", re.I),
    re.compile(r"(auth|credential|cred|cert|pem|rsa|dsa)", re.I),
    re.compile(r"(access[_-]?key|session[_-]?id|client[_-]?secret)", re.I),
]

_MODERATE_PATTERNS: List[re.Pattern] = [
    re.compile(r"(email|user|username|login|account)", re.I),
    re.compile(r"(host|endpoint|url|uri|dsn|connection)", re.I),
    re.compile(r"(port|database|db[_-]?name)", re.I),
]

LEVEL_SENSITIVE = "sensitive"
LEVEL_MODERATE = "moderate"
LEVEL_PUBLIC = "public"


@dataclass
class SensitivityResult:
    snapshot: str
    sensitive: List[str] = field(default_factory=list)
    moderate: List[str] = field(default_factory=list)
    public: List[str] = field(default_factory=list)
    score: float = 0.0  # 0.0 (all public) – 1.0 (all sensitive)

    def as_dict(self) -> Dict:
        return {
            "snapshot": self.snapshot,
            "sensitive": self.sensitive,
            "moderate": self.moderate,
            "public": self.public,
            "score": round(self.score, 3),
        }


def _classify_key(key: str) -> str:
    for pat in _SENSITIVE_PATTERNS:
        if pat.search(key):
            return LEVEL_SENSITIVE
    for pat in _MODERATE_PATTERNS:
        if pat.search(key):
            return LEVEL_MODERATE
    return LEVEL_PUBLIC


def analyze_sensitivity(snapshot_name: str) -> SensitivityResult:
    data = load_snapshot(snapshot_name)
    result = SensitivityResult(snapshot=snapshot_name)
    for key in data:
        level = _classify_key(key)
        if level == LEVEL_SENSITIVE:
            result.sensitive.append(key)
        elif level == LEVEL_MODERATE:
            result.moderate.append(key)
        else:
            result.public.append(key)
    total = len(data)
    if total:
        result.score = (len(result.sensitive) + 0.5 * len(result.moderate)) / total
    return result


def analyze_all_sensitivity() -> List[SensitivityResult]:
    return [analyze_sensitivity(name) for name in list_snapshots()]


def format_sensitivity(result: SensitivityResult) -> str:
    lines = [f"Snapshot : {result.snapshot}", f"Score    : {result.score:.3f}"]
    if result.sensitive:
        lines.append(f"Sensitive: {', '.join(sorted(result.sensitive))}")
    if result.moderate:
        lines.append(f"Moderate : {', '.join(sorted(result.moderate))}")
    if result.public:
        lines.append(f"Public   : {', '.join(sorted(result.public))}")
    return "\n".join(lines)
