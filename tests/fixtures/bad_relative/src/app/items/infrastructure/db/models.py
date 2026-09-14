from sqlalchemy.orm import Mapped, mapped_column

from app.shared.db import Base


class ItemRow(Base):
    __tablename__ = 'items'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
