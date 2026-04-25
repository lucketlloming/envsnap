"""CLI commands for snapshot vitals."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_vitals import compute_vitals, compute_all_vitals, format_vitals
from envsnap.storage import load_snapshot


@click.group("vitals")
def vitals_cmd():
    """Show quick vitals for snapshots."""


@vitals_cmd.command("show")
@click.argument("name")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
def vitals_show(name: str, fmt: str):
    """Show vitals for a single snapshot."""
    try:
        result = compute_vitals(name)
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{name}' not found.")

    if fmt == "json":
        click.echo(json.dumps(result.as_dict(), indent=2))
    else:
        click.echo(format_vitals(result))


@vitals_cmd.command("all")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
def vitals_all(fmt: str):
    """Show vitals for all snapshots."""
    results = compute_all_vitals()
    if not results:
        click.echo("No snapshots found.")
        return

    if fmt == "json":
        click.echo(json.dumps([r.as_dict() for r in results], indent=2))
    else:
        for r in results:
            click.echo(format_vitals(r))
            click.echo("---")
