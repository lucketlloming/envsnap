"""CLI commands for snapshot dependency management."""

from __future__ import annotations

import json

import click

from envsnap.dependency import (
    DependencyError,
    SnapshotNotFoundError,
    CircularDependencyError,
    add_dependency,
    remove_dependency,
    get_dependencies,
    get_dependents,
    all_dependencies,
)


@click.group("dependency")
def dependency_cmd():
    """Manage snapshot dependencies."""


@dependency_cmd.command("add")
@click.argument("snapshot")
@click.argument("depends_on")
def dep_add(snapshot: str, depends_on: str) -> None:
    """Add DEPENDS_ON as a dependency of SNAPSHOT."""
    try:
        add_dependency(snapshot, depends_on)
        click.echo(f"Added dependency: '{snapshot}' -> '{depends_on}'")
    except (SnapshotNotFoundError, CircularDependencyError, DependencyError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@dependency_cmd.command("remove")
@click.argument("snapshot")
@click.argument("depends_on")
def dep_remove(snapshot: str, depends_on: str) -> None:
    """Remove DEPENDS_ON from SNAPSHOT's dependencies."""
    try:
        remove_dependency(snapshot, depends_on)
        click.echo(f"Removed dependency: '{snapshot}' -> '{depends_on}'")
    except DependencyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@dependency_cmd.command("show")
@click.argument("snapshot")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def dep_show(snapshot: str, as_json: bool) -> None:
    """Show dependencies of SNAPSHOT."""
    deps = get_dependencies(snapshot)
    dependents = get_dependents(snapshot)
    if as_json:
        click.echo(json.dumps({"dependencies": deps, "dependents": dependents}, indent=2))
    else:
        click.echo(f"Dependencies of '{snapshot}':")
        for d in deps:
            click.echo(f"  - {d}")
        if not deps:
            click.echo("  (none)")
        click.echo(f"Dependents of '{snapshot}':")
        for d in dependents:
            click.echo(f"  - {d}")
        if not dependents:
            click.echo("  (none)")


@dependency_cmd.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def dep_list(as_json: bool) -> None:
    """List all snapshot dependencies."""
    data = all_dependencies()
    if as_json:
        click.echo(json.dumps(data, indent=2))
    else:
        if not data:
            click.echo("No dependencies defined.")
            return
        for snap, deps in data.items():
            click.echo(f"{snap}: {', '.join(deps)}")
