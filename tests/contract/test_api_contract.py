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
    client.post(
        "/api/v1/companies",
        json={"company_id": "CRTG", "legal_name": "CRTG S.A.C.", "display_name": "CRTG"},
    )

    created = client.post(
        "/api/v1/companies/CRTG/projects",
        json={
            "project_id": "PSZ-2026",
            "company_id": "CRTG",
            "name": "Proyecto Suiza",
            "cui": "CUI 2661613",
        },
    )
    provisioned = client.post("/api/v1/provisioning/websig", json={"project_id": "PSZ-2026"})

    assert created.status_code == 201
    assert created.json()["status"] == "registered"
    assert provisioned.status_code == 202
    assert provisioned.json()["project_id"] == "PSZ-2026"
    assert provisioned.json()["target_revision"] == "REV12"

    listed_requests = client.get("/api/v1/provisioning/websig")
    project = client.get("/api/v1/companies/CRTG/projects/PSZ-2026")
    summary = client.get("/api/v1/companies/CRTG/portfolio/summary")

    assert listed_requests.status_code == 200
    assert len(listed_requests.json()) == 1
    assert project.json()["status"] == "provisioning_requested"
    assert project.json()["company_id"] == "CRTG"
    assert summary.json()["total_projects"] == 1
    assert summary.json()["provisioning_requested"] == 1


def test_enterprise_project_stack_provisioning_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))

    provisioned = client.post(
        "/api/v1/companies/CRTG/provisioning/project-stack",
        json={
            "company": {
                "company_id": "CRTG",
                "legal_name": "CRTG S.A.C.",
                "display_name": "CRTG",
            },
            "project": {
                "project_id": "PSZ-2026",
                "company_id": "CRTG",
                "name": "Proyecto Suiza",
                "cui": "CUI 2661613",
            },
            "users": [
                {
                    "user_id": "USR-001",
                    "email": "admin@example.com",
                    "display_name": "Admin User",
                }
            ],
            "memberships": [
                {
                    "membership_id": "MEM-001",
                    "company_id": "CRTG",
                    "user_id": "USR-001",
                    "role": "portfolio_manager",
                }
            ],
            "catalogs": ["disciplinas", "estados_gobierno"],
        },
    )
    project = client.get("/api/v1/companies/CRTG/projects/PSZ-2026")
    requests = client.get("/api/v1/companies/CRTG/provisioning/websig")

    assert provisioned.status_code == 202
    assert provisioned.json()["operation"] == "project_stack"
    assert provisioned.json()["status"] == "provisioned"
    assert provisioned.json()["company_id"] == "CRTG"
    assert project.json()["status"] == "active"
    assert requests.status_code == 200
    assert requests.json()[0]["operation"] == "project_stack"
    assert {
        step["resource_type"] for step in provisioned.json()["steps"]
    } >= {
        "company",
        "project",
        "websig",
        "postgis",
        "nas",
        "document_structure",
        "geoserver",
        "dashboard",
        "user",
        "role",
        "catalog",
    }


def test_enterprise_project_stack_dry_run_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))

    dry_run = client.post(
        "/api/v1/companies/CRTG/provisioning/project-stack/dry-run",
        json={
            "company": {
                "company_id": "CRTG",
                "legal_name": "CRTG S.A.C.",
                "display_name": "CRTG",
            },
            "project": {
                "project_id": "PSZ-2026",
                "company_id": "CRTG",
                "name": "Proyecto Suiza",
            },
            "catalogs": ["disciplinas"],
        },
    )

    assert dry_run.status_code == 200
    assert dry_run.json()["operation"] == "project_stack"
    assert {step["status"] for step in dry_run.json()["steps"]} == {"planned"}
    assert client.get("/api/v1/companies/CRTG").status_code == 404
    assert client.get("/api/v1/provisioning/websig").json() == []


