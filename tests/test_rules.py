"""Un fixture por regla: el bueno pasa limpio, cada malo falla con su ID y nada más."""

from __future__ import annotations

import pytest

from tests.conftest import run_on


def rules_of(findings: list[tuple[str, str, int]]) -> set[str]:
    return {rule for rule, _, _ in findings}


def test_ok_project_is_clean() -> None:
    assert run_on("ok_project") == []


@pytest.mark.parametrize(
    ("fixture", "rule", "rel"),
    [
        ("bad_h001", "H001", "src/app/items/domain/entities.py"),
        ("bad_h002", "H002", "src/app/items/application/create_item.py"),
        ("bad_h003", "H003", "src/app/orders/infrastructure/db/repository.py"),
        ("bad_h004", "H004", "src/app/shared/errors.py"),
        ("bad_h005", "H005", "src/app/items/application/archive_item.py"),
        ("bad_h006", "H006", "src/app/items/infrastructure/api/router.py"),
        ("bad_h007", "H007", "src/app/items/infrastructure/api/router.py"),
        ("bad_h008", "H008", "src/app/items/infrastructure/db/repository.py"),
        ("bad_h009", "H009", "src/app/items/infrastructure/api/router.py"),
        ("bad_h010", "H010", "src/app/orders"),
    ],
)
def test_each_bad_fixture_fails_with_its_rule(fixture: str, rule: str, rel: str) -> None:
    findings = run_on(fixture)
    assert rules_of(findings) == {rule}, findings
    assert any(r == rel for _, r, _ in findings), findings


def test_w001_is_a_warning_and_a_clock_port_silences_it() -> None:
    findings = run_on("warn_w001")
    assert rules_of(findings) == {"W001"}
    assert run_on("ok_clock_port") == []


def test_allow_list_suppresses_one_rule_for_one_file() -> None:
    assert run_on("allow_h001") == []


def test_relative_imports_are_resolved() -> None:
    findings = run_on("bad_relative")
    assert rules_of(findings) == {"H001"}
