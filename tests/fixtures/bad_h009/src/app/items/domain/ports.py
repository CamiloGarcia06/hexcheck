from typing import Protocol

from .entities import Item


class ItemRepository(Protocol):
    def add(self, item: Item) -> None: ...
    def list_all(self) -> list[Item]: ...
