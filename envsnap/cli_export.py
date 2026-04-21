"""CLI commands for export/import of snapshots."""

import click

from envsnap.export import export_snapshot, import_snapshot


def _detect_format(filename: str) -> str:
    """Detect export/import format from file extension."""
    return "json" if filename.endswith(".json") else "env"


@click.command("export")
@click.argument("name")
@click.argument("output")
@click.option(
    "--format", "fmt",
    type=click.Choice(["env", "json"], case_sensitive=False),
    default=None,
    help="Output format. Auto-detected from file extension if omitted.",
)
def export_cmd(name: str, output: str, fmt: str) -> None:
    """Export snapshot NAME to OUTPUT file."""
    if fmt is None:
        fmt = _detect_format(output)
    try:
        export_snapshot(name, output, fmt=fmt)
        click.echo(f"Exported '{name}' to {output} ({fmt})")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except ValueError as exc:
        raise click.ClickException(str(exc))


@click.command("import")
@click.argument("name")
@click.argument("input_file")
@click.option(
    "--format", "fmt",
    type=click.Choice(["env", "json"], case_sensitive=False),
    default=None,
    help="Input format. Auto-detected from file extension if omitted.",
)
def import_cmd(name: str, input_file: str, fmt: str) -> None:
    """Import snapshot NAME from INPUT_FILE."""
    if fmt is None:
        fmt = _detect_format(input_file)
    try:
        import_snapshot(name, input_file, fmt=fmt)
        click.echo(f"Imported '{name}' from {input_file}")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except ValueError as exc:
        raise click.ClickException(str(exc))
