"""CLI commands for snapshot quota management."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_quota import (
    QuotaNotFoundError,
    get_quota,
    list_quotas,
    remove_quota,
    set_quota,
)


@click.group("quota")
def quota_cmd() -> None:
    """Manage snapshot quotas."""


@quota_cmd.command("set")
@click.argument("scope")
@click.argument("max_snapshots", type=int)
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def quota_set(scope: str, max_snapshots: int, fmt: str) -> None:
    """Set the maximum number of snapshots for SCOPE."""
    try:
        set_quota(scope, max_snapshots)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    if fmt == "json":
        click.echo(json.dumps({"scope": scope, "max_snapshots": max_snapshots}))
    else:
        click.echo(f"Quota set: scope='{scope}', max_snapshots={max_snapshots}")


@quota_cmd.command("show")
@click.argument("scope")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def quota_show(scope: str, fmt: str) -> None:
    """Show quota for SCOPE."""
    quota = get_quota(scope)
    if quota is None:
        click.echo(f"No quota configured for scope '{scope}'.")
        return
    if fmt == "json":
        click.echo(json.dumps({"scope": scope, **quota}))
    else:
        click.echo(f"scope: {scope}")
        click.echo(f"max_snapshots: {quota['max_snapshots']}")


@quota_cmd.command("remove")
@click.argument("scope")
def quota_remove(scope: str) -> None:
    """Remove quota for SCOPE."""
    try:
        remove_quota(scope)
        click.echo(f"Quota removed for scope '{scope}'.")
    except QuotaNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@quota_cmd.command("list")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def quota_list(fmt: str) -> None:
    """List all configured quotas."""
    quotas = list_quotas()
    if fmt == "json":
        click.echo(json.dumps(quotas))
        return
    if not quotas:
        click.echo("No quotas configured.")
        return
    for scope, cfg in quotas.items():
        click.echo(f"{scope}: max_snapshots={cfg['max_snapshots']}")
