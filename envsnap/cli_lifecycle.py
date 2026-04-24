"""CLI commands for snapshot lifecycle management."""
import json
import click
from envsnap.snapshot_lifecycle import (
    set_state,
    transition,
    get_state,
    list_by_state,
    LifecycleError,
    SnapshotNotFoundError,
    VALID_STATES,
)


@click.group("lifecycle")
def lifecycle_cmd():
    """Manage snapshot lifecycle states."""


@lifecycle_cmd.command("set")
@click.argument("snapshot")
@click.argument("state", type=click.Choice(VALID_STATES))
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def lifecycle_set(snapshot, state, fmt):
    """Force-set the lifecycle state of a snapshot."""
    try:
        set_state(snapshot, state)
        if fmt == "json":
            click.echo(json.dumps({"snapshot": snapshot, "state": state}))
        else:
            click.echo(f"Snapshot '{snapshot}' state set to '{state}'.")
    except (LifecycleError, SnapshotNotFoundError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@lifecycle_cmd.command("transition")
@click.argument("snapshot")
@click.argument("new_state", type=click.Choice(VALID_STATES))
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def lifecycle_transition(snapshot, new_state, fmt):
    """Transition a snapshot to a new lifecycle state."""
    try:
        transition(snapshot, new_state)
        if fmt == "json":
            click.echo(json.dumps({"snapshot": snapshot, "new_state": new_state}))
        else:
            click.echo(f"Snapshot '{snapshot}' transitioned to '{new_state}'.")
    except (LifecycleError, SnapshotNotFoundError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@lifecycle_cmd.command("show")
@click.argument("snapshot")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def lifecycle_show(snapshot, fmt):
    """Show the current lifecycle state of a snapshot."""
    state = get_state(snapshot)
    if fmt == "json":
        click.echo(json.dumps({"snapshot": snapshot, "state": state}))
    else:
        click.echo(f"{snapshot}: {state}")


@lifecycle_cmd.command("list")
@click.argument("state", type=click.Choice(VALID_STATES))
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def lifecycle_list(state, fmt):
    """List all snapshots in a given lifecycle state."""
    snaps = list_by_state(state)
    if fmt == "json":
        click.echo(json.dumps({"state": state, "snapshots": snaps}))
    else:
        if not snaps:
            click.echo(f"No snapshots in state '{state}'.")
        else:
            for s in snaps:
                click.echo(s)
