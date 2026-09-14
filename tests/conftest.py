"""Fixtures: mini-servicios en tests/fixtures/<caso>/ que deben pasar o fallar."""

from __future__ import annotations

from pathlib import Path

import pytest

from hexcheck.config import load_config
from hexcheck.model import load_service
from hexcheck.rules import run_rules

FIXTURES = Path(__file__).parent / "fixtures"


def run_on(fixture: str) -> list[tuple[str, str, int]]:
    cfg = load_config(FIXTURES / fixture)
    svc, errors = load_service(cfg)
    return [(f.rule, f.rel, f.lineno) for f in run_rules(svc, errors)]


@pytest.fixture
def fixtures() -> Path:
    return FIXTURES
