"""CLI commands for snapshot digest operations."""
from __future__ import annotations

import json
import sys

import click

from envsnap.snapshot_digest import (
    compute_digest,
    compare_digests,
    digest_all,
    verify_digest,
)
from envsnap.storage import load_snapshot  # noqa: F401 – side-effect import


@click.group("digest")
def digest_cmd() -> None:
    """Compute and verify snapshot digests."""


@digest_cmd.command("show")
@click.argument("name")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def digest_show(name: str, fmt: str) -> None:
    """Show the SHA-256 digest for a snapshot."""
    try:
        digest = compute_digest(name)
    except FileNotFoundError:
        click.echo(f"Snapshot '{name}' not found.", err=True)
        sys.exit(1)

    if fmt == "json":
        click.echo(json.dumps({"snapshot": name, "digest": digest}))
    else:
        click.echo(f"{name}: {digest}")


@digest_cmd.command("verify")
@click.argument("name")
@click.argument("expected")
def digest_verify(name: str, expected: str) -> None:
    """Verify a snapshot's digest against an expected value."""
    try:
        ok = verify_digest(name, expected)
    except FileNotFoundError:
        click.echo(f"Snapshot '{name}' not found.", err=True)
        sys.exit(1)

    if ok:
        click.echo(f"OK  {name}")
    else:
        click.echo(f"MISMATCH  {name}")
        sys.exit(1)


@digest_cmd.command("compare")
@click.argument("name_a")
@click.argument("name_b")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def digest_compare(name_a: str, name_b: str, fmt: str) -> None:
    """Compare digests of two snapshots."""
    try:
        result = compare_digests(name_a, name_b)
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)

    if fmt == "json":
        click.echo(json.dumps({"a": name_a, "b": name_b, **result}))
    else:
        match_label = "MATCH" if result["match"] else "DIFFER"
        click.echo(f"{name_a}: {result['a']}")
        click.echo(f"{name_b}: {result['b']}")
        click.echo(match_label)


@digest_cmd.command("all")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def digest_all_cmd(fmt: str) -> None:
    """Show digests for all snapshots."""
    digests = digest_all()
    if fmt == "json":
        click.echo(json.dumps(digests))
    else:
        if not digests:
            click.echo("No snapshots found.")
        for name, digest in sorted(digests.items()):
            click.echo(f"{name}: {digest}")
