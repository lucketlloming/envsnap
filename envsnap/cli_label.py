"""CLI commands for snapshot label management."""
from __future__ import annotations

import json

import click

from envsnap.label import (
    SnapshotNotFoundError,
    add_label,
    clear_labels,
    get_labels,
    remove_label,
    snapshots_with_label,
)


@click.group("label")
def label_cmd() -> None:
    """Manage labels attached to snapshots."""


@label_cmd.command("add")
@click.argument("snapshot")
@click.argument("label")
def label_add(snapshot: str, label: str) -> None:
    """Attach LABEL to SNAPSHOT."""
    try:
        add_label(snapshot, label)
        click.echo(f"Label '{label}' added to '{snapshot}'.")
    except SnapshotNotFoundError:
        click.echo(f"Error: snapshot '{snapshot}' not found.", err=True)
        raise SystemExit(1)


@label_cmd.command("remove")
@click.argument("snapshot")
@click.argument("label")
def label_remove(snapshot: str, label: str) -> None:
    """Detach LABEL from SNAPSHOT."""
    remove_label(snapshot, label)
    click.echo(f"Label '{label}' removed from '{snapshot}'.")


@label_cmd.command("list")
@click.argument("snapshot")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def label_list(snapshot: str, fmt: str) -> None:
    """List labels attached to SNAPSHOT."""
    labels = get_labels(snapshot)
    if fmt == "json":
        click.echo(json.dumps(labels))
    else:
        if labels:
            for lbl in labels:
                click.echo(lbl)
        else:
            click.echo(f"No labels for '{snapshot}'.")


@label_cmd.command("find")
@click.argument("label")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def label_find(label: str, fmt: str) -> None:
    """Find all snapshots carrying LABEL."""
    names = snapshots_with_label(label)
    if fmt == "json":
        click.echo(json.dumps(names))
    else:
        if names:
            for name in names:
                click.echo(name)
        else:
            click.echo(f"No snapshots with label '{label}'.")


@label_cmd.command("clear")
@click.argument("snapshot")
def label_clear(snapshot: str) -> None:
    """Remove all labels from SNAPSHOT."""
    clear_labels(snapshot)
    click.echo(f"All labels cleared from '{snapshot}'.")
