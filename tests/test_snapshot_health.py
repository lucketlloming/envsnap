"""Tests for envsnap.snapshot_health."""
import pytest
from unittest.mock import patch, MagicMock

from envsnap.snapshot_health import check_health, check_all_health, format_health, HealthResult


def _lint_result(level, message):
    r = MagicMock()
    r.level = level
    r.message = message
    return r


def _val_result(level, message):
    r = MagicMock()
    r.level = level
    r.message = message
    return r


def _patch(load_data=None, lint=None, validate=None, locked=False, expiry=None):
    load_data = load_data or {"KEY": "val"}
    lint = lint or []
    validate = validate or []

    def _expiry_side_effect(name):
        from envsnap.expire import ExpiryNotFoundError
        if expiry is None:
            raise ExpiryNotFoundError(name)
        return expiry

    return [
        patch("envsnap.snapshot_health.load_snapshot", return_value=load_data),
        patch("envsnap.snapshot_health.lint_snapshot", return_value=lint),
        patch("envsnap.snapshot_health.validate_snapshot", return_value=validate),
        patch("envsnap.snapshot_health.is_locked", return_value=locked),
        patch("envsnap.snapshot_health.get_expiry", side_effect=_expiry_side_effect),
    ]


def test_healthy_snapshot():
    with _patch()[0], _patch()[1], _patch()[2], _patch()[3], _patch()[4]:
        patches = _patch()
        with patches[0], patches[1], patches[2], patches[3], patches[4]:
            result = check_health("mysnap")
    assert result.status == "healthy"
    assert result.score == 100
    assert result.issues == []


def test_warning_status_from_lint():
    lint = [_lint_result("warning", "empty value"), _lint_result("warning", "whitespace")]
    patches = _patch(lint=lint)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = check_health("mysnap")
    assert result.lint_warnings == 2
    assert result.score == 90
    assert result.status == "warning"
    assert len(result.issues) == 2


def test_critical_status_from_validation_errors():
    validate = [_val_result("error", "bad key") for _ in range(4)]
    patches = _patch(validate=validate)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = check_health("mysnap")
    assert result.validation_errors == 4
    assert result.score == 20
    assert result.status == "critical"


def test_expiry_date_populated():
    patches = _patch(expiry={"expires_at": "2025-12-31"})
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = check_health("mysnap")
    assert result.expiry_date == "2025-12-31"


def test_locked_flag():
    patches = _patch(locked=True)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = check_health("mysnap")
    assert result.is_locked is True


def test_as_dict_keys():
    patches = _patch()
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = check_health("mysnap")
    d = result.as_dict()
    for key in ("name", "key_count", "score", "status", "issues", "is_locked", "expiry_date"):
        assert key in d


def test_format_health_contains_fields():
    r = HealthResult(
        name="snap1", key_count=5, lint_warnings=1, lint_errors=0,
        validation_warnings=0, validation_errors=0, is_locked=False,
        expiry_date=None, score=95, status="healthy", issues=["[lint/warning] empty"]
    )
    text = format_health(r)
    assert "snap1" in text
    assert "HEALTHY" in text
    assert "95/100" in text
    assert "[lint/warning] empty" in text


def test_check_all_health():
    patches = _patch()
    with patch("envsnap.snapshot_health.list_snapshots", return_value=["a", "b"]):
        with patch("envsnap.snapshot_health.check_health") as mock_check:
            mock_check.side_effect = lambda n: HealthResult(
                name=n, key_count=1, lint_warnings=0, lint_errors=0,
                validation_warnings=0, validation_errors=0, is_locked=False,
                expiry_date=None, score=100, status="healthy"
            )
            results = check_all_health()
    assert len(results) == 2
    assert results[0].name == "a"
    assert results[1].name == "b"
