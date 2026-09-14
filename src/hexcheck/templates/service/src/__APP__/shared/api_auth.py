"""Token de escritura: dependencia para todo endpoint que modifique datos (decisión 13)."""

from __future__ import annotations

import secrets

from fastapi import HTTPException, Request


def require_token(request: Request) -> None:
    expected = request.app.state.settings.token
    header = request.headers.get("authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not secrets.compare_digest(token, expected):
        raise HTTPException(status_code=401, detail="token de escritura inválido")
