"""Register watch commands with the main CLI."""
from __future__ import annotations

from envsnap.cli_watch import watch_cmd


def register(cli):
    """Attach watch_cmd group to the root CLI."""
    cli.add_command(watch_cmd)
