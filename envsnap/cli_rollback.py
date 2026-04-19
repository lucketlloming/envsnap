"""CLI commands for snapshot rollback."""
import click

from envsnap.rollback import rollback_snapshot, get_rollback_points, RollbackError
from envsnap.history import get_history


@click.group("rollback")
def rollback_cmd():
    """Roll back snapshots to previous states."""


@rollback_cmd.command("run")
@click.argument("name")
@click.option("--steps", default=1, show_default=True, help="How many saves to go back.")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def rollback_run(name: str, steps: int, yes: bool):
    """Roll back NAME by STEPS save(s)."""
    if not yes:
        click.confirm(
            f"Roll back '{name}' by {steps} step(s)?  This overwrites the current snapshot.",
            abort=True,
        )
    try:
        data = rollback_snapshot(name, steps=steps)
    except RollbackError as exc:
        raise click.ClickException(str(exc))
    click.echo(f"Rolled back '{name}' ({len(data)} key(s) restored).")


@rollback_cmd.command("points")
@click.argument("name")
@click.option("--json", "as_json", is_flag=True)
def rollback_points(name: str, as_json: bool):
    """List rollback points available for NAME."""
    points = get_rollback_points(name)
    if as_json:
        import json
        click.echo(json.dumps(points, indent=2))
        return
    if not points:
        click.echo(f"No rollback points found for '{name}'.")
        return
    for i, pt in enumerate(reversed(points), 1):
        ts = pt.get("timestamp", "unknown")
        ev = pt.get("event", "?")
        keys = len(pt.get("data") or {})
        click.echo(f"  [{i}] {ts}  event={ev}  keys={keys}")
