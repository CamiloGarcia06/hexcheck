"""El traductor de errores de dominio a HTTP: un código por familia.

Un traductor mal cableado no rompe ningún test de caso de uso (esos no ven HTTP)
y deja la API devolviendo códigos equivocados en silencio. Este test lo fija.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from __APP__.shared.api_errors import register_error_handlers, status_for
from __APP__.shared.errors import Conflict, DomainError, Invalid, NotFound, Unavailable, Upstream


def test_status_by_family() -> None:
    assert status_for(Unavailable()) == 503
    assert status_for(Upstream()) == 502
    assert status_for(NotFound()) == 404
    assert status_for(Conflict()) == 409
    assert status_for(Invalid()) == 422
    assert status_for(DomainError()) == 400


def test_subclasses_inherit_their_family() -> None:
    class ThingMissing(NotFound):
        code = "thing_missing"

    assert status_for(ThingMissing()) == 404


def test_handler_returns_code_and_detail() -> None:
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/boom")
    def boom() -> None:
        raise Upstream("el servicio de fuera falló")

    response = TestClient(app).get("/boom")
    assert response.status_code == 502
    assert response.json() == {"error": "upstream", "detail": "el servicio de fuera falló"}
