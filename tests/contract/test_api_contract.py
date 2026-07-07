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


def test_operational_health_contract() -> None:
    client = TestClient(create_app(database_url="sqlite:///:memory:"))

    response = client.get("/api/v1/operational/health")

    assert response.status_code == 200
    assert response.json()["database"] == "ok"


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

    listed_requests = client.get("/api/v1/provisioning/websig")
    project = client.get("/api/v1/projects/PSZ-2026")
    summary = client.get("/api/v1/portfolio/summary")

    assert listed_requests.status_code == 200
    assert len(listed_requests.json()) == 1
    assert project.json()["status"] == "provisioning_requested"
    assert summary.json()["total_projects"] == 1
    assert summary.json()["provisioning_requested"] == 1


def test_governance_status_and_audit_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))
    client.post("/api/v1/projects", json={"project_id": "PSZ-2026", "name": "Proyecto Suiza"})

    updated = client.patch(
        "/api/v1/projects/PSZ-2026/governance-status",
        json={"status": "active"},
    )
    audit = client.get("/api/v1/audit/events")

    assert updated.status_code == 200
    assert updated.json()["status"] == "active"
    assert audit.status_code == 200
    assert {event["action"] for event in audit.json()} >= {
        "project.registered",
        "project.status_changed",
    }


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
