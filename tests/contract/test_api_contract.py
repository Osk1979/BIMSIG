from fastapi.testclient import TestClient

from control_tower.api.app import create_app


def sqlite_url(tmp_path) -> str:
    return f"sqlite:///{tmp_path / 'control_tower_test.db'}"


def test_health_contract() -> None:
    client = TestClient(create_app(database_url="sqlite:///:memory:"))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "revision": "REV12",
        "service": "corporate-control-tower",
    }


def test_project_registration_and_websig_provisioning_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))

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


def test_project_registration_persists_across_app_instances(tmp_path) -> None:
    database_url = sqlite_url(tmp_path)
    first_client = TestClient(create_app(database_url=database_url))

    first_client.post(
        "/api/v1/projects",
        json={"project_id": "PSZ-2026", "name": "Proyecto Suiza", "cui": "CUI 2661613"},
    )
    second_client = TestClient(create_app(database_url=database_url))
    listed = second_client.get("/api/v1/projects")

    assert listed.status_code == 200
    assert listed.json() == [
        {
            "project_id": "PSZ-2026",
            "name": "Proyecto Suiza",
            "cui": "CUI 2661613",
            "status": "registered",
        }
    ]
