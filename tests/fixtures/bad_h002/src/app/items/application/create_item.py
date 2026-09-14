from app.items.infrastructure.db.repository import SqlItemRepository
from app.items.domain.entities import Item
from app.items.domain.ports import ItemRepository
from app.orders.domain.entities import Order


class CreateItem:
    def __init__(self, repo: ItemRepository) -> None:
        self._repo = repo

    def __call__(self, name: str, order: Order | None = None) -> Item:
        item = Item(id=len(self._repo.list_all()) + 1, name=name)
        self._repo.add(item)
        return item
