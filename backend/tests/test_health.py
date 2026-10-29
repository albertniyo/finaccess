"""API smoke tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_meta_sources() -> None:
    response = client.get("/meta/sources")
    assert response.status_code == 200
    body = response.json()
    assert "sources" in body
    assert len(body["sources"]) >= 1


def test_priorities_stub() -> None:
    response = client.get("/priorities", params={"povertyWeight": 0.6, "exclusionWeight": 0.4})
    assert response.status_code == 200
    body = response.json()
    assert body["weights"]["poverty"] == 0.6
    assert body["weights"]["exclusion"] == 0.4


def test_scenario_rejects_unknown_strategy() -> None:
    response = client.post("/scenarios", json={"budget": 1_000_000, "strategy": "magic"})
    assert response.status_code == 200
    assert response.json()["status"] == "error"