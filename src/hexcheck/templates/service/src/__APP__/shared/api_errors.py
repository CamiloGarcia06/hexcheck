"""El único traductor de errores de dominio a HTTP (regla H006)."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from __APP__.shared.errors import Conflict, DomainError, Invalid, NotFound, Unavailable, Upstream

# Una familia, un código. El orden importa si una familia hereda de otra: gana
# la primera que case. tests/test_api_errors.py fija esta tabla; si cambias un
# código, cambia el test en el mismo commit.
STATUS: tuple[tuple[type[DomainError], int], ...] = (
    (Unavailable, 503),
    (Upstream, 502),
    (NotFound, 404),
    (Conflict, 409),
    (Invalid, 422),
)


def status_for(exc: DomainError) -> int:
    for base, status in STATUS:
        if isinstance(exc, base):
            return status
    return 400


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    def translate(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=status_for(exc),
            content={"error": exc.code, "detail": exc.message},
        )
