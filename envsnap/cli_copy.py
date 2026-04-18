"""CLI commands for copying keys between snapshots."""

from __future__ import annotations

import click

from envsnap.copy import copy_keys, SnapshotNotFoundError


@click.group("copy")
def copy_cmd():
    """Copy env-var keys from one snapshot to another."""


@copy_cmd.command("run")
@click.argument("src")
@click.argument("dst")
@click.argument("keys", nargs=-1, required=True)
@click.option("--overwrite", is_flag=True, default=False,
              help="Overwrite existing keys in destination.")
def copy_run(src: str, dst: str, keys: tuple, overwrite: bool):
    """Copy KEYS from SRC snapshot into DST snapshot.

    Example:

        envsnap copy run prod staging FOO BAR
    """
    try:
        result = copy_keys(src, dst, list(keys), overwrite=overwrite)
    except SnapshotNotFoundError as exc:
        raise click.ClickException(str(exc))
    except KeyError as exc:
        raise click.ClickException(str(exc))

    click.echo(
        f"Copied {len(keys)} key(s) from '{src}' into '{dst}'. "
        f"Destination now has {len(result)} key(s)."
    )
