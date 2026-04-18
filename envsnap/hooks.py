"""Lifecycle hooks that record history events on snapshot operations."""

from envsnap.history import record_event


def on_snap(snapshot_name: str) -> None:
    """Called after a snapshot is created."""
    record_event(snapshot_name, "create")


def on_restore(snapshot_name: str) -> None:
    """Called after a snapshot is restored."""
    record_event(snapshot_name, "restore")


def on_delete(snapshot_name: str) -> None:
    """Called after a snapshot is deleted."""
    record_event(snapshot_name, "delete")
