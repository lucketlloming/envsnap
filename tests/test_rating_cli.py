import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envsnap.rating_cli import rating_cmd
from envsnap.rating import InvalidRatingError, SnapshotNotFoundError


@pytest.fixture
def runner():
    return CliRunner()


def _patch(get=None, set_side=None, remove_side=None, list_ret=None):
    patches = {
        "envsnap.rating_cli.set_rating": MagicMock(side_effect=set_side),
        "envsnap.rating_cli.get_rating": MagicMock(return_value=get),
        "envsnap.rating_cli.remove_rating": MagicMock(side_effect=remove_side),
        "envsnap.rating_cli.list_ratings": MagicMock(return_value=list_ret or {}),
    }
    return patches


def test_rating_set_success(runner):
    with patch("envsnap.rating_cli.set_rating") as mock_set:
        result = runner.invoke(rating_cmd, ["set", "mysnap", "4"])
    assert result.exit_code == 0
    assert "Rated 'mysnap': 4/5" in result.output


def test_rating_set_with_note(runner):
    with patch("envsnap.rating_cli.set_rating") as mock_set:
        result = runner.invoke(rating_cmd, ["set", "mysnap", "5", "--note", "excellent"])
    assert result.exit_code == 0
    assert "excellent" in result.output


def test_rating_set_invalid_score(runner):
    with patch("envsnap.rating_cli.set_rating", side_effect=InvalidRatingError("out of range")):
        result = runner.invoke(rating_cmd, ["set", "mysnap", "9"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_rating_set_missing_snapshot(runner):
    with patch("envsnap.rating_cli.set_rating", side_effect=SnapshotNotFoundError("mysnap")):
        result = runner.invoke(rating_cmd, ["set", "ghost", "3"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_rating_show_text(runner):
    entry = {"score": 3, "note": "decent", "timestamp": "2024-01-01T00:00:00"}
    with patch("envsnap.rating_cli.get_rating", return_value=entry):
        result = runner.invoke(rating_cmd, ["show", "mysnap"])
    assert "3/5" in result.output
    assert "decent" in result.output


def test_rating_show_json(runner):
    entry = {"score": 5, "note": None, "timestamp": "2024-01-01T00:00:00"}
    with patch("envsnap.rating_cli.get_rating", return_value=entry):
        result = runner.invoke(rating_cmd, ["show", "mysnap", "--format", "json"])
    data = json.loads(result.output)
    assert data["score"] == 5
    assert data["snapshot"] == "mysnap"


def test_rating_show_none(runner):
    with patch("envsnap.rating_cli.get_rating", return_value=None):
        result = runner.invoke(rating_cmd, ["show", "unrated"])
    assert "No rating" in result.output


def test_rating_remove_success(runner):
    with patch("envsnap.rating_cli.remove_rating"):
        result = runner.invoke(rating_cmd, ["remove", "mysnap"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_rating_list_text(runner):
    ratings = {
        "snap1": {"score": 4, "note": "good", "timestamp": "2024-01-01T00:00:00"},
        "snap2": {"score": 2, "note": None, "timestamp": "2024-01-02T00:00:00"},
    }
    with patch("envsnap.rating_cli.list_ratings", return_value=ratings):
        result = runner.invoke(rating_cmd, ["list"])
    assert "snap1" in result.output
    assert "4/5" in result.output
    assert "snap2" in result.output


def test_rating_list_empty(runner):
    with patch("envsnap.rating_cli.list_ratings", return_value={}):
        result = runner.invoke(rating_cmd, ["list"])
    assert "No ratings" in result.output
