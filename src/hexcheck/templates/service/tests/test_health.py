from fastapi.testclient import TestClient


def test_health_reports_version_and_db(client: TestClient) -> None:
    body = client.get("/health").json()
    assert body == {"status": "ok", "version": "test", "db": "ok"}
