"""Build and format a dependency/relationship graph for snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envsnap.dependency import get_dependencies, SnapshotNotFoundError
from envsnap.storage import list_snapshots


@dataclass
class GraphNode:
    name: str
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "dependencies": self.dependencies,
            "dependents": self.dependents,
        }


def build_graph(snapshot_name: Optional[str] = None) -> Dict[str, GraphNode]:
    """Build a graph of snapshot dependencies.

    If *snapshot_name* is given, only that snapshot and its transitive
    dependencies/dependents are included.  Otherwise the full graph is built.
    """
    all_names = list_snapshots()
    nodes: Dict[str, GraphNode] = {n: GraphNode(name=n) for n in all_names}

    for name in all_names:
        try:
            deps = get_dependencies(name)
        except SnapshotNotFoundError:
            deps = []
        nodes[name].dependencies = list(deps)
        for dep in deps:
            if dep in nodes:
                nodes[dep].dependents.append(name)

    if snapshot_name is not None:
        if snapshot_name not in nodes:
            raise SnapshotNotFoundError(snapshot_name)
        # Collect reachable nodes (both directions) via BFS
        visited = set()
        queue = [snapshot_name]
        while queue:
            current = queue.pop()
            if current in visited:
                continue
            visited.add(current)
            node = nodes.get(current)
            if node:
                queue.extend(node.dependencies)
                queue.extend(node.dependents)
        nodes = {k: v for k, v in nodes.items() if k in visited}

    return nodes


def format_graph(nodes: Dict[str, GraphNode], fmt: str = "text") -> str:
    """Render the graph as *text* or *json*."""
    if fmt == "json":
        import json
        return json.dumps({k: v.as_dict() for k, v in nodes.items()}, indent=2)

    if not nodes:
        return "No snapshots found."

    lines: List[str] = []
    for name, node in sorted(nodes.items()):
        lines.append(f"[{name}]")
        if node.dependencies:
            lines.append("  depends on : " + ", ".join(sorted(node.dependencies)))
        if node.dependents:
            lines.append("  required by: " + ", ".join(sorted(node.dependents)))
        if not node.dependencies and not node.dependents:
            lines.append("  (no relationships)")
    return "\n".join(lines)
