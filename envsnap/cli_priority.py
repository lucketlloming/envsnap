"""CLI commands for snapshot priority management."""
from __future__ import annotations

import json

import click

from envsnap.priority import (
    InvalidPriorityError,
    SnapshotNotFoundError,
    VALID_PRIORITIES,
    get_priority,
    list_by_priority,
    remove_priority,
    set_priority,
)


@click.group("priority")
def priority_cmd() -> None:
    """Manage snapshot priorities."""


@priority_cmd.command("set")
@click.argument("snapshot")
@click.argument("priority", type=click.Choice(sorted(VALID_PRIORITIES)))
def priority_set(snapshot: str, priority: str) -> None:
    """Set priority for a snapshot."""
    try:
        set_priority(snapshot, priority)
        click.echo(f"Priority for '{snapshot}' set to '{priority}'.")
    except SnapshotNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    except InvalidPriorityError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@priority_cmd.command("show")
@click.argument("snapshot")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def priority_show(snapshot: str, fmt: str) -> None:
    """Show priority of a snapshot."""
    priority = get_priority(snapshot)
    if fmt == "json":
        click.echo(json.dumps({"snapshot": snapshot, "priority": priority}))
    else:
        click.echo(f"{snapshot}: {priority}")


@priority_cmd.command("remove")
@click.argument("snapshot")
def priority_remove(snapshot: str) -> None:
    """Remove explicit priority from a snapshot (resets to default)."""
    remove_priority(snapshot)
    click.echo(f"Priority for '{snapshot}' removed (reset to default).")


@priority_cmd.command("list")
@click.option("--filter", "filter_priority", default=None,
              type=click.Choice(sorted(VALID_PRIORITIES)),
              help="Filter by a specific priority level.")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def priority_list(filter_priority: str, fmt: str) -> None:
    """List snapshots grouped by priority."""
    grouped = list_by_priority(filter_priority)
    if fmt == "json":
        click.echo(json.dumps(grouped))
    else:
        order = ["critical", "high", "normal", "low"]
        for level in order:
            if level not in grouped:
                continue
            snaps = grouped[level]
            if snaps:
                click.echo(f"[{level.upper()}]")
                for s in snaps:
                    click.echo(f"  {s}")
