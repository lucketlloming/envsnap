import pytest
from pathlib import Path
from unittest.mock import patch
import envsnap.template as tpl


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path):
    with patch("envsnap.template.get_snapshot_dir", return_value=tmp_path):
        yield tmp_path


def test_save_and_list_template():
    tpl.save_template("base", ["FOO", "BAR"])
    assert "base" in tpl.list_templates()


def test_get_template_returns_data():
    tpl.save_template("myenv", ["HOST", "PORT"], {"PORT": "8080"})
    t = tpl.get_template("myenv")
    assert t["keys"] == ["HOST", "PORT"]
    assert t["defaults"]["PORT"] == "8080"


def test_get_template_missing_raises():
    with pytest.raises(KeyError, match="not found"):
        tpl.get_template("ghost")


def test_delete_template():
    tpl.save_template("tmp", ["X"])
    tpl.delete_template("tmp")
    assert "tmp" not in tpl.list_templates()


def test_delete_missing_raises():
    with pytest.raises(KeyError):
        tpl.delete_template("nope")


def test_apply_template_defaults():
    tpl.save_template("t", ["A", "B"], {"A": "hello", "B": "world"})
    result = tpl.apply_template("t")
    assert result == {"A": "hello", "B": "world"}


def test_apply_template_with_overrides():
    tpl.save_template("t2", ["A", "B"], {"A": "default"})
    result = tpl.apply_template("t2", {"A": "override", "B": "new"})
    assert result["A"] == "override"
    assert result["B"] == "new"


def test_apply_template_missing_key_empty_string():
    tpl.save_template("t3", ["X", "Y"])
    result = tpl.apply_template("t3")
    assert result["X"] == ""
    assert result["Y"] == ""
