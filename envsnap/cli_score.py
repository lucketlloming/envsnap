"""CLI commands for snapshot scoring."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_score import score_snapshot, format_score
from envsnap.storage import list_snapshots


@click.group("score")
def score_cmd() -> None:
    """Snapshot quality scoring."""


@score_cmd.command("show")
@click.argument("name")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def score_show(name: str, fmt: str) -> None:
    """Show the quality score for a snapshot."""
    try:
        result = score_snapshot(name)
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{name}' not found.")

    if fmt == "json":
        click.echo(json.dumps({
            "snapshot": result.snapshot,
            "score": result.score,
            "breakdown": result.breakdown,
            "penalties": result.penalties,
        }, indent=2))
    else:
        click.echo(format_score(result))


@score_cmd.command("all")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
@click.option("--min-score", default=0, type=int, help="Only show snapshots with score >= this value.")
def score_all(fmt: str, min_score: int) -> None:
    """Score all snapshots and display a ranked list."""
    names = list_snapshots()
    if not names:
        click.echo("No snapshots found.")
        return

    results = [score_snapshot(n) for n in names]
    results = [r for r in results if r.score >= min_score]
    results.sort(key=lambda r: r.score, reverse=True)

    if fmt == "json":
        click.echo(json.dumps(
            [{"snapshot": r.snapshot, "score": r.score} for r in results],
            indent=2,
        ))
    else:
        click.echo(f"{'Snapshot':<30} {'Score':>5}")
        click.echo("-" * 37)
        for r in results:
            click.echo(f"{r.snapshot:<30} {r.score:>5}/100")