def test_governance_status_and_audit_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))
    client.post(
        "/api/v1/companies",
        json={"company_id": "CRTG", "legal_name": "CRTG S.A.C.", "display_name": "CRTG"},
    )
    client.post(
        "/api/v1/companies/CRTG/projects",
        json={"project_id": "PSZ-2026", "company_id": "CRTG", "name": "Proyecto Suiza"},
    )

    updated = client.patch(
        "/api/v1/companies/CRTG/projects/PSZ-2026/governance-status",
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


def test_enterprise_company_user_membership_and_license_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))

    company = client.post(
        "/api/v1/companies",
        json={
            "company_id": "CRTG",
            "legal_name": "CRTG S.A.C.",
            "display_name": "CRTG",
            "tax_id": "RUC 00000000000",
        },
    )
    user = client.post(
        "/api/v1/users",
        json={
            "user_id": "USR-001",
            "email": "admin@example.com",
            "display_name": "Admin User",
        },
    )
    membership = client.post(
        "/api/v1/companies/CRTG/memberships",
        json={
            "membership_id": "MEM-001",
            "company_id": "CRTG",
            "user_id": "USR-001",
            "role": "portfolio_manager",
        },
    )
    plan = client.post(
        "/api/v1/license-plans",
        json={
            "plan_id": "PLAN-ENTERPRISE",
            "name": "Enterprise",
            "max_users": 50,
            "max_projects": 20,
            "max_websig_instances": 20,
            "enabled_modules": "portfolio,provisioning,audit,ai,reports",
            "ai_enabled": True,
            "reporting_enabled": True,
        },
    )
    license_assignment = client.post(
        "/api/v1/companies/CRTG/licenses",
        json={
            "company_license_id": "LIC-001",
            "company_id": "CRTG",
            "plan_id": "PLAN-ENTERPRISE",
            "valid_from": "2026-07-07",
        },
    )

    assert company.status_code == 201
    assert user.status_code == 201
    assert membership.status_code == 201
    assert plan.status_code == 201
    assert license_assignment.status_code == 201
    assert client.get("/api/v1/companies").json()[0]["company_id"] == "CRTG"
    assert client.get("/api/v1/users").json()[0]["user_id"] == "USR-001"
    assert client.get("/api/v1/companies/CRTG/memberships").json()[0]["role"] == "portfolio_manager"
    assert client.get("/api/v1/companies/CRTG/licenses").json()[0]["plan_id"] == "PLAN-ENTERPRISE"
    assert {
        event["action"] for event in client.get("/api/v1/audit/events").json()
    } >= {
        "company.registered",
        "user.registered",
        "membership.assigned",
        "license_plan.saved",
        "company_license.assigned",
    }


def test_executive_dashboard_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))
    client.post(
        "/api/v1/companies",
        json={"company_id": "CRTG", "legal_name": "CRTG S.A.C.", "display_name": "CRTG"},
    )
    client.post(
        "/api/v1/companies/CRTG/projects",
        json={"project_id": "PSZ-2026", "company_id": "CRTG", "name": "Proyecto Suiza"},
    )

    response = client.get("/api/v1/companies/CRTG/dashboard/executive")
    html = client.get("/dashboard")

    assert response.status_code == 200
    assert response.json()["company_id"] == "CRTG"
    assert {"portfolio", "map_points", "kpis", "risks", "comparisons"} <= set(response.json())
    assert html.status_code == 200
    assert "Dashboard Ejecutivo Corporativo" in html.text
    assert "data-theme=\"dark\"" in html.text


