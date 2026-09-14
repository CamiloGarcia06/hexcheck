from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.items.domain.entities import Item

from .models import ItemRow


class SqlItemRepository:
    def __init__(self, sessions: sessionmaker) -> None:
        self._sessions = sessions

    def add(self, item: Item) -> None:
        with self._sessions() as s:
            s.add(ItemRow(id=item.id, name=item.name))
            s.commit()

    def list_all(self) -> list[Item]:
        with self._sessions() as s:
            return [Item(id=r.id, name=r.name) for r in s.scalars(select(ItemRow))]
