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

    response = client.get("/health", headers={"X-Request-ID": "REQ-001"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "REQ-001"
    assert "X-Response-Time-Ms" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Permissions-Policy"] == "geolocation=(), microphone=(), camera=()"
