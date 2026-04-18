"""Template support: save/load snapshot templates with placeholder values."""
from __future__ import annotations
import json
from pathlib import Path
from envsnap.storage import get_snapshot_dir

_TEMPLATES_FILE = "templates.json"


def _templates_path() -> Path:
    return get_snapshot_dir() / _TEMPLATES_FILE


def _load_templates() -> dict:
    p = _templates_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_templates(data: dict) -> None:
    _templates_path().write_text(json.dumps(data, indent=2))


def save_template(name: str, keys: list[str], defaults: dict[str, str] | None = None) -> None:
    """Save a template with a list of expected keys and optional default values."""
    data = _load_templates()
    data[name] = {"keys": keys, "defaults": defaults or {}}
    _save_templates(data)


def get_template(name: str) -> dict:
    data = _load_templates()
    if name not in data:
        raise KeyError(f"Template '{name}' not found.")
    return data[name]


def list_templates() -> list[str]:
    return list(_load_templates().keys())


def delete_template(name: str) -> None:
    data = _load_templates()
    if name not in data:
        raise KeyError(f"Template '{name}' not found.")
    del data[name]
    _save_templates(data)


def apply_template(name: str, overrides: dict[str, str] | None = None) -> dict[str, str]:
    """Return an env dict from template defaults merged with overrides."""
    tmpl = get_template(name)
    result = dict(tmpl["defaults"])
    if overrides:
        result.update(overrides)
    return {k: result.get(k, "") for k in tmpl["keys"]}
