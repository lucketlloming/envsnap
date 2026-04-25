"""Register mirror commands with the main CLI."""
from envsnap.cli_mirror import mirror_cmd


def register(cli):
    cli.add_command(mirror_cmd)
