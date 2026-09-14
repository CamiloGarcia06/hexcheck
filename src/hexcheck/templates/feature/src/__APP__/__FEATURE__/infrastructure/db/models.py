"""Tablas de __FEATURE__. Se mapean a mano a las entidades del dominio."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from __APP__.shared.db import Base


class __Entity__Row(Base):
    __tablename__ = "__FEATURE__"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
