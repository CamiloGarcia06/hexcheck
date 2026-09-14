"""El único traductor de errores de dominio a HTTP (regla H006)."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from __APP__.shared.errors import Conflict, DomainError, Invalid, NotFound

STATUS: dict[type[DomainError], int] = {NotFound: 404, Conflict: 409, Invalid: 422}


def status_for(exc: DomainError) -> int:
    for base, status in STATUS.items():
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
