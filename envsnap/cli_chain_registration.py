"""Register chain commands with the main CLI."""
from envsnap.cli_chain import chain_cmd


def register(cli):
    cli.add_command(chain_cmd)
