from fastapi import FastAPI

from app.items.application.create_item import CreateItem
from app.items.infrastructure.api.router import router as items_router
from app.items.infrastructure.db.repository import SqlItemRepository
from app.orders.infrastructure.api.router import router as orders_router
from app.shared.api_errors import register_error_handlers
from app.shared.config import Settings
from app.shared.db import make_session_factory


def build_app(settings: Settings) -> FastAPI:
    app = FastAPI()
    sessions = make_session_factory(settings.db_path)
    app.state.items = CreateItem(SqlItemRepository(sessions))
    register_error_handlers(app)
    app.include_router(items_router)
    app.include_router(orders_router)
    return app
