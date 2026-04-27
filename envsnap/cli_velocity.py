"""CLI commands for snapshot velocity reporting."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_velocity import (
    compute_all_velocity,
    compute_velocity,
    format_velocity,
)
from envsnap.storage import list_snapshots


@click.group("velocity")
def velocity_cmd() -> None:
    """Snapshot change-velocity analysis."""


@velocity_cmd.command("show")
@click.argument("name")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def velocity_show(name: str, fmt: str) -> None:
    """Show velocity metrics for a single snapshot."""
    if name not in list_snapshots():
        raise click.ClickException(f"Snapshot '{name}' not found.")
    result = compute_velocity(name)
    if fmt == "json":
        click.echo(json.dumps(result.as_dict(), indent=2))
    else:
        click.echo(format_velocity(result))


@velocity_cmd.command("all")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
@click.option("--min-level", default=None, type=click.Choice(["idle", "low", "moderate", "high"]))
def velocity_all(fmt: str, min_level: str | None) -> None:
    """Show velocity metrics for all snapshots."""
    _order = {"idle": 0, "low": 1, "moderate": 2, "high": 3}
    results = compute_all_velocity()
    if min_level is not None:
        threshold = _order[min_level]
        results = [r for r in results if _order[r.level] >= threshold]
    if not results:
        click.echo("No snapshots match the criteria.")
        return
    if fmt == "json":
        click.echo(json.dumps([r.as_dict() for r in results], indent=2))
    else:
        for r in results:
            click.echo(format_velocity(r))
            click.echo("---")
