"""Register the risk command group with the main CLI."""
from envsnap.cli_risk import risk_cmd


def register(cli) -> None:  # type: ignore[type-arg]
    cli.add_command(risk_cmd)
