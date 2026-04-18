"""CLI commands for renaming snapshots."""
import click
from envsnap.rename import rename_snapshot, SnapshotNotFoundError, SnapshotAlreadyExistsError


@click.group("rename")
def rename_cmd():
    """Rename a snapshot."""


@rename_cmd.command("run")
@click.argument("old_name")
@click.argument("new_name")
def rename_run(old_name: str, new_name: str):
    """Rename OLD_NAME to NEW_NAME, updating all cross-references."""
    try:
        rename_snapshot(old_name, new_name)
        click.echo(f"Renamed '{old_name}' -> '{new_name}'.")
    except SnapshotNotFoundError as exc:
        raise click.ClickException(str(exc))
    except SnapshotAlreadyExistsError as exc:
        raise click.ClickException(str(exc))
