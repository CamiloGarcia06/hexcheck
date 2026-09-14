"""Entidades de __FEATURE__: datos + reglas puras. Sin IO, sin framework."""

from __future__ import annotations

from dataclasses import dataclass, replace

from __APP__.shared.types import EntityId

from .errors import Empty__Entity__Name


@dataclass(frozen=True)
class __Entity__:
    name: str
    id: EntityId | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise Empty__Entity__Name()

    def with_id(self, new_id: EntityId) -> __Entity__:
        return replace(self, id=new_id)
