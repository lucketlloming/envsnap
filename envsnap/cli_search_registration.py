"""Register search commands with the main CLI.

Import and call `register(cli)` from the main cli.py entrypoint.
"""
from __future__ import annotations
import click
from envsnap.cli_search import search_cmd


def register(cli: click.Group) -> None:
    """Attach the search command group to the root CLI group."""
    cli.add_command(search_cmd)
