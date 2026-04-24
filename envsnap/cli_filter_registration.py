"""Register the filter command group."""
from envsnap.cli_filter import filter_cmd


def register(cli) -> None:  # type: ignore[type-arg]
    cli.add_command(filter_cmd)
