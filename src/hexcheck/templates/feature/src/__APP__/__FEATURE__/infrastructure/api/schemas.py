"""Esquemas HTTP de __FEATURE__ (pydantic vive aquí, no en el dominio)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from __APP__.__FEATURE__.domain.entities import __Entity__


class __Entity__In(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class __Entity__Out(BaseModel):
    id: int
    name: str

    @classmethod
    def from_entity(cls, __entity__: __Entity__) -> __Entity__Out:
        assert __entity__.id is not None
        return cls(id=int(__entity__.id), name=__entity__.name)
