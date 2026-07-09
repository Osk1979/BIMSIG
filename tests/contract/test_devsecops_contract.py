from fastapi.testclient import TestClient

from control_tower import __version__
from control_tower.api.app import create_app


def test_operational_readiness_and_version_contract() -> None:
    client = TestClient(create_app(database_url="sqlite:///:memory:"))

    readiness = client.get("/api/v1/operational/readiness")
    version = client.get("/api/v1/operational/version")

    assert readiness.status_code == 200
    assert readiness.json() == {
        "status": "ready",
        "database": "ready",
        "revision": "REV12",
    }
    assert version.status_code == 200
    assert version.json() == {
        "service": "corporate-control-tower",
        "version": __version__,
        "revision": "REV12",
    }


def test_devsecops_security_headers_and_request_id_contract() -> None:
    client = TestClient(create_app(database_url="sqlite:///:memory:"))

    response = client.get(
        "/health",
        headers={"X-Request-ID": "REQ-001", "X-Correlation-ID": "CORR-001"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "REQ-001"
    assert response.headers["X-Correlation-ID"] == "CORR-001"
    assert "X-Response-Time-Ms" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Permissions-Policy"] == "geolocation=(), microphone=(), camera=()"


def test_observability_monitoring_contract() -> None:
    client = TestClient(create_app(database_url="sqlite:///:memory:"))

    client.get("/health", headers={"X-Correlation-ID": "CORR-MON-001"})
    metrics = client.get("/api/v1/observability/metrics")
    prometheus = client.get("/metrics")
    health = client.get("/api/v1/observability/health/deep")
    dashboard = client.get("/api/v1/observability/dashboard")
    otel = client.get("/api/v1/observability/otel")

    assert metrics.status_code == 200
    assert metrics.json()["total_requests"] >= 1
    assert prometheus.status_code == 200
    assert "control_tower_http_requests_total" in prometheus.text
    assert health.status_code == 200
    assert health.json()["database"] == "ok"
    assert len(health.json()["connectors"]) == 4
    assert dashboard.status_code == 200
    assert dashboard.json()["service"] == "corporate-control-tower"
    assert "alerts" in dashboard.json()
    assert otel.status_code == 200
    assert otel.json()["resource"]["service.name"] == "corporate-control-tower"
