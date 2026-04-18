"""Tests for envsnap.watch."""
from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from envsnap.watch import watch


def test_watch_no_change_no_callback(monkeypatch):
    monkeypatch.setenv("WATCH_VAR", "hello")
    calls = []

    with patch("envsnap.watch.time.sleep"):
        watch(
            interval=0,
            keys=["WATCH_VAR"],
            on_change=lambda r: calls.append(r),
            max_iterations=1,
        )

    assert calls == []


def test_watch_detects_addition(monkeypatch):
    monkeypatch.delenv("NEW_VAR", raising=False)
    calls = []
    iteration = 0

    def fake_sleep(_):
        nonlocal iteration
        if iteration == 0:
            monkeypatch.setenv("NEW_VAR", "added")
        iteration += 1

    with patch("envsnap.watch.time.sleep", side_effect=fake_sleep):
        watch(
            interval=0,
            keys=["NEW_VAR"],
            on_change=lambda r: calls.append(r),
            max_iterations=1,
        )

    assert len(calls) == 1
    assert "NEW_VAR" in calls[0]["only_in_b"]


def test_watch_detects_change(monkeypatch):
    monkeypatch.setenv("CHG_VAR", "before")
    calls = []
    iteration = 0

    def fake_sleep(_):
        nonlocal iteration
        if iteration == 0:
            monkeypatch.setenv("CHG_VAR", "after")
        iteration += 1

    with patch("envsnap.watch.time.sleep", side_effect=fake_sleep):
        watch(
            interval=0,
            keys=["CHG_VAR"],
            on_change=lambda r: calls.append(r),
            max_iterations=1,
        )

    assert len(calls) == 1
    assert "CHG_VAR" in calls[0]["changed"]


def test_watch_detects_removal(monkeypatch):
    monkeypatch.setenv("REM_VAR", "exists")
    calls = []
    iteration = 0

    def fake_sleep(_):
        nonlocal iteration
        if iteration == 0:
            monkeypatch.delenv("REM_VAR", raising=False)
        iteration += 1

    with patch("envsnap.watch.time.sleep", side_effect=fake_sleep):
        watch(
            interval=0,
            keys=["REM_VAR"],
            on_change=lambda r: calls.append(r),
            max_iterations=1,
        )

    assert len(calls) == 1
    assert "REM_VAR" in calls[0]["only_in_a"]
