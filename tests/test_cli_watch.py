"""Tests for envsnap.cli_watch."""
from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from envsnap.cli_watch import watch_cmd


@pytest.fixture
def runner():
    return CliRunner()


def test_watch_start_exits_on_keyboard_interrupt(runner):
    with patch("envsnap.cli_watch.watch", side_effect=KeyboardInterrupt):
        result = runner.invoke(watch_cmd, ["start", "--interval", "1"])
    assert result.exit_code == 0
    assert "Watch stopped" in result.output


def test_watch_start_text_on_change(runner):
    sample_result = {"only_in_a": {}, "only_in_b": {"X": "1"}, "changed": {}, "common": {}}

    def fake_watch(interval, keys, on_change, max_iterations=None):
        on_change(sample_result)

    with patch("envsnap.cli_watch.watch", side_effect=fake_watch):
        result = runner.invoke(watch_cmd, ["start", "--interval", "1"])

    assert "change detected" in result.output


def test_watch_start_json_on_change(runner):
    sample_result = {"only_in_a": {}, "only_in_b": {"X": "1"}, "changed": {}, "common": {}}

    def fake_watch(interval, keys, on_change, max_iterations=None):
        on_change(sample_result)

    with patch("envsnap.cli_watch.watch", side_effect=fake_watch):
        result = runner.invoke(watch_cmd, ["start", "--format", "json"])

    assert "only_in_b" in result.output


def test_watch_start_specific_keys_message(runner):
    with patch("envsnap.cli_watch.watch", side_effect=KeyboardInterrupt):
        result = runner.invoke(watch_cmd, ["start", "--key", "FOO", "--key", "BAR"])
    assert "FOO" in result.output
    assert "BAR" in result.output
