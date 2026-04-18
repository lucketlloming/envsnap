"""Wire audit logging into envsnap hooks so actions are recorded automatically."""
from envsnap.hooks import on_snap, on_restore, on_delete
from envsnap.audit import record_audit


def _handle_snap(name: str, **kwargs) -> None:
    record_audit("snap", name, detail=kwargs.get("detail"))


def _handle_restore(name: str, **kwargs) -> None:
    record_audit("restore", name, detail=kwargs.get("detail"))


def _handle_delete(name: str, **kwargs) -> None:
    record_audit("delete", name, detail=kwargs.get("detail"))


def register_audit_hooks() -> None:
    """Register audit handlers for snap, restore, and delete events."""
    on_snap(_handle_snap)
    on_restore(_handle_restore)
    on_delete(_handle_delete)
