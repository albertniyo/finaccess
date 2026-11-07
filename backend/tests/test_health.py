"""API contract tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
VERCEL = "https://finaccessrw.vercel.app"


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["data"] == "ok"
    assert body["districts"] == 30


def test_meta_sources() -> None:
    body = client.get("/meta/sources").json()
    ids = {s["id"] for s in body["sources"]}
    assert {"eicv7-tables", "finscope-2024"} <= ids


def test_meta_validation_and_method() -> None:
    validation = client.get("/meta/validation").json()
    assert validation["status"] == "ok"
    assert validation["failed"] == 0
    method = client.get("/meta/method").json()
    assert "formula" in method and method["typology"]


def test_indicators() -> None:
    body = client.get("/indicators").json()
    assert body["status"] == "ok"
    assert len(body["districts"]) == 30
    row = body["districts"][0]
    assert {"poverty_rate", "excluded", "profile"} <= set(row)
    assert row["poverty_rate"]["uncertainty"] == "published"
    assert row["excluded"]["uncertainty"] == "approximate"


def test_indicators_province_filter() -> None:
    body = client.get("/indicators", params={"province": "northern"}).json()
    assert body["filters"]["province"] == "Northern"
    assert len(body["districts"]) == 5


def test_indicators_unknown_province() -> None:
    assert client.get("/indicators", params={"province": "Atlantis"}).status_code == 422


def test_geo_districts() -> None:
    body = client.get("/geo/districts").json()
    assert body["type"] == "FeatureCollection"
    assert len(body["features"]) == 30


def test_priorities() -> None:
    response = client.get("/priorities", params={"povertyWeight": 0.6, "exclusionWeight": 0.4})
    assert response.status_code == 200
    body = response.json()
    assert body["weights"]["poverty"] == 0.6
    assert body["weights"]["exclusion"] == 0.4
    assert len(body["rankings"]) == 30


def test_priorities_rejects_bad_input() -> None:
    assert client.get("/priorities", params={"measure": "vibes"}).status_code == 422
    assert client.get("/priorities", params={"povertyWeight": 2}).status_code == 422


def test_scenario() -> None:
    response = client.post(
        "/scenarios", json={"budget": 1_000_000, "strategy": "combined_score", "topN": 5}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["label"] == "scenario"
    assert len(body["allocations"]) == 5
    assert sum(a["share"] for a in body["allocations"]) == 1.0
    assert {c["strategy"] for c in body["comparison"]} == {"poverty_only", "exclusion_gap", "combined_score"}


def test_scenario_rejects_unknown_strategy() -> None:
    response = client.post("/scenarios", json={"budget": 1_000_000, "strategy": "magic"})
    assert response.status_code == 422


def test_brief() -> None:
    response = client.post("/briefs", json={"geo": "Ngoma", "povertyWeight": 0.5, "exclusionWeight": 0.5})
    assert response.status_code == 200
    body = response.json()
    assert body["geo"] == "Ngoma"
    kinds = {s["kind"] for sec in ("key_findings", "interpretation", "next_steps") for s in body["sections"][sec]}
    assert {"observed", "estimate", "recommendation"} <= kinds
    assert body["sections"]["limitations"]


def test_brief_unknown_district() -> None:
    assert client.post("/briefs", json={"geo": "Atlantis"}).status_code == 404


def test_cors_allows_vercel_frontend() -> None:
    response = client.options(
        "/priorities",
        headers={"Origin": VERCEL, "Access-Control-Request-Method": "GET"},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == VERCEL


def test_cors_allows_vercel_preview() -> None:
    origin = "https://finaccessrw-git-main-albertniyo.vercel.app"
    response = client.get("/health", headers={"Origin": origin})
    assert response.headers["access-control-allow-origin"] == origin


def test_security_and_cache_headers() -> None:
    response = client.get("/indicators")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "max-age" in response.headers["cache-control"]
    assert client.get("/health").headers["cache-control"] == "no-store"


def test_indicators_include_context_and_groups() -> None:
    body = client.get("/indicators").json()
    ids = {i["id"] for i in body["indicators"]}
    assert {"health_insurance", "smartphone_households", "internet_households", "poverty_decrease"} <= ids
    assert body["who_is_excluded"]["groups"]
    assert set(body["flags"]) >= {"slow_poverty_reduction", "low_digital_readiness"}


def test_priorities_cache_returns_independent_copies() -> None:
    a = client.get("/priorities").json()
    a["rankings"].clear()
    b = client.get("/priorities").json()
    assert len(b["rankings"]) == 30


def test_cors_rejects_other_origins() -> None:
    response = client.get("/health", headers={"Origin": "https://evil.example.com"})
    assert "access-control-allow-origin" not in response.headers
