"""Puertos de __FEATURE__: lo que el dominio necesita de fuera, como Protocol."""

from __future__ import annotations

from typing import Protocol

from __APP__.shared.types import EntityId

from .entities import __Entity__


class __Entity__Repository(Protocol):
    def add(self, __entity__: __Entity__) -> __Entity__:
        """Persiste y devuelve la entidad con id asignado."""
        ...

    def get(self, __entity___id: EntityId) -> __Entity__:
        """Lanza __Entity__NotFound si no existe."""
        ...

    def list_all(self) -> list[__Entity__]: ...
