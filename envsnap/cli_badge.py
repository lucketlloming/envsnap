"""CLI commands for snapshot badges."""
from __future__ import annotations

import json
from pathlib import Path

import click

from envsnap.snapshot_badge import generate_badge, Badge
from envsnap.storage import list_snapshots


@click.group("badge")
def badge_cmd() -> None:
    """Generate status badges for snapshots."""


@badge_cmd.command("show")
@click.argument("name")
@click.option("--format", "fmt", type=click.Choice(["text", "json", "svg", "markdown"]), default="text")
def badge_show(name: str, fmt: str) -> None:
    """Show the badge for a snapshot."""
    try:
        badge = generate_badge(name)
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{name}' not found.")

    if fmt == "json":
        click.echo(json.dumps(badge.as_dict(), indent=2))
    elif fmt == "svg":
        click.echo(badge.as_svg())
    elif fmt == "markdown":
        click.echo(badge.as_markdown())
    else:
        click.echo(f"Snapshot : {badge.snapshot}")
        click.echo(f"Score    : {badge.score}/100")
        click.echo(f"Level    : {badge.level}")
        click.echo(f"Color    : {badge.color}")


@badge_cmd.command("export")
@click.argument("name")
@click.argument("output", type=click.Path())
@click.option("--format", "fmt", type=click.Choice(["svg", "json"]), default="svg")
def badge_export(name: str, output: str, fmt: str) -> None:
    """Export a badge to a file."""
    try:
        badge = generate_badge(name)
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{name}' not found.")

    content = badge.as_svg() if fmt == "svg" else json.dumps(badge.as_dict(), indent=2)
    Path(output).write_text(content, encoding="utf-8")
    click.echo(f"Badge exported to {output}")


@badge_cmd.command("all")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
def badge_all(fmt: str) -> None:
    """Show badges for all snapshots."""
    names = list_snapshots()
    if not names:
        click.echo("No snapshots found.")
        return

    badges = [generate_badge(n) for n in names]

    if fmt == "json":
        click.echo(json.dumps([b.as_dict() for b in badges], indent=2))
    else:
        for b in badges:
            click.echo(f"{b.snapshot:<30} {b.score:>3}/100  [{b.level}]")
