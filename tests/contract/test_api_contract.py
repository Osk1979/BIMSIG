from fastapi.testclient import TestClient

from control_tower.api.app import create_app


def test_health_contract() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "revision": "REV12",
        "service": "corporate-control-tower",
    }


def test_project_registration_and_websig_provisioning_contract() -> None:
    client = TestClient(create_app())

    created = client.post(
        "/api/v1/projects",
        json={"project_id": "PSZ-2026", "name": "Proyecto Suiza", "cui": "CUI 2661613"},
    )
    provisioned = client.post("/api/v1/provisioning/websig", json={"project_id": "PSZ-2026"})

    assert created.status_code == 201
    assert created.json()["status"] == "registered"
    assert provisioned.status_code == 202
    assert provisioned.json()["project_id"] == "PSZ-2026"
    assert provisioned.json()["target_revision"] == "REV12"
