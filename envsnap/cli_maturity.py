"""CLI commands for snapshot maturity scoring."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_maturity import (
    MaturityNotFoundError,
    format_maturity,
    score_all_maturity,
    score_maturity,
)
from envsnap.storage import SnapshotNotFoundError


@click.group("maturity")
def maturity_cmd() -> None:
    """Snapshot maturity scoring."""


@maturity_cmd.command("show")
@click.argument("name")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
def maturity_show(name: str, fmt: str) -> None:
    """Show maturity score for a single snapshot."""
    try:
        result = score_maturity(name)
    except (SnapshotNotFoundError, KeyError):
        raise click.ClickException(f"Snapshot '{name}' not found.")

    if fmt == "json":
        click.echo(json.dumps(result.as_dict(), indent=2))
    else:
        click.echo(format_maturity(result))


@maturity_cmd.command("all")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
@click.option("--min-score", type=int, default=0, help="Only show snapshots at or above this score.")
def maturity_all(fmt: str, min_score: int) -> None:
    """Show maturity scores for all snapshots."""
    results = [r for r in score_all_maturity() if r.score >= min_score]
    results.sort(key=lambda r: r.score, reverse=True)

    if not results:
        click.echo("No snapshots found.")
        return

    if fmt == "json":
        click.echo(json.dumps([r.as_dict() for r in results], indent=2))
    else:
        for r in results:
            click.echo(f"{r.name:<30} {r.score:>3}/100  [{r.level}]")
