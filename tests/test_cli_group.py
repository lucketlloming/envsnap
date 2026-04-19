import pytest
from click.testing import CliRunner
from envsnap.cli_group import group_cmd
from unittest.mock import patch


@pytest.fixture
def runner():
    return CliRunner()


def _patch(members=None, groups=None):
    members = members or ["snap1", "snap2"]
    groups = groups or ["g1", "g2"]
    return {
        "add": patch("envsnap.cli_group.add_to_group"),
        "remove": patch("envsnap.cli_group.remove_from_group"),
        "get": patch("envsnap.cli_group.get_group", return_value=members),
        "list": patch("envsnap.cli_group.list_groups", return_value=groups),
        "delete": patch("envsnap.cli_group.delete_group"),
    }


def test_group_add(runner):
    with patch("envsnap.cli_group.add_to_group") as m:
        result = runner.invoke(group_cmd, ["add", "mygroup", "snap1"])
        assert result.exit_code == 0
        assert "Added" in result.output
        m.assert_called_once_with("mygroup", "snap1")


def test_group_add_missing_snapshot(runner):
    with patch("envsnap.cli_group.add_to_group", side_effect=KeyError("Snapshot 'x' does not exist.")):
        result = runner.invoke(group_cmd, ["add", "mygroup", "x"])
        assert result.exit_code == 1


def test_group_show_text(runner):
    with patch("envsnap.cli_group.get_group", return_value=["snap1", "snap2"]):
        result = runner.invoke(group_cmd, ["show", "mygroup"])
        assert "snap1" in result.output
        assert "snap2" in result.output


def test_group_show_json(runner):
    with patch("envsnap.cli_group.get_group", return_value=["snap1"]):
        result = runner.invoke(group_cmd, ["show", "mygroup", "--json"])
        import json
        data = json.loads(result.output)
        assert data["mygroup"] == ["snap1"]


def test_group_list(runner):
    with patch("envsnap.cli_group.list_groups", return_value=["g1", "g2"]):
        result = runner.invoke(group_cmd, ["list"])
        assert "g1" in result.output
        assert "g2" in result.output


def test_group_delete(runner):
    with patch("envsnap.cli_group.delete_group") as m:
        result = runner.invoke(group_cmd, ["delete", "mygroup"])
        assert result.exit_code == 0
        assert "Deleted" in result.output
        m.assert_called_once_with("mygroup")