def test_nas_information_center_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))
    client.post(
        "/api/v1/companies",
        json={"company_id": "CRTG", "legal_name": "CRTG S.A.C.", "display_name": "CRTG"},
    )
    client.post(
        "/api/v1/companies/CRTG/projects",
        json={"project_id": "PSZ-2026", "company_id": "CRTG", "name": "Proyecto Suiza"},
    )

    asset = client.post(
        "/api/v1/companies/CRTG/nas/assets",
        json={
            "asset_id": "NAS-001",
            "company_id": "CRTG",
            "project_id": "PSZ-2026",
            "name": "Modelo federado IFC",
            "asset_type": "ifc",
            "category": "bim",
            "logical_uri": "nas://CRTG/PSZ-2026/bim/ifc/model.ifc",
            "metadata": {"discipline": "bim"},
            "google_drive_id": "drive-folder-1",
            "geoserver_reference": "geoserver://workspace/CRTG_PSZ",
            "postgis_reference": "postgis://CRTG/psz_2026",
            "docker_reference": "docker://websig/psz-2026",
        },
    )
    version = client.post(
        "/api/v1/nas/assets/NAS-001/versions",
        json={"version": "v2", "logical_uri": "nas://CRTG/PSZ-2026/bim/ifc/model-v2.ifc"},
    )
    permission = client.patch(
        "/api/v1/nas/assets/NAS-001/permissions",
        json={"principal": "role:portfolio_manager", "permission": "admin"},
    )
    metadata = client.patch(
        "/api/v1/nas/assets/NAS-001/metadata",
        json={"metadata": {"document_status": "review"}},
    )
    snapshot = client.post(
        "/api/v1/companies/CRTG/nas/snapshots",
        json={"name": "Cierre Semanal", "project_id": "PSZ-2026", "asset_ids": ["NAS-001"]},
    )
    backup = client.post(
        "/api/v1/companies/CRTG/nas/backups",
        json={
            "project_id": "PSZ-2026",
            "snapshot_id": snapshot.json()["snapshot_id"],
            "logical_uri": "nas://CRTG/PSZ-2026/backups/cierre.zip",
        },
    )
    archived = client.patch("/api/v1/nas/assets/NAS-001/archive")

    assert asset.status_code == 201
    assert asset.json()["asset_type"] == "ifc"
    assert asset.json()["category"] == "bim"
    assert asset.json()["status"] == "draft"
    assert version.status_code == 200
    assert version.json()["version"] == "v2"
    assert permission.json()["permissions"]["role:portfolio_manager"] == "admin"
    assert metadata.json()["metadata"]["document_status"] == "review"
    assert snapshot.status_code == 200
    assert backup.status_code == 200
    assert archived.json()["status"] == "archived"
    assert client.get("/api/v1/companies/CRTG/nas/assets").json()[0]["asset_id"] == "NAS-001"
    assert client.get("/api/v1/nas/assets/NAS-001/versions").json()[0]["version"] == "v2"


def test_project_registration_persists_across_app_instances(tmp_path) -> None:
    database_url = sqlite_url(tmp_path)
    first_client = TestClient(create_app(database_url=database_url))

    first_client.post(
        "/api/v1/companies",
        json={"company_id": "CRTG", "legal_name": "CRTG S.A.C.", "display_name": "CRTG"},
    )
    first_client.post(
        "/api/v1/companies/CRTG/projects",
        json={
            "project_id": "PSZ-2026",
            "company_id": "CRTG",
            "name": "Proyecto Suiza",
            "cui": "CUI 2661613",
        },
    )
    second_client = TestClient(create_app(database_url=database_url))
    listed = second_client.get("/api/v1/companies/CRTG/projects")

    assert listed.status_code == 200
    assert listed.json() == [
        {
            "project_id": "PSZ-2026",
            "company_id": "CRTG",
            "name": "Proyecto Suiza",
            "cui": "CUI 2661613",
            "customer_id": None,
            "program_id": None,
            "status": "registered",
            "lifecycle_stage": "intake",
            "websig_instance_id": None,
            "websig_url": None,
            "nas_root_uri": None,
            "gis_binding_id": None,
            "google_drive_folder_id": None,
        }
    ]


