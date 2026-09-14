from fastapi import FastAPI, HTTPException, Request

from app.shared.errors import DomainError, NotFound


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    def translate(_: Request, exc: DomainError) -> None:
        status = 404 if isinstance(exc, NotFound) else 422
        raise HTTPException(status_code=status, detail=exc.code)
