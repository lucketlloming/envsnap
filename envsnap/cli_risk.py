"""CLI commands for snapshot risk assessment."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_risk import assess_risk, assess_all_risk, format_risk
from envsnap.storage import list_snapshots


@click.group("risk")
def risk_cmd() -> None:
    """Assess risk level of snapshots."""


@risk_cmd.command("show")
@click.argument("snapshot")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def risk_show(snapshot: str, fmt: str) -> None:
    """Show risk assessment for a single snapshot."""
    try:
        result = assess_risk(snapshot)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    if fmt == "json":
        click.echo(json.dumps(result.as_dict(), indent=2))
    else:
        click.echo(format_risk(result))


@risk_cmd.command("all")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
@click.option("--min-level", default="low", type=click.Choice(["low", "medium", "high", "critical"]), show_default=True)
def risk_all(fmt: str, min_level: str) -> None:
    """Show risk assessment for all snapshots."""
    _order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    threshold = _order[min_level]

    names = list_snapshots()
    if not names:
        click.echo("No snapshots found.")
        return

    results = assess_all_risk(names)
    filtered = [r for r in results if _order[r.level] >= threshold]
    filtered.sort(key=lambda r: r.score, reverse=True)

    if not filtered:
        click.echo(f"No snapshots at or above '{min_level}' risk level.")
        return

    if fmt == "json":
        click.echo(json.dumps([r.as_dict() for r in filtered], indent=2))
    else:
        for r in filtered:
            click.echo(format_risk(r))
            click.echo()
