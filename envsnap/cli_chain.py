"""CLI commands for snapshot chains."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_chain import (
    ChainError,
    SnapshotNotFoundError,
    append_to_chain,
    create_chain,
    delete_chain,
    get_chain,
    list_chains,
)


@click.group("chain")
def chain_cmd():
    """Manage snapshot chains."""


@chain_cmd.command("create")
@click.argument("chain_name")
@click.argument("snapshots", nargs=-1, required=True)
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def chain_create(chain_name, snapshots, fmt):
    """Create a named chain from an ordered list of snapshots."""
    try:
        create_chain(chain_name, list(snapshots))
    except SnapshotNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    if fmt == "json":
        click.echo(json.dumps({"chain": chain_name, "snapshots": list(snapshots)}))
    else:
        click.echo(f"Chain '{chain_name}' created with {len(snapshots)} snapshot(s).")


@chain_cmd.command("show")
@click.argument("chain_name")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def chain_show(chain_name, fmt):
    """Show snapshots in a chain."""
    try:
        snaps = get_chain(chain_name)
    except ChainError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    if fmt == "json":
        click.echo(json.dumps({"chain": chain_name, "snapshots": snaps}))
    else:
        click.echo(f"Chain: {chain_name}")
        for i, s in enumerate(snaps, 1):
            click.echo(f"  {i}. {s}")


@chain_cmd.command("list")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def chain_list(fmt):
    """List all chains."""
    names = list_chains()
    if fmt == "json":
        click.echo(json.dumps({"chains": names}))
    else:
        if not names:
            click.echo("No chains defined.")
        else:
            for n in names:
                click.echo(n)


@chain_cmd.command("append")
@click.argument("chain_name")
@click.argument("snapshot_name")
def chain_append(chain_name, snapshot_name):
    """Append a snapshot to an existing chain."""
    try:
        append_to_chain(chain_name, snapshot_name)
        click.echo(f"Appended '{snapshot_name}' to chain '{chain_name}'.")
    except (ChainError, SnapshotNotFoundError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@chain_cmd.command("delete")
@click.argument("chain_name")
def chain_delete(chain_name):
    """Delete a chain."""
    try:
        delete_chain(chain_name)
        click.echo(f"Chain '{chain_name}' deleted.")
    except ChainError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
