"""Test de contrato: la misma suite contra el fake y contra SQLite con migraciones."""

from collections.abc import Callable

import pytest
from sqlalchemy.orm import Session, sessionmaker

from __APP__.__FEATURE__.domain.entities import __Entity__
from __APP__.__FEATURE__.domain.errors import __Entity__NotFound
from __APP__.__FEATURE__.domain.ports import __Entity__Repository
from __APP__.__FEATURE__.infrastructure.db.repository import Sql__Entity__Repository
from __APP__.shared.types import EntityId

from .fakes import InMemory__Entity__Repository

Factory = Callable[[], __Entity__Repository]


@pytest.fixture(params=["fake", "sql"])
def repository(request: pytest.FixtureRequest, sessions: sessionmaker[Session]) -> __Entity__Repository:
    if request.param == "fake":
        return InMemory__Entity__Repository()
    return Sql__Entity__Repository(sessions)


def test_add_assigns_incrementing_ids(repository: __Entity__Repository) -> None:
    a = repository.add(__Entity__(name="a"))
    b = repository.add(__Entity__(name="b"))
    assert a.id is not None and b.id is not None
    assert b.id > a.id


def test_get_returns_stored_and_raises_when_missing(repository: __Entity__Repository) -> None:
    stored = repository.add(__Entity__(name="x"))
    assert stored.id is not None
    assert repository.get(stored.id) == stored
    with pytest.raises(__Entity__NotFound):
        repository.get(EntityId(9999))


def test_list_all_in_id_order(repository: __Entity__Repository) -> None:
    names = ["c", "a", "b"]
    for n in names:
        repository.add(__Entity__(name=n))
    assert [e.name for e in repository.list_all()] == names
