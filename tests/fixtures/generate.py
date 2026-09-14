# ruff: noqa: E501
"""Genera los mini-servicios de tests/fixtures. Ejecutar: uv run python tests/fixtures/generate.py

Los fixtures se versionan; este script existe para regenerarlos con un cambio de una línea.
"""

from __future__ import annotations

import shutil
from pathlib import Path

HERE = Path(__file__).parent

PYPROJECT = '[project]\nname = "app"\nversion = "0"\n\n[tool.hexcheck]\nsrc = "src/app"\n{extra}'

OK: dict[str, str] = {
    "src/app/__init__.py": "",
    "src/app/main.py": (
        "from fastapi import FastAPI\n\n"
        "from app.items.application.create_item import CreateItem\n"
        "from app.items.infrastructure.api.router import router as items_router\n"
        "from app.items.infrastructure.db.repository import SqlItemRepository\n"
        "from app.orders.infrastructure.api.router import router as orders_router\n"
        "from app.shared.api_errors import register_error_handlers\n"
        "from app.shared.config import Settings\n"
        "from app.shared.db import make_session_factory\n\n\n"
        "def build_app(settings: Settings) -> FastAPI:\n"
        "    app = FastAPI()\n"
        "    sessions = make_session_factory(settings.db_path)\n"
        "    app.state.items = CreateItem(SqlItemRepository(sessions))\n"
        "    register_error_handlers(app)\n"
        "    app.include_router(items_router)\n"
        "    app.include_router(orders_router)\n"
        "    return app\n"
    ),
    "src/app/shared/__init__.py": "",
    "src/app/shared/errors.py": (
        "class DomainError(Exception):\n    code = 'domain_error'\n\n\n"
        "class NotFound(DomainError):\n    code = 'not_found'\n"
    ),
    "src/app/shared/types.py": "type ItemId = int\n",
    "src/app/shared/config.py": (
        "import os\nfrom dataclasses import dataclass\n\n\n"
        "@dataclass(frozen=True)\nclass Settings:\n    db_path: str\n\n\n"
        "def load() -> Settings:\n    return Settings(db_path=os.environ.get('APP_DB_PATH', 'data/app.db'))\n"
    ),
    "src/app/shared/db.py": (
        "from sqlalchemy import create_engine\n"
        "from sqlalchemy.orm import DeclarativeBase, sessionmaker\n\n\n"
        "class Base(DeclarativeBase):\n    pass\n\n\n"
        "def make_session_factory(db_path: str) -> sessionmaker:\n"
        "    return sessionmaker(bind=create_engine(f'sqlite:///{db_path}'))\n"
    ),
    "src/app/shared/api_errors.py": (
        "from fastapi import FastAPI, HTTPException, Request\n\n"
        "from app.shared.errors import DomainError, NotFound\n\n\n"
        "def register_error_handlers(app: FastAPI) -> None:\n"
        "    @app.exception_handler(DomainError)\n"
        "    def translate(_: Request, exc: DomainError) -> None:\n"
        "        status = 404 if isinstance(exc, NotFound) else 422\n"
        "        raise HTTPException(status_code=status, detail=exc.code)\n"
    ),
    "src/app/shared/api_auth.py": (
        "from fastapi import HTTPException, Request\n\n\n"
        "def require_token(request: Request) -> None:\n"
        "    if request.headers.get('authorization') != 'Bearer x':\n"
        "        raise HTTPException(status_code=401)\n"
    ),
    "src/app/items/__init__.py": "",
    "src/app/items/domain/__init__.py": "",
    "src/app/items/domain/entities.py": (
        "from dataclasses import dataclass\n\n"
        "from app.shared.errors import DomainError\n"
        "from app.shared.types import ItemId\n\n\n"
        "class EmptyName(DomainError):\n    code = 'empty_name'\n\n\n"
        "@dataclass(frozen=True)\nclass Item:\n    id: ItemId\n    name: str\n\n"
        "    def __post_init__(self) -> None:\n        if not self.name:\n            raise EmptyName()\n"
    ),
    "src/app/items/domain/ports.py": (
        "from typing import Protocol\n\n"
        "from .entities import Item\n\n\n"
        "class ItemRepository(Protocol):\n"
        "    def add(self, item: Item) -> None: ...\n"
        "    def list_all(self) -> list[Item]: ...\n"
    ),
    "src/app/items/application/__init__.py": "",
    "src/app/items/application/create_item.py": (
        "from app.items.domain.entities import Item\n"
        "from app.items.domain.ports import ItemRepository\n"
        "from app.orders.domain.entities import Order\n\n\n"
        "class CreateItem:\n"
        "    def __init__(self, repo: ItemRepository) -> None:\n        self._repo = repo\n\n"
        "    def __call__(self, name: str, order: Order | None = None) -> Item:\n"
        "        item = Item(id=len(self._repo.list_all()) + 1, name=name)\n"
        "        self._repo.add(item)\n        return item\n"
    ),
    "src/app/items/infrastructure/__init__.py": "",
    "src/app/items/infrastructure/api/__init__.py": "",
    "src/app/items/infrastructure/api/deps.py": (
        "from fastapi import Request\n\n"
        "from app.items.application.create_item import CreateItem\n\n\n"
        "def get_create_item(request: Request) -> CreateItem:\n    return request.app.state.items\n"
    ),
    "src/app/items/infrastructure/api/schemas.py": (
        "from pydantic import BaseModel\n\n\nclass ItemIn(BaseModel):\n    name: str\n"
    ),
    "src/app/items/infrastructure/api/router.py": (
        "from fastapi import APIRouter, Depends\n\n"
        "from app.items.application.create_item import CreateItem\n"
        "from app.shared.api_auth import require_token\n\n"
        "from .deps import get_create_item\n"
        "from .schemas import ItemIn\n\n"
        "router = APIRouter(prefix='/items')\n\n\n"
        "@router.post('', dependencies=[Depends(require_token)])\n"
        "def create(body: ItemIn, use_case: CreateItem = Depends(get_create_item)) -> dict[str, int]:\n"
        "    return {'id': use_case(body.name).id}\n"
    ),
    "src/app/items/infrastructure/db/__init__.py": "",
    "src/app/items/infrastructure/db/models.py": (
        "from sqlalchemy.orm import Mapped, mapped_column\n\n"
        "from app.shared.db import Base\n\n\n"
        "class ItemRow(Base):\n    __tablename__ = 'items'\n"
        "    id: Mapped[int] = mapped_column(primary_key=True)\n"
        "    name: Mapped[str]\n"
    ),
    "src/app/items/infrastructure/db/repository.py": (
        "from sqlalchemy import select\n"
        "from sqlalchemy.orm import sessionmaker\n\n"
        "from app.items.domain.entities import Item\n\n"
        "from .models import ItemRow\n\n\n"
        "class SqlItemRepository:\n"
        "    def __init__(self, sessions: sessionmaker) -> None:\n        self._sessions = sessions\n\n"
        "    def add(self, item: Item) -> None:\n"
        "        with self._sessions() as s:\n            s.add(ItemRow(id=item.id, name=item.name))\n            s.commit()\n\n"
        "    def list_all(self) -> list[Item]:\n"
        "        with self._sessions() as s:\n"
        "            return [Item(id=r.id, name=r.name) for r in s.scalars(select(ItemRow))]\n"
    ),
    "src/app/orders/__init__.py": "",
    "src/app/orders/domain/__init__.py": "",
    "src/app/orders/domain/entities.py": (
        "from dataclasses import dataclass\n\n\n@dataclass(frozen=True)\nclass Order:\n    id: int\n"
    ),
    "src/app/orders/application/__init__.py": "",
    "src/app/orders/application/list_orders.py": (
        "from app.orders.domain.entities import Order\n\n\n"
        "class ListOrders:\n    def __call__(self) -> list[Order]:\n        return []\n"
    ),
    "src/app/orders/infrastructure/__init__.py": "",
    "src/app/orders/infrastructure/api/__init__.py": "",
    "src/app/orders/infrastructure/api/router.py": (
        "from fastapi import APIRouter\n\nrouter = APIRouter(prefix='/orders')\n"
    ),
    "src/app/orders/infrastructure/db/__init__.py": "",
    "src/app/orders/infrastructure/db/repository.py": (
        "from sqlalchemy.orm import sessionmaker\n\n\n"
        "class SqlOrderRepository:\n"
        "    def __init__(self, sessions: sessionmaker) -> None:\n        self._sessions = sessions\n"
    ),
    "tests/__init__.py": "",
    "tests/items/__init__.py": "",
    "tests/items/test_create_item.py": (
        "from app.items.application.create_item import CreateItem\n\n\n"
        "def test_create() -> None:\n    assert CreateItem\n"
    ),
    "tests/orders/__init__.py": "",
    "tests/orders/test_list_orders.py": (
        "from app.orders.application.list_orders import ListOrders\n\n\n"
        "def test_list() -> None:\n    assert ListOrders()() == []\n"
    ),
}


