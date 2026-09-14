import fastapi
from dataclasses import dataclass

from app.shared.errors import DomainError
from app.shared.types import ItemId


class EmptyName(DomainError):
    code = 'empty_name'


@dataclass(frozen=True)
class Item:
    id: ItemId
    name: str

    def __post_init__(self) -> None:
        if not self.name:
            raise EmptyName()
