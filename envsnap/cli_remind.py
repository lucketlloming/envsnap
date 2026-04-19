"""CLI commands for snapshot reminders."""
import json
import click
from envsnap.remind import (
    set_reminder, get_reminder, remove_reminder,
    list_reminders, due_reminders,
    ReminderNotFoundError, SnapshotNotFoundError,
)


@click.group("remind")
def remind_cmd():
    """Manage reminders attached to snapshots."""


@remind_cmd.command("set")
@click.argument("snapshot")
@click.argument("message")
@click.option("--due", default=None, help="Due date (YYYY-MM-DD)")
def remind_set(snapshot, message, due):
    """Attach a reminder to SNAPSHOT."""
    try:
        set_reminder(snapshot, message, due)
        click.echo(f"Reminder set for '{snapshot}'.")
    except SnapshotNotFoundError:
        click.echo(f"Snapshot '{snapshot}' not found.", err=True)
        raise SystemExit(1)
    except ValueError as e:
        click.echo(f"Invalid date: {e}", err=True)
        raise SystemExit(1)


@remind_cmd.command("show")
@click.argument("snapshot")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def remind_show(snapshot, fmt):
    """Show reminder for SNAPSHOT."""
    try:
        r = get_reminder(snapshot)
    except ReminderNotFoundError:
        click.echo(f"No reminder for '{snapshot}'.", err=True)
        raise SystemExit(1)
    if fmt == "json":
        click.echo(json.dumps({snapshot: r}, indent=2))
    else:
        due = r["due"] or "(none)"
        click.echo(f"{snapshot}: {r['message']}  [due: {due}]")


@remind_cmd.command("remove")
@click.argument("snapshot")
def remind_remove(snapshot):
    """Remove reminder from SNAPSHOT."""
    try:
        remove_reminder(snapshot)
        click.echo(f"Reminder removed from '{snapshot}'.")
    except ReminderNotFoundError:
        click.echo(f"No reminder for '{snapshot}'.", err=True)
        raise SystemExit(1)


@remind_cmd.command("list")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def remind_list(fmt):
    """List all reminders."""
    data = list_reminders()
    if fmt == "json":
        click.echo(json.dumps(data, indent=2))
    else:
        if not data:
            click.echo("No reminders.")
        for snap, info in data.items():
            due = info["due"] or "(none)"
            click.echo(f"{snap}: {info['message']}  [due: {due}]")


@remind_cmd.command("due")
@click.option("--as-of", default=None, help="Check due as of date (YYYY-MM-DD)")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def remind_due(as_of, fmt):
    """Show reminders that are due."""
    data = due_reminders(as_of)
    if fmt == "json":
        click.echo(json.dumps(data, indent=2))
    else:
        if not data:
            click.echo("No due reminders.")
        for snap, info in data.items():
            click.echo(f"{snap}: {info['message']}  [due: {info['due']}]")
