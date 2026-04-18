"""CLI commands for merging snapshots."""
from __future__ import annotations
import json
import click
from envsnap.merge import merge_snapshots, conflicts
from envsnap.storage import SnapshotNotFoundError


@click.group("merge")
def merge_cmd() -> None:
    """Merge two snapshots."""


@merge_cmd.command("run")
@click.argument("snapshot_a")
@click.argument("snapshot_b")
@click.argument("output")
@click.option(
    "--strategy",
    type=click.Choice(["union", "ours", "theirs"]),
    default="union",
    show_default=True,
    help="Conflict resolution strategy.",
)
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
def merge_run(snapshot_a: str, snapshot_b: str, output: str, strategy: str, fmt: str) -> None:
    """Merge SNAPSHOT_A and SNAPSHOT_B into OUTPUT."""
    try:
        result = merge_snapshots(snapshot_a, snapshot_b, output, strategy=strategy)
    except SnapshotNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    if fmt == "json":
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"Merged {snapshot_a!r} + {snapshot_b!r} → {output!r} ({len(result)} keys, strategy={strategy})")


@merge_cmd.command("conflicts")
@click.argument("snapshot_a")
@click.argument("snapshot_b")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
def merge_conflicts(snapshot_a: str, snapshot_b: str, fmt: str) -> None:
    """Show conflicting keys between two snapshots."""
    try:
        result = conflicts(snapshot_a, snapshot_b)
    except SnapshotNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    if fmt == "json":
        click.echo(json.dumps({k: {"a": v[0], "b": v[1]} for k, v in result.items()}, indent=2))
    else:
        if not result:
            click.echo("No conflicts.")
            return
        for key, (val_a, val_b) in result.items():
            click.echo(f"  {key}: {val_a!r} (a) vs {val_b!r} (b)")
