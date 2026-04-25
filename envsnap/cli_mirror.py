"""CLI commands for snapshot mirroring."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_mirror import MirrorError, push_snapshot, pull_snapshot, sync_status


@click.group("mirror")
def mirror_cmd():
    """Push, pull, and sync snapshots with a remote directory."""


@mirror_cmd.command("push")
@click.argument("name")
@click.argument("remote_dir")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing remote snapshot.")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def mirror_push(name: str, remote_dir: str, overwrite: bool, fmt: str):
    """Push a local snapshot to REMOTE_DIR."""
    try:
        dest = push_snapshot(name, remote_dir, overwrite=overwrite)
        if fmt == "json":
            click.echo(json.dumps({"pushed": name, "dest": str(dest)}))
        else:
            click.echo(f"Pushed '{name}' -> {dest}")
    except MirrorError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@mirror_cmd.command("pull")
@click.argument("name")
@click.argument("remote_dir")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing local snapshot.")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def mirror_pull(name: str, remote_dir: str, overwrite: bool, fmt: str):
    """Pull a snapshot from REMOTE_DIR to local storage."""
    try:
        dest = pull_snapshot(name, remote_dir, overwrite=overwrite)
        if fmt == "json":
            click.echo(json.dumps({"pulled": name, "dest": str(dest)}))
        else:
            click.echo(f"Pulled '{name}' -> {dest}")
    except MirrorError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@mirror_cmd.command("status")
@click.argument("remote_dir")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def mirror_status(remote_dir: str, fmt: str):
    """Show sync status between local and REMOTE_DIR."""
    results = sync_status(remote_dir)
    if fmt == "json":
        click.echo(json.dumps([{"name": n, "status": s} for n, s in results]))
    else:
        if not results:
            click.echo("No snapshots found.")
            return
        for name, status in results:
            click.echo(f"  {name:<30} {status}")
