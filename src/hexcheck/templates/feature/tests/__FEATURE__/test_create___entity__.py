import pytest

from __APP__.__FEATURE__.application.create___entity__ import Create__Entity__
from __APP__.__FEATURE__.domain.errors import Empty__Entity__Name

from .fakes import InMemory__Entity__Repository


def test_create_assigns_id_and_stores() -> None:
    repo = InMemory__Entity__Repository()
    created = Create__Entity__(repo)("  primera  ")
    assert created.id is not None
    assert created.name == "primera"
    assert repo.list_all() == [created]


def test_create_rejects_empty_name() -> None:
    with pytest.raises(Empty__Entity__Name):
        Create__Entity__(InMemory__Entity__Repository())("   ")
