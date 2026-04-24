"""Generate status badges for snapshots based on score, lint, and validation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from envsnap.snapshot_score import score_snapshot, ScoreResult

BadgeLevel = Literal["excellent", "good", "fair", "poor"]

SVG_TEMPLATE = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="20">'
    '<rect width="70" height="20" fill="#555"/>'
    '<rect x="70" width="50" height="20" fill="{color}"/>'
    '<text x="35" y="14" fill="#fff" font-size="11" font-family="sans-serif" text-anchor="middle">envsnap</text>'
    '<text x="95" y="14" fill="#fff" font-size="11" font-family="sans-serif" text-anchor="middle">{label}</text>'
    '</svg>'
)

_LEVEL_COLOR: dict[BadgeLevel, str] = {
    "excellent": "#4c1",
    "good": "#97ca00",
    "fair": "#dfb317",
    "poor": "#e05d44",
}


@dataclass
class Badge:
    snapshot: str
    score: int
    level: BadgeLevel
    color: str
    label: str

    def as_dict(self) -> dict:
        return {
            "snapshot": self.snapshot,
            "score": self.score,
            "level": self.level,
            "color": self.color,
            "label": self.label,
        }

    def as_svg(self) -> str:
        return SVG_TEMPLATE.format(color=self.color, label=self.label)

    def as_markdown(self) -> str:
        return f"![envsnap score: {self.label}](badge:{self.snapshot})"


def _level_from_score(score: int) -> BadgeLevel:
    if score >= 90:
        return "excellent"
    if score >= 70:
        return "good"
    if score >= 50:
        return "fair"
    return "poor"


def generate_badge(name: str) -> Badge:
    """Generate a Badge for the given snapshot name."""
    result: ScoreResult = score_snapshot(name)
    level = _level_from_score(result.score)
    color = _LEVEL_COLOR[level]
    label = f"{result.score}/100"
    return Badge(
        snapshot=name,
        score=result.score,
        level=level,
        color=color,
        label=label,
    )
