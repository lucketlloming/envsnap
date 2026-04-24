"""CLI commands for snapshot usage forecasting."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_forecast import forecast_all, forecast_snapshot, format_forecast
from envsnap.storage import list_snapshots


@click.group("forecast")
def forecast_cmd() -> None:
    """Forecast snapshot usage trends."""


@forecast_cmd.command("show")
@click.argument("name")
@click.option("--window", default=30, show_default=True, help="History window in days.")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def forecast_show(name: str, window: int, fmt: str) -> None:
    """Show forecast for a single snapshot."""
    from envsnap.storage import list_snapshots as _ls
    if name not in _ls():
        raise click.ClickException(f"Snapshot '{name}' not found.")
    result = forecast_snapshot(name, window_days=window)
    if fmt == "json":
        click.echo(json.dumps(result.as_dict(), indent=2))
    else:
        click.echo(format_forecast(result))


@forecast_cmd.command("all")
@click.option("--window", default=30, show_default=True, help="History window in days.")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def forecast_all_cmd(window: int, fmt: str) -> None:
    """Show forecasts for all snapshots."""
    names = list_snapshots()
    if not names:
        click.echo("No snapshots found.")
        return
    results = forecast_all(window_days=window)
    if fmt == "json":
        click.echo(json.dumps([r.as_dict() for r in results], indent=2))
    else:
        for r in results:
            click.echo(format_forecast(r))
            click.echo("")
