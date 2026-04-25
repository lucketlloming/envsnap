"""CLI commands for snapshot sensitivity analysis."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_sensitivity import (
    analyze_sensitivity,
    analyze_all_sensitivity,
    format_sensitivity,
)
from envsnap.storage import list_snapshots


@click.group("sensitivity")
def sensitivity_cmd():
    """Analyse key sensitivity levels in snapshots."""


@sensitivity_cmd.command("show")
@click.argument("snapshot")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def sensitivity_show(snapshot: str, fmt: str):
    """Show sensitivity analysis for a single snapshot."""
    try:
        result = analyze_sensitivity(snapshot)
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{snapshot}' not found.")
    if fmt == "json":
        click.echo(json.dumps(result.as_dict(), indent=2))
    else:
        click.echo(format_sensitivity(result))


@sensitivity_cmd.command("all")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
@click.option("--min-score", default=0.0, type=float, help="Only show results above this score.")
def sensitivity_all(fmt: str, min_score: float):
    """Show sensitivity analysis for all snapshots."""
    names = list_snapshots()
    if not names:
        click.echo("No snapshots found.")
        return
    results = [r for r in analyze_all_sensitivity() if r.score >= min_score]
    if not results:
        click.echo("No snapshots match the given threshold.")
        return
    if fmt == "json":
        click.echo(json.dumps([r.as_dict() for r in results], indent=2))
    else:
        for r in results:
            click.echo(format_sensitivity(r))
            click.echo("")
