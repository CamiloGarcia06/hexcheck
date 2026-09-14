"""Humo de la API: códigos, esquemas y el traductor de errores. Sin base de datos."""

from fastapi.testclient import TestClient


def test_create_requires_token(client: TestClient) -> None:
    assert client.post("/api/__FEATURE__", json={"name": "x"}).status_code == 401


def test_create_and_list(client: TestClient, auth: dict[str, str]) -> None:
    created = client.post("/api/__FEATURE__", json={"name": "primera"}, headers=auth)
    assert created.status_code == 201
    assert created.json() == {"id": 1, "name": "primera"}
    assert client.get("/api/__FEATURE__").json() == [{"id": 1, "name": "primera"}]


def test_domain_error_is_translated(client: TestClient, auth: dict[str, str]) -> None:
    response = client.post("/api/__FEATURE__", json={"name": "   "}, headers=auth)
    assert response.status_code == 422
    assert response.json()["error"] == "empty___entity___name"
