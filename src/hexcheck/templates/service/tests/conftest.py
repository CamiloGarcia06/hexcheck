"""Fixtures compartidas. `hexcheck add` inserta los fakes de cada funcionalidad aquí."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from __APP__.main import Deps, build_app
from __APP__.shared.config import Settings
from __APP__.shared.db import make_engine, make_session_factory

# hexcheck:fake-imports

ROOT = Path(__file__).resolve().parents[1]
TEST_TOKEN = "test-token"


def fake_deps(**overrides: object) -> Deps:
    kwargs: dict[str, object] = {
        "db_ping": lambda: True,
        # hexcheck:fakes
    }
    kwargs.update(overrides)
    return Deps(**kwargs)  # type: ignore[arg-type]


@pytest.fixture
def settings() -> Settings:
    return Settings(db_path=":memory:", token=TEST_TOKEN, version="test")


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(build_app(settings, deps=fake_deps())) as c:
        yield c


@pytest.fixture
def auth() -> dict[str, str]:
    return {"Authorization": f"Bearer {TEST_TOKEN}"}


@pytest.fixture
def engine(tmp_path: Path) -> Engine:
    """SQLite real con las migraciones de Alembic aplicadas (así se prueban también)."""
    db_path = tmp_path / "test.db"
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "migrations"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(cfg, "head")
    return make_engine(str(db_path))


@pytest.fixture
def sessions(engine: Engine) -> sessionmaker[Session]:
    return make_session_factory(engine)
