"""CLI commands for snapshot annotations."""
from __future__ import annotations

import json
import click

from envsnap import annotate


@click.group("annotate")
def annotate_cmd():
    """Manage snapshot annotations (arbitrary metadata)."""


@annotate_cmd.command("set")
@click.argument("snapshot")
@click.argument("key")
@click.argument("value")
def annotate_set(snapshot: str, key: str, value: str):
    """Set an annotation KEY=VALUE on SNAPSHOT."""
    try:
        annotate.set_annotation(snapshot, key, value)
        click.echo(f"Annotation '{key}' set on '{snapshot}'.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@annotate_cmd.command("get")
@click.argument("snapshot")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def annotate_get(snapshot: str, fmt: str):
    """Show all annotations for SNAPSHOT."""
    data = annotate.get_annotations(snapshot)
    if fmt == "json":
        click.echo(json.dumps(data, indent=2))
    else:
        if not data:
            click.echo(f"No annotations for '{snapshot}'.")
        else:
            for k, v in data.items():
                click.echo(f"  {k}: {v}")


@annotate_cmd.command("remove")
@click.argument("snapshot")
@click.argument("key")
def annotate_remove(snapshot: str, key: str):
    """Remove annotation KEY from SNAPSHOT."""
    annotate.remove_annotation(snapshot, key)
    click.echo(f"Annotation '{key}' removed from '{snapshot}'.")


@annotate_cmd.command("clear")
@click.argument("snapshot")
def annotate_clear(snapshot: str):
    """Clear all annotations from SNAPSHOT."""
    annotate.clear_annotations(snapshot)
    click.echo(f"All annotations cleared from '{snapshot}'.")


@annotate_cmd.command("list")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def annotate_list(fmt: str):
    """List all annotations across all snapshots."""
    data = annotate.all_annotations()
    if fmt == "json":
        click.echo(json.dumps(data, indent=2))
    else:
        if not data:
            click.echo("No annotations found.")
        else:
            for snap, kvs in data.items():
                for k, v in kvs.items():
                    click.echo(f"  {snap}  {k}: {v}")
