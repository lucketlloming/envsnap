"""Lifecycle hooks called on core envsnap events."""

from __future__ import annotations

from typing import Callable, Dict, List

_hooks: Dict[str, List[Callable[..., None]]] = {
    "snap": [],
    "restore": [],
    "delete": [],
    "profile_add": [],
    "profile_delete": [],
}


def _register(event: str, fn: Callable[..., None]) -> None:
    if event not in _hooks:
        raise ValueError(f"Unknown event: {event}")
    _hooks[event].append(fn)


def _fire(event: str, **kwargs) -> None:
    for fn in _hooks.get(event, []):
        fn(**kwargs)


def on_snap(fn: Callable[..., None]) -> Callable[..., None]:
    _register("snap", fn)
    return fn


def on_restore(fn: Callable[..., None]) -> Callable[..., None]:
    _register("restore", fn)
    return fn


def on_delete(fn: Callable[..., None]) -> Callable[..., None]:
    _register("delete", fn)
    return fn


def on_profile_add(fn: Callable[..., None]) -> Callable[..., None]:
    _register("profile_add", fn)
    return fn


def on_profile_delete(fn: Callable[..., None]) -> Callable[..., None]:
    _register("profile_delete", fn)
    return fn