def test_corporate_portfolio_domain_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))
    client.post(
        "/api/v1/companies",
        json={"company_id": "CRTG", "legal_name": "CRTG S.A.C.", "display_name": "CRTG"},
    )
    customer = client.post(
        "/api/v1/companies/CRTG/portfolio/customers",
        json={
            "customer_id": "CLI-MTC",
            "company_id": "CRTG",
            "legal_name": "Ministerio de Transportes",
            "display_name": "MTC",
        },
    )
    program = client.post(
        "/api/v1/companies/CRTG/portfolio/programs",
        json={
            "program_id": "PRG-TRANSPORTE",
            "company_id": "CRTG",
            "customer_id": "CLI-MTC",
            "name": "Programa Transporte",
        },
    )
    project = client.post(
        "/api/v1/companies/CRTG/projects",
        json={
            "project_id": "PSZ-2026",
            "company_id": "CRTG",
            "customer_id": "CLI-MTC",
            "program_id": "PRG-TRANSPORTE",
            "name": "Proyecto Suiza",
            "websig_instance_id": "WEB-PSZ-2026",
            "websig_url": "https://websig.example.com/psz",
            "nas_root_uri": "nas://CRTG/PSZ-2026",
            "google_drive_folder_id": "DRIVE-PSZ",
        },
    )
    lifecycle = client.patch(
        "/api/v1/companies/CRTG/projects/PSZ-2026/lifecycle",
        json={"lifecycle_stage": "execution"},
    )
    view = client.get("/api/v1/companies/CRTG/projects/PSZ-2026/portfolio-governance")

    assert customer.status_code == 201
    assert program.status_code == 201
    assert project.status_code == 201
    assert lifecycle.status_code == 200
    assert lifecycle.json()["status"] == "active"
    assert view.status_code == 200
    assert view.json()["project"]["customer_id"] == "CLI-MTC"
    assert view.json()["customer"]["display_name"] == "MTC"
    assert view.json()["program"]["program_id"] == "PRG-TRANSPORTE"
    assert view.json()["integrations"]["websig_instance_id"] == "WEB-PSZ-2026"
    assert view.json()["integrations"]["nas_root_uri"] == "nas://CRTG/PSZ-2026"


def test_corporate_user_security_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))
    client.post(
        "/api/v1/companies",
        json={"company_id": "CRTG", "legal_name": "CRTG S.A.C.", "display_name": "CRTG"},
    )
    client.post(
        "/api/v1/users",
        json={"user_id": "USR-001", "email": "admin@example.com", "display_name": "Admin"},
    )
    client.post(
        "/api/v1/companies/CRTG/projects",
        json={"project_id": "PSZ-2026", "company_id": "CRTG", "name": "Proyecto Suiza"},
    )

    specialty = client.post(
        "/api/v1/specialties",
        json={"specialty_id": "SPEC-BIM", "name": "BIM Management"},
    )
    user_specialty = client.post(
        "/api/v1/users/USR-001/specialties",
        json={
            "user_specialty_id": "USPEC-001",
            "user_id": "USR-001",
            "specialty_id": "SPEC-BIM",
        },
    )
    project_membership = client.post(
        "/api/v1/companies/CRTG/projects/PSZ-2026/memberships",
        json={
            "project_membership_id": "PMEM-001",
            "company_id": "CRTG",
            "project_id": "PSZ-2026",
            "user_id": "USR-001",
            "role": "project_operator",
        },
    )
    role_permission = client.post(
        "/api/v1/roles/project_operator/permissions",
        json={
            "role_permission_id": "PERM-001",
            "role": "project_operator",
            "scope": "nas",
            "action": "write",
        },
    )
    identity = client.post(
        "/api/v1/users/USR-001/auth-identities",
        json={
            "identity_id": "IDP-001",
            "user_id": "USR-001",
            "provider": "oidc",
            "subject": "aad|001",
            "email": "admin@example.com",
        },
    )
    resolved = client.post(
        "/api/v1/auth/sso/resolve",
        json={"provider": "oidc", "subject": "aad|001"},
    )
    history = client.get("/api/v1/users/USR-001/history")

    assert specialty.status_code == 201
    assert user_specialty.status_code == 201
    assert project_membership.status_code == 201
    assert role_permission.status_code == 201
    assert identity.status_code == 201
    assert resolved.status_code == 200
    assert resolved.json()["user_id"] == "USR-001"
    assert client.get("/api/v1/specialties").json()[0]["specialty_id"] == "SPEC-BIM"
    assert client.get("/api/v1/users/USR-001/specialties").json()[0]["specialty_id"] == "SPEC-BIM"
    assert client.get("/api/v1/roles/project_operator/permissions").json()[0]["scope"] == "nas"
    assert history.status_code == 200
    assert {
        event["action"] for event in history.json()
    } >= {
        "user_specialty.assigned",
        "project_membership.assigned",
        "auth_identity.linked",
        "auth_identity.authenticated",
    }
