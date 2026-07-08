from fastapi.testclient import TestClient

from control_tower.api.app import create_app


def sqlite_url(tmp_path) -> str:
    return f"sqlite:///{tmp_path / 'control_tower_gis_test.db'}"


def test_corporate_gis_administration_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))
    client.post(
        "/api/v1/companies",
        json={"company_id": "CRTG", "legal_name": "CRTG S.A.C.", "display_name": "CRTG"},
    )
    client.post(
        "/api/v1/companies/CRTG/projects",
        json={"project_id": "PSZ-2026", "company_id": "CRTG", "name": "Proyecto Suiza"},
    )

    schema = client.post(
        "/api/v1/companies/CRTG/gis/postgis-schemas",
        json={
            "schema_id": "PGS-001",
            "company_id": "CRTG",
            "project_id": "PSZ-2026",
            "schema_name": "crtg_psz_2026",
            "database_ref": "postgis://CRTG/crtg_psz_2026",
        },
    )
    workspace = client.post(
        "/api/v1/companies/CRTG/gis/geoserver/workspaces",
        json={
            "workspace_id": "GWS-001",
            "company_id": "CRTG",
            "project_id": "PSZ-2026",
            "name": "CRTG_PSZ_2026",
            "geoserver_url": "https://geoserver.example.com",
        },
    )
    datastore = client.post(
        "/api/v1/companies/CRTG/gis/geoserver/datastores",
        json={
            "datastore_id": "GDS-001",
            "company_id": "CRTG",
            "project_id": "PSZ-2026",
            "workspace_id": "GWS-001",
            "name": "postgis_psz",
            "postgis_schema_id": "PGS-001",
        },
    )
    layer = client.post(
        "/api/v1/companies/CRTG/gis/geoserver/layers",
        json={
            "layer_id": "GLY-001",
            "company_id": "CRTG",
            "project_id": "PSZ-2026",
            "workspace_id": "GWS-001",
            "datastore_id": "GDS-001",
            "name": "frentes_obra",
            "title": "Frentes de obra",
            "wms_url": "https://geoserver.example.com/wms?layers=CRTG_PSZ_2026:frentes_obra",
            "wfs_url": "https://geoserver.example.com/wfs?typeName=CRTG_PSZ_2026:frentes_obra",
        },
    )
    binding = client.post(
        "/api/v1/companies/CRTG/projects/PSZ-2026/gis/binding",
        json={
            "binding_id": "GBD-001",
            "company_id": "CRTG",
            "project_id": "PSZ-2026",
            "postgis_schema_id": "PGS-001",
            "geoserver_workspace_id": "GWS-001",
        },
    )
    resources = client.get("/api/v1/companies/CRTG/projects/PSZ-2026/gis/resources")
    validations = client.post("/api/v1/companies/CRTG/projects/PSZ-2026/gis/validate")
    validated = client.post("/api/v1/companies/CRTG/projects/PSZ-2026/gis/mark-validated")

    assert schema.status_code == 201
    assert workspace.status_code == 201
    assert datastore.status_code == 201
    assert layer.status_code == 201
    assert binding.status_code == 201
    assert resources.status_code == 200
    assert resources.json()["postgis_schema"]["schema_name"] == "crtg_psz_2026"
    assert resources.json()["geoserver_workspace"]["name"] == "CRTG_PSZ_2026"
    assert resources.json()["layers"][0]["wms_url"].endswith("frentes_obra")
    assert validations.status_code == 200
    assert all(item["valid"] for item in validations.json())
    assert validated.json()["binding"]["status"] == "validated"
    assert client.get("/api/v1/companies/CRTG/gis/postgis-schemas").json()[0]["schema_id"] == "PGS-001"
    assert client.get("/api/v1/companies/CRTG/gis/geoserver/workspaces").json()[0]["workspace_id"] == "GWS-001"
