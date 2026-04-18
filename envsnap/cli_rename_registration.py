"""Register rename commands with the main CLI."""
from envsnap.cli_rename import rename_cmd


def register(cli):
    """Attach rename_cmd to the root CLI group."""
    cli.add_command(rename_cmd)
