"""Tests for envsnap.cli_search."""
import pytest
from click.testing import CliRunner
from envsnap.cli_search import search_cmd

SNAPSHOTS = {
    "dev": {"DB_HOST": "localhost", "DEBUG": "true"},
    "prod": {"DB_HOST": "prod.example.com", "DEBUG": "false"},
}


@pytest.fixture(autouse=True)
def _patch(monkeypatch):
    monkeypatch.setattr("envsnap.search.list_snapshots", lambda: list(SNAPSHOTS))
    monkeypatch.setattr(
        "envsnap.search.load_snapshot",
        lambda name: SNAPSHOTS[name] if name in SNAPSHOTS else (_ for _ in ()).throw(FileNotFoundError(name))
    )


@pytest.fixture
def runner():
    return CliRunner()


def test_search_by_key(runner):
    result = runner.invoke(search_cmd, ["run", "--key", "DB_HOST"])
    assert result.exit_code == 0
    assert "[dev]" in result.output
    assert "DB_HOST=localhost" in result.output
    assert "[prod]" in result.output


def test_search_by_value(runner):
    result = runner.invoke(search_cmd, ["run", "--value", "*example.com"])
    assert result.exit_code == 0
    assert "[prod]" in result.output
    assert "[dev]" not in result.output


def test_search_json_output(runner):
    import json
    result = runner.invoke(search_cmd, ["run", "--key", "DEBUG", "--format", "json"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert "dev" in parsed
    assert parsed["dev"]["DEBUG"] == "true"


def test_search_no_patterns_errors(runner):
    result = runner.invoke(search_cmd, ["run"])
    assert result.exit_code != 0
    assert "at least" in result.output.lower()


def test_search_specific_snapshots(runner):
    result = runner.invoke(search_cmd, ["run", "--key", "DEBUG", "--snapshots", "dev"])
    assert result.exit_code == 0
    assert "[dev]" in result.output
    assert "[prod]" not in result.output


def test_search_no_match(runner):
    result = runner.invoke(search_cmd, ["run", "--key", "NONEXISTENT"])
    assert result.exit_code == 0
    assert "No matches found." in result.output