def write(name: str, files: dict[str, str], extra: str = "") -> None:
    base = HERE / name
    if base.exists():
        shutil.rmtree(base)
    for rel, body in files.items():
        path = base / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    (base / "pyproject.toml").write_text(PYPROJECT.format(extra=extra))


def variant(**changes: str | None) -> dict[str, str]:
    files = dict(OK)
    for rel, body in changes.items():
        # las claves de kwargs no admiten '/': se usa '__', protegiendo '__init__'
        rel = rel.replace("__init__", "\0init\0").replace("__", "/").replace("\0init\0", "__init__")
        if body is None:
            files.pop(rel)
        else:
            files[rel] = body
    return files


ENT = OK["src/app/items/domain/entities.py"]
UC = OK["src/app/items/application/create_item.py"]
ROUTER = OK["src/app/items/infrastructure/api/router.py"]
REPO = OK["src/app/items/infrastructure/db/repository.py"]

write("ok_project", OK)
write("bad_h001", variant(**{"src__app__items__domain__entities.py": "import fastapi\n" + ENT}))
write(
    "bad_h002",
    variant(
        **{
            "src__app__items__application__create_item.py": (
                "from app.items.infrastructure.db.repository import SqlItemRepository\n" + UC
            )
        }
    ),
)
write(
    "bad_h003",
    variant(
        **{
            "src__app__orders__infrastructure__db__repository.py": (
                "from app.items.infrastructure.db.models import ItemRow\n"
                + OK["src/app/orders/infrastructure/db/repository.py"]
            )
        }
    ),
)
write(
    "bad_h004",
    variant(
        **{
            "src__app__shared__errors.py": (
                "from app.items.domain.entities import Item\n" + OK["src/app/shared/errors.py"]
            )
        }
    ),
)
write(
    "bad_h005",
    variant(
        **{
            "src__app__items__application__archive_item.py": (
                "class ArchiveItem:\n    def __call__(self, item_id: int) -> None:\n        return None\n"
            )
        }
    ),
)
write(
    "bad_h006",
    variant(
        **{
            "src__app__items__infrastructure__api__router.py": ROUTER.replace(
                "from fastapi import APIRouter, Depends",
                "from fastapi import APIRouter, Depends, HTTPException",
            ).replace(
                "    return {'id': use_case(body.name).id}\n",
                "    if not body.name:\n        raise HTTPException(status_code=422)\n"
                "    return {'id': use_case(body.name).id}\n",
            )
        }
    ),
)
write(
    "bad_h007",
    variant(
        **{
            "src__app__items__infrastructure__api__router.py": (
                "from app.items.infrastructure.db.repository import SqlItemRepository\n" + ROUTER
            )
        }
    ),
)
write(
    "bad_h008",
    variant(
        **{
            "src__app__items__infrastructure__db__repository.py": (
                "import os\n" + REPO + "\n\nDEBUG = os.environ.get('DEBUG')\n"
            )
        }
    ),
)
write(
    "bad_h009",
    variant(**{"src__app__items__infrastructure__api__router.py": "import sqlalchemy\n" + ROUTER}),
)
write(
    "bad_h010",
    variant(
        **{
            "src__app__orders__application____init__.py": None,
            "src__app__orders__application__list_orders.py": None,
            "src__app__orders__infrastructure____init__.py": None,
            "src__app__orders__infrastructure__api____init__.py": None,
            "src__app__orders__infrastructure__api__router.py": None,
            "src__app__orders__infrastructure__db____init__.py": None,
            "src__app__orders__infrastructure__db__repository.py": None,
            "tests__orders____init__.py": None,
            "tests__orders__test_list_orders.py": None,
            "src__app__main.py": OK["src/app/main.py"]
            .replace(
                "from app.orders.infrastructure.api.router import router as orders_router\n", ""
            )
            .replace("    app.include_router(orders_router)\n", ""),
        }
    ),
)
W001_UC = UC.replace(
    "from app.items.domain.entities import Item\n",
    "from datetime import datetime\n\nfrom app.items.domain.entities import Item\n",
).replace("        item = Item(", "        _ = datetime.now()\n        item = Item(")
write("warn_w001", variant(**{"src__app__items__application__create_item.py": W001_UC}))
write(
    "ok_clock_port",
    variant(
        **{
            "src__app__items__application__create_item.py": W001_UC,
            "src__app__items__domain__ports.py": OK["src/app/items/domain/ports.py"]
            + "\n\nclass Clock(Protocol):\n    def now(self) -> object: ...\n",
        }
    ),
)
write(
    "allow_h001",
    variant(**{"src__app__items__domain__entities.py": "import fastapi\n" + ENT}),
    extra='allow = ["src/app/items/domain/entities.py: H001 # legado, pendiente de migrar"]\n',
)
write(
    "bad_relative",
    variant(
        **{"src__app__items__domain__entities.py": "from ...shared.config import Settings\n" + ENT}
    ),
)
print("fixtures regenerados en", HERE)
