"""Raíz de composición: el único módulo que conoce todas las piezas concretas.

`hexcheck add <feature>` inserta líneas antes de los comentarios `# hexcheck:...`.
No los borres.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from fastapi import FastAPI, Request

from __APP__.shared.api_errors import register_error_handlers
from __APP__.shared.config import Settings
from __APP__.shared.db import make_engine, make_session_factory, ping

# hexcheck:imports


@dataclass(frozen=True)
class Deps:
    """Adaptadores concretos. Los tests construyen uno con fakes (tests/conftest.py)."""

    db_ping: Callable[[], bool]
    # hexcheck:deps


def build_deps(settings: Settings) -> Deps:
    sessions = make_session_factory(make_engine(settings.db_path))
    return Deps(
        db_ping=lambda: ping(sessions),
        # hexcheck:deps-build
    )


def build_app(settings: Settings | None = None, deps: Deps | None = None) -> FastAPI:
    settings = settings or Settings()
    if not settings.token:
        raise RuntimeError("__APP_UPPER___TOKEN vacío: el token de escritura es obligatorio")
    deps = deps or build_deps(settings)
    app = FastAPI(title="__NAME__", version=settings.version)
    app.state.settings = settings
    register_error_handlers(app)

    @app.get("/health")
    def health(request: Request) -> dict[str, str]:
        db_ok = deps.db_ping()
        return {
            "status": "ok" if db_ok else "degraded",
            "version": request.app.state.settings.version,
            "db": "ok" if db_ok else "error",
        }

    # hexcheck:wire
    return app


def app() -> FastAPI:
    """Factoría para uvicorn: `uvicorn __APP__.main:app --factory`."""
    return build_app()
