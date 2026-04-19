"""CLI commands for snapshot locking."""
from __future__ import annotations

import json

import click

from envsnap.lock import (
    SnapshotLockedError,
    SnapshotNotFoundError,
    is_locked,
    list_locked,
    lock_snapshot,
    unlock_snapshot,
)


@click.group("lock")
def lock_cmd():
    """Lock or unlock snapshots to prevent modification."""


@lock_cmd.command("set")
@click.argument("name")
def lock_set(name: str):
    """Lock a snapshot."""
    try:
        lock_snapshot(name)
        click.echo(f"Snapshot '{name}' locked.")
    except SnapshotNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@lock_cmd.command("unset")
@click.argument("name")
def lock_unset(name: str):
    """Unlock a snapshot."""
    try:
        unlock_snapshot(name)
        click.echo(f"Snapshot '{name}' unlocked.")
    except SnapshotNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@lock_cmd.command("status")
@click.argument("name")
@click.option("--json", "as_json", is_flag=True)
def lock_status(name: str, as_json: bool):
    """Show lock status for a snapshot."""
    locked = is_locked(name)
    if as_json:
        click.echo(json.dumps({"name": name, "locked": locked}))
    else:
        state = "locked" if locked else "unlocked"
        click.echo(f"Snapshot '{name}' is {state}.")


@lock_cmd.command("list")
@click.option("--json", "as_json", is_flag=True)
def lock_list(as_json: bool):
    """List all locked snapshots."""
    names = list_locked()
    if as_json:
        click.echo(json.dumps(names))
    elif names:
        for n in names:
            click.echo(n)
    else:
        click.echo("No locked snapshots.")
