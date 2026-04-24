"""CLI commands for the snapshot timeline feature."""

from __future__ import annotations

import click

from envsnap.snapshot_timeline import build_timeline, format_timeline
from envsnap.storage import SnapshotNotFoundError


@click.group("timeline")
def timeline_cmd():
    """View a chronological timeline of snapshot events."""


@timeline_cmd.command("show")
@click.argument("snapshot", required=False, default=None)
@click.option("--event", default=None, help="Filter by event type (snap, restore, delete, …).")
@click.option("--limit", default=None, type=int, help="Maximum number of entries to show.")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def timeline_show(snapshot, event, limit, fmt):
    """Show timeline of events, optionally scoped to SNAPSHOT."""
    try:
        entries = build_timeline(snapshot=snapshot, event_filter=event, limit=limit)
    except SnapshotNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(format_timeline(entries, fmt=fmt))


@timeline_cmd.command("events")
def timeline_events():
    """List known event types recorded in the timeline."""
    known = ["snap", "restore", "delete", "rename", "clone", "patch", "rollback"]
    for ev in known:
        click.echo(ev)
