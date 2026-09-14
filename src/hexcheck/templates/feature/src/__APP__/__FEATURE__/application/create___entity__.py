"""Caso de uso: crear un __entity__. Un archivo, una clase, `__call__`."""

from __future__ import annotations

from __APP__.__FEATURE__.domain.entities import __Entity__
from __APP__.__FEATURE__.domain.ports import __Entity__Repository


class Create__Entity__:
    def __init__(self, repository: __Entity__Repository) -> None:
        self._repository = repository

    def __call__(self, name: str) -> __Entity__:
        return self._repository.add(__Entity__(name=name.strip()))
