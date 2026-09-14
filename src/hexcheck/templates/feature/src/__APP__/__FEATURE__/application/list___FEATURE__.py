"""Caso de uso: listar __FEATURE__."""

from __future__ import annotations

from __APP__.__FEATURE__.domain.entities import __Entity__
from __APP__.__FEATURE__.domain.ports import __Entity__Repository


class List__Feature__:
    def __init__(self, repository: __Entity__Repository) -> None:
        self._repository = repository

    def __call__(self) -> list[__Entity__]:
        return self._repository.list_all()
