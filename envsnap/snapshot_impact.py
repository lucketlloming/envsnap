"""Assess the impact of a snapshot based on dependencies, dependents, and group membership."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envsnap import storage, dependency, group as group_mod


@dataclass
class ImpactResult:
    name: str
    dependency_count: int
    dependent_count: int
    group_count: int
    score: float
    level: str
    groups: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    dependents: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "dependency_count": self.dependency_count,
            "dependent_count": self.dependent_count,
            "group_count": self.group_count,
            "score": self.score,
            "level": self.level,
            "groups": self.groups,
            "dependencies": self.dependencies,
            "dependents": self.dependents,
        }


def _level(score: float) -> str:
    if score >= 0.7:
        return "high"
    if score >= 0.35:
        return "medium"
    return "low"


def assess_impact(name: str) -> ImpactResult:
    """Compute an impact score for *name* based on its relationships."""
    all_snaps = storage.list_snapshots()
    if name not in all_snaps:
        raise KeyError(f"Snapshot '{name}' not found.")

    deps = dependency.get_dependencies(name)
    dependents: list[str] = []
    for snap in all_snaps:
        try:
            if name in dependency.get_dependencies(snap):
                dependents.append(snap)
        except Exception:
            pass

    all_groups = group_mod.list_groups()
    snap_groups = [g for g, members in all_groups.items() if name in members]

    total = len(all_snaps) or 1
    raw = (
        len(deps) * 1.0
        + len(dependents) * 2.0
        + len(snap_groups) * 0.5
    )
    score = min(raw / (total * 0.5 + 1), 1.0)

    return ImpactResult(
        name=name,
        dependency_count=len(deps),
        dependent_count=len(dependents),
        group_count=len(snap_groups),
        score=round(score, 4),
        level=_level(score),
        groups=snap_groups,
        dependencies=list(deps),
        dependents=dependents,
    )


def assess_all_impact() -> list[ImpactResult]:
    return [assess_impact(n) for n in storage.list_snapshots()]


def format_impact(result: ImpactResult) -> str:
    lines = [
        f"Snapshot : {result.name}",
        f"Level    : {result.level} (score={result.score:.4f})",
        f"Deps     : {result.dependency_count}  {result.dependencies}",
        f"Dependents: {result.dependent_count}  {result.dependents}",
        f"Groups   : {result.group_count}  {result.groups}",
    ]
    return "\n".join(lines)
