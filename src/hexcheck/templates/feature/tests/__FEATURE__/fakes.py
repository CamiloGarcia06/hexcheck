"""Fakes de los puertos de __FEATURE__: listas en memoria, sin mocks."""

from __future__ import annotations

from __APP__.__FEATURE__.domain.entities import __Entity__
from __APP__.__FEATURE__.domain.errors import __Entity__NotFound
from __APP__.shared.types import EntityId


class InMemory__Entity__Repository:
    def __init__(self) -> None:
        self.items: dict[int, __Entity__] = {}

    def add(self, __entity__: __Entity__) -> __Entity__:
        new_id = EntityId(max(self.items, default=0) + 1)
        stored = __entity__.with_id(new_id)
        self.items[int(new_id)] = stored
        return stored

    def get(self, __entity___id: EntityId) -> __Entity__:
        try:
            return self.items[int(__entity___id)]
        except KeyError:
            raise __Entity__NotFound(f"__entity__ {__entity___id}") from None

    def list_all(self) -> list[__Entity__]:
        return list(self.items.values())
