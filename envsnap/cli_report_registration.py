"""Register the report command group with the main CLI."""
from envsnap.cli_report import report_cmd


def register(cli) -> None:  # noqa: ANN001
    cli.add_command(report_cmd)
