"""CLI commands for snapshot reports."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_report import build_report, build_all_reports, format_report
from envsnap.storage import load_snapshot


@click.group("report")
def report_cmd() -> None:
    """Generate snapshot reports."""


@report_cmd.command("show")
@click.argument("name")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def report_show(name: str, fmt: str) -> None:
    """Show a detailed report for NAME."""
    try:
        load_snapshot(name)  # fast existence check
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{name}' not found.")
    report = build_report(name)
    click.echo(format_report(report, fmt=fmt))


@report_cmd.command("all")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def report_all(fmt: str) -> None:
    """Show reports for all snapshots."""
    reports = build_all_reports()
    if not reports:
        click.echo("No snapshots found.")
        return
    if fmt == "json":
        payload = [
            {
                "name": r.name,
                "key_count": r.key_count,
                "tags": r.tags,
                "pinned": r.pinned,
                "locked": r.locked,
                "rating": r.rating,
                "note": r.note,
                "stats": r.stats,
            }
            for r in reports
        ]
        click.echo(json.dumps(payload, indent=2))
    else:
        separator = "-" * 40
        for r in reports:
            click.echo(format_report(r, fmt="text"))
            click.echo(separator)
