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


def test_infrastructure_connectors_contract(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("CONTROL_TOWER_NAS_ROOT", str(tmp_path / "nas-root"))
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))

    health = client.get("/api/v1/infrastructure/connectors/health")
    dry_run = client.post(
        "/api/v1/infrastructure/connectors/nas/dry-run",
        json={
            "company_id": "CRTG",
            "project_id": "PSZ-2026",
            "target": {"folder": "websig"},
        },
    )
    execute_without_approval = client.post(
        "/api/v1/infrastructure/connectors/nas/execute",
        json={
            "company_id": "CRTG",
            "project_id": "PSZ-2026",
            "target": {"folder": "websig"},
        },
    )
    execute = client.post(
        "/api/v1/infrastructure/connectors/nas/execute",
        json={
            "company_id": "CRTG",
            "project_id": "PSZ-2026",
            "target": {"folder": "websig"},
            "approved_by": "USR-ADMIN",
        },
    )
    audit = client.get("/api/v1/audit/events?limit=10")

    assert health.status_code == 200
    assert {item["connector"] for item in health.json()} == {"postgis", "geoserver", "nas", "google_drive"}
    assert dry_run.status_code == 200
    assert dry_run.json()["status"] == "planned"
    assert execute_without_approval.status_code == 400
    assert execute.status_code == 202
    assert execute.json()["status"] == "executed"
    assert (tmp_path / "nas-root" / "CRTG" / "PSZ-2026" / "websig").is_dir()
    assert any(event["action"] == "infrastructure.nas.execute" for event in audit.json())


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
            "approved_by": "portfolio-manager",
        },
    )
    project = client.get("/api/v1/companies/CRTG/projects/PSZ-2026")
    requests = client.get("/api/v1/companies/CRTG/provisioning/websig")

    assert provisioned.status_code == 202
    assert provisioned.json()["operation"] == "project_stack"
    assert provisioned.json()["status"] == "provisioned"
    assert provisioned.json()["execution_mode"] == "controlled"
    assert provisioned.json()["approved_by"] == "portfolio-manager"
    assert provisioned.json()["company_id"] == "CRTG"
    assert project.json()["status"] == "active"
    assert requests.status_code == 200
    assert requests.json()[0]["operation"] == "project_stack"
    assert {
        step["resource_type"] for step in provisioned.json()["steps"]
    } >= {
        "factory_blueprint",
        "governance_gate",
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


def test_websig_factory_controlled_execution_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))
    payload = {
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
        "factory_blueprint": {
            "template_id": "WEB-SIG-ENTERPRISE-REV13",
            "websig_slug": "crtg-psz-2026",
            "websig_url": "https://websig.example.com/crtg/psz-2026",
            "nas_root_uri": "nas://CRTG/PSZ-2026/websig/root",
            "postgis_schema_name": "crtg_psz_2026",
            "geoserver_workspace": "CRTG_PSZ_2026",
        },
    }

    dry_run = client.post("/api/v1/companies/CRTG/websig-factory/dry-run", json=payload)
    rejected = client.post("/api/v1/companies/CRTG/websig-factory/execute", json=payload)
    executed = client.post(
        "/api/v1/companies/CRTG/websig-factory/execute",
        json={**payload, "approved_by": "portfolio-manager"},
    )
    project = client.get("/api/v1/companies/CRTG/projects/PSZ-2026")

    assert dry_run.status_code == 200
    assert dry_run.json()["operation"] == "websig_factory"
    assert dry_run.json()["execution_mode"] == "dry_run"
    assert {step["status"] for step in dry_run.json()["steps"]} == {"planned"}
    assert rejected.status_code == 400
    assert "approved_by" in rejected.json()["detail"]
    assert executed.status_code == 202
    assert executed.json()["status"] == "provisioned"
    assert executed.json()["approved_by"] == "portfolio-manager"
    assert project.json()["websig_instance_id"] == "WEB-CRTG-PSZ-2026"
    assert project.json()["websig_url"] == "https://websig.example.com/crtg/psz-2026"
    assert project.json()["nas_root_uri"] == "nas://CRTG/PSZ-2026/websig/root"
    assert project.json()["gis_binding_id"] == "GBD-CRTG-PSZ-2026"


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
    assert {
        "portfolio",
        "map_points",
        "kpis",
        "risks",
        "comparisons",
        "portfolio_governance",
        "operational_flow",
        "operating_model",
    } <= set(response.json())
    assert response.json()["portfolio_governance"][0]["project_id"] == "PSZ-2026"
    assert response.json()["operational_flow"][0]["project_id"] == "PSZ-2026"
    assert response.json()["operating_model"]["phase"] == "Fase 3 - funcionamiento operativo"
    assert html.status_code == 200
    assert "Dashboard Ejecutivo Corporativo" in html.text
    assert "Corporate Experience" in html.text
    assert "Corporate Home" in html.text
    assert "Control Ejecutivo" in html.text
    assert "GIS Corporativo" in html.text
    assert "Corporate GIS Dashboard" in html.text
    assert "Comunicacion KPI -> Mapa" in html.text
    assert "Capas corporativas publicadas" in html.text
    assert "Visor SIG Corporativo" in html.text
    assert "gisKpiCharts" in html.text
    assert "projectRadar" in html.text
    assert "gisMapSurface" in html.text
    assert "gisServiceSlots" in html.text
    assert "Mapa Administrativo Peru" in html.text
    assert "peruAdministrativeMap" in html.text
    assert "peruRegionList" in html.text
    assert "data-kpi-filter-options=\"produccion,riesgo" in html.text
    assert "publicada por WEB SIG" in html.text
    assert "Mapa Nacional" in html.text
    assert "Mapa Regional" in html.text
    assert "Explorador de Portafolio" in html.text
    assert "Corporate Wizard" in html.text
    assert "Executive Dashboard" in html.text
    assert "Corporate Notifications" in html.text
    assert "/api/v1/audit/events?limit=12" in html.text
    assert "/api/v1/enterprise-wizard" in html.text
    assert "data-gis-filter=\"riesgo\"" in html.text
    assert "data-portfolio-filter=\"contract\"" in html.text
    assert "data-rbac-scope=\"provisioning\"" in html.text
    assert "accessStatus" in html.text
    assert "/api/v1/auth/me" in html.text
    assert "/api/v1/auth/permissions/matrix" in html.text
    assert "Ver detalle accionable" in html.text
    assert "WEB SIG Enterprise" in html.text
    assert "Solo lectura" in html.text
    assert "Flujo Operacional" in html.text
    assert "Modelo Operativo Corporativo" in html.text
    assert "data-theme=\"dark\"" in html.text


def test_corporate_reporting_print_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))
    client.post(
        "/api/v1/companies",
        json={"company_id": "CRTG", "legal_name": "CRTG S.A.C.", "display_name": "CRTG"},
    )
    client.post(
        "/api/v1/companies/CRTG/projects",
        json={
            "project_id": "PSZ-2026",
            "company_id": "CRTG",
            "name": "Proyecto Suiza",
            "country": "PE",
            "region": "Lima",
            "province": "Lima",
            "district": "Miraflores",
            "latitude": -12.1211,
            "longitude": -77.0305,
            "location_source": "portfolio_domain",
            "location_validation_status": "validated",
        },
    )

    templates = client.get("/api/v1/reports/templates")
    preview = client.post("/api/v1/reports/preview", json={"company_id": "CRTG", "requested_by": "cto"})
    issued = client.post("/api/v1/reports/issue", json={"company_id": "CRTG", "requested_by": "cto"})
    html = client.post("/api/v1/reports/issue/html", json={"company_id": "CRTG", "requested_by": "cto"})
    events = client.get("/api/v1/audit/events?limit=20")

    assert templates.status_code == 200
    assert "executive_portfolio" in templates.json()
    assert preview.status_code == 200
    assert preview.json()["manifest"]["status"] == "preview"
    assert issued.status_code == 200
    assert issued.json()["manifest"]["status"] == "issued"
    assert issued.json()["manifest"]["nas_logical_uri"].startswith("nas://CRTG/reports/")
    assert len(issued.json()["manifest"]["checksum_sha256"]) == 64
    assert "Proyecto Suiza" in issued.json()["html"]
    assert "Miraflores" in issued.json()["html"]
    assert html.status_code == 200
    assert "text/html" in html.headers["content-type"]
    assert "Reporte Executive Portfolio" in html.text
    assert "corporate_report.issued" in {event["action"] for event in events.json()}


def test_company_operational_flow_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))
    payload = {
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
        "factory_blueprint": {
            "template_id": "WEB-SIG-ENTERPRISE-REV13",
            "websig_slug": "crtg-psz-2026",
            "websig_url": "https://websig.example.com/crtg/psz-2026",
            "nas_root_uri": "nas://CRTG/PSZ-2026/websig/root",
            "postgis_schema_name": "crtg_psz_2026",
            "geoserver_workspace": "CRTG_PSZ_2026",
        },
        "approved_by": "portfolio-manager",
    }
    client.post("/api/v1/companies/CRTG/websig-factory/execute", json=payload)

    response = client.get("/api/v1/companies/CRTG/operations/flow")

    assert response.status_code == 200
    assert response.json()["company_id"] == "CRTG"
    assert response.json()["summary"]["observed"] == 1
    assert response.json()["items"][0]["current_state"] == "observed"
    assert response.json()["items"][0]["approved_by"] == "portfolio-manager"
    assert response.json()["items"][0]["websig_registered"] is True
    assert response.json()["items"][0]["nas_registered"] is True
    assert response.json()["items"][0]["gis_registered"] is True

    model = client.get("/api/v1/companies/CRTG/operations/model")

    assert model.status_code == 200
    assert model.json()["company_id"] == "CRTG"
    assert model.json()["flow"]["summary"]["observed"] == 1
    assert {lane["lane_id"] for lane in model.json()["lanes"]} >= {
        "intake",
        "provisioning",
        "governance",
        "intelligence",
        "continuity",
    }
    assert {capability["capability_id"] for capability in model.json()["capabilities"]} >= {
        "enterprise-wizard",
        "workflow-engine",
        "portfolio-governance",
        "websig-factory",
    }


def test_corporate_workflow_engine_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))
    client.post(
        "/api/v1/companies",
        json={"company_id": "CRTG", "legal_name": "CRTG S.A.C.", "display_name": "CRTG"},
    )
    client.post(
        "/api/v1/companies/CRTG/projects",
        json={"project_id": "PSZ-2026", "company_id": "CRTG", "name": "Proyecto Suiza"},
    )

    started = client.post(
        "/api/v1/companies/CRTG/workflows/corporate/start",
        json={
            "workflow_id": "CWF-CRTG-PSZ-2026",
            "project_id": "PSZ-2026",
            "actor": "portfolio-manager",
            "reason": "Inicio CTO-101",
        },
    )
    advanced = client.post(
        "/api/v1/companies/CRTG/workflows/corporate/CWF-CRTG-PSZ-2026/advance",
        json={
            "to_stage": "create_program",
            "actor": "portfolio-manager",
            "reason": "Programa creado",
        },
    )
    rejected_skip = client.post(
        "/api/v1/companies/CRTG/workflows/corporate/CWF-CRTG-PSZ-2026/advance",
        json={"to_stage": "provision_websig", "actor": "portfolio-manager"},
    )
    rolled_back = client.post(
        "/api/v1/companies/CRTG/workflows/corporate/CWF-CRTG-PSZ-2026/rollback",
        json={"actor": "portfolio-manager", "reason": "Rollback controlado de prueba"},
    )
    transitions = client.get(
        "/api/v1/companies/CRTG/workflows/corporate/CWF-CRTG-PSZ-2026/transitions"
    )
    audit = client.get("/api/v1/audit/events")

    assert started.status_code == 201
    assert started.json()["current_stage"] == "create_company"
    assert advanced.status_code == 200
    assert advanced.json()["current_stage"] == "create_program"
    assert rejected_skip.status_code == 400
    assert "Next allowed workflow stage" in rejected_skip.json()["detail"]
    assert rolled_back.status_code == 200
    assert rolled_back.json()["current_stage"] == "create_company"
    assert transitions.status_code == 200
    assert transitions.json()[-1]["rollback"] is True
    assert {
        event["action"]
        for event in audit.json()
    } >= {
        "corporate_workflow.transitioned",
        "corporate_workflow.rollback",
    }


def test_enterprise_wizard_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))
    wizard = client.post(
        "/api/v1/enterprise-wizard",
        json={"wizard_id": "WIZ-API-001", "actor": "portfolio-manager"},
    )
    invalid_project = client.post(
        "/api/v1/enterprise-wizard/WIZ-API-001/steps/project/validate",
        json={"data": {"project_id": "PSZ-WIZ"}, "actor": "portfolio-manager"},
    )
    step_payloads = {
        "company": {
            "company_id": "CRTG-WIZ",
            "legal_name": "CRTG Wizard S.A.C.",
            "display_name": "CRTG Wizard",
        },
        "program": {"program_id": "PRG-WIZ", "name": "Programa Wizard"},
        "project": {"project_id": "PSZ-WIZ", "name": "Proyecto Wizard"},
        "location": {
            "country": "PE",
            "region": "Lima",
            "province": "Lima",
            "district": "Miraflores",
            "latitude": -12.1211,
            "longitude": -77.0305,
            "location_source": "enterprise_wizard",
            "location_validation_status": "validated",
        },
        "specialties": {"specialties": ["bim", "gis"]},
        "web_sig": {
            "template_id": "WEB-SIG-ENTERPRISE-REV13",
            "websig_slug": "crtg-wiz-psz",
            "websig_instance_id": "WEB-CRTG-WIZ-PSZ",
            "websig_url": "https://websig.example.com/crtg-wiz/psz",
        },
        "gis": {
            "postgis_schema": "crtg_wiz_psz",
            "geoserver_workspace": "CRTG_WIZ_PSZ",
            "gis_binding_id": "GBD-CRTG-WIZ-PSZ",
        },
        "nas": {
            "nas_root_uri": "nas://CRTG-WIZ/PSZ-WIZ",
            "google_drive_folder_id": "DRIVE-WIZ",
        },
        "users": {
            "users": [
                {
                    "user_id": "USR-WIZ-001",
                    "email": "wizard@example.com",
                    "display_name": "Wizard User",
                    "role": "portfolio_manager",
                }
            ]
        },
        "activation": {"approved_by": "portfolio-manager"},
    }
    saved = None
    for step, data in step_payloads.items():
        saved = client.put(
            f"/api/v1/enterprise-wizard/WIZ-API-001/steps/{step}",
            json={"data": data, "actor": "portfolio-manager"},
        )
        assert saved.status_code == 200

    resumed = client.get("/api/v1/enterprise-wizard/WIZ-API-001")
    activated = client.post(
        "/api/v1/enterprise-wizard/WIZ-API-001/activate",
        json={"actor": "portfolio-manager", "reason": "Activacion Wizard API"},
    )
    project = client.get("/api/v1/companies/CRTG-WIZ/projects/PSZ-WIZ")
    workflow = client.get("/api/v1/companies/CRTG-WIZ/workflows/corporate/CWF-WIZ-API-001")

    assert wizard.status_code == 201
    assert wizard.json()["current_step"] == "company"
    assert invalid_project.status_code == 200
    assert invalid_project.json()["status"] == "invalid"
    assert "name is required" in invalid_project.json()["validation_errors"]
    assert saved is not None
    assert saved.json()["status"] == "ready"
    assert resumed.json()["project_id"] == "PSZ-WIZ"
    assert activated.status_code == 200
    assert activated.json()["status"] == "activated"
    assert activated.json()["workflow_id"] == "CWF-WIZ-API-001"
    assert project.json()["status"] == "active"
    assert project.json()["websig_instance_id"] == "WEB-CRTG-WIZ-PSZ"
    assert project.json()["region"] == "Lima"
    assert project.json()["province"] == "Lima"
    assert project.json()["district"] == "Miraflores"
    assert project.json()["location_validation_status"] == "validated"
    assert workflow.json()["current_stage"] == "activate_project"


def test_corporate_gis_intelligence_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=sqlite_url(tmp_path)))
    client.post(
        "/api/v1/companies",
        json={"company_id": "CRTG", "legal_name": "CRTG S.A.C.", "display_name": "CRTG"},
    )
    client.post(
        "/api/v1/companies/CRTG/portfolio/programs",
        json={"program_id": "PRG-GIS", "company_id": "CRTG", "name": "Programa GIS"},
    )
    client.post(
        "/api/v1/companies/CRTG/projects",
        json={
            "project_id": "PSZ-2026",
            "company_id": "CRTG",
            "program_id": "PRG-GIS",
            "name": "Proyecto Suiza",
            "status": "active",
            "lifecycle_stage": "execution",
            "websig_instance_id": "WEB-CRTG-PSZ-2026",
        },
    )
    source = client.post(
        "/api/v1/companies/CRTG/gis-intelligence/sources",
        json={
            "source_id": "CGIS-SRC-001",
            "company_id": "CRTG",
            "project_id": "PSZ-2026",
            "program_id": "PRG-GIS",
            "websig_instance_id": "WEB-CRTG-PSZ-2026",
            "service_kind": "wms",
            "service_url": "https://websig.example.com/crtg/psz-2026/wms",
            "discipline": "production",
            "layer_type": "physical_progress",
            "status": "active",
            "updated_on": "2026-07-08",
        },
    )
    layer = client.post(
        "/api/v1/companies/CRTG/gis-intelligence/layers",
        json={
            "layer_id": "CGIS-LYR-001",
            "source_id": "CGIS-SRC-001",
            "company_id": "CRTG",
            "project_id": "PSZ-2026",
            "program_id": "PRG-GIS",
            "name": "Avance fisico",
            "layer_type": "physical_progress",
            "discipline": "production",
            "status": "available",
            "spatial_indicator": "physical_progress",
            "indicator_value": 78,
            "updated_on": "2026-07-08",
            "region": "Lima",
        },
    )
    quality_source = client.post(
        "/api/v1/companies/CRTG/gis-intelligence/sources",
        json={
            "source_id": "CGIS-SRC-QUALITY",
            "company_id": "CRTG",
            "project_id": "PSZ-2026",
            "program_id": "PRG-GIS",
            "websig_instance_id": "WEB-CRTG-PSZ-2026",
            "service_kind": "wms",
            "service_url": "https://websig.example.com/crtg/psz-2026/quality/wms",
            "discipline": "quality",
            "layer_type": "quality",
            "status": "active",
            "updated_on": "2026-07-08",
        },
    )
    quality_layer = client.post(
        "/api/v1/companies/CRTG/gis-intelligence/layers",
        json={
            "layer_id": "CGIS-LYR-QUALITY",
            "source_id": "CGIS-SRC-QUALITY",
            "company_id": "CRTG",
            "project_id": "PSZ-2026",
            "program_id": "PRG-GIS",
            "name": "Calidad QA",
            "layer_type": "quality",
            "discipline": "quality",
            "status": "warning",
            "spatial_indicator": "quality",
            "indicator_value": 64,
            "updated_on": "2026-07-08",
            "region": "Lima",
            "risk_level": "medium",
            "metadata": {"calidad": "observed"},
        },
    )
    summary = client.get("/api/v1/companies/CRTG/gis-intelligence/summary")
    corporate_map = client.get("/api/v1/companies/CRTG/gis-intelligence/maps/corporate")
    company_map = client.get("/api/v1/companies/CRTG/gis-intelligence/maps/company")
    regional_map = client.get("/api/v1/companies/CRTG/gis-intelligence/maps/regional/Lima")
    program_map = client.get("/api/v1/companies/CRTG/programs/PRG-GIS/gis-intelligence/maps")
    project_map = client.get("/api/v1/companies/CRTG/projects/PSZ-2026/gis-intelligence/maps")
    thematic_map = client.get("/api/v1/companies/CRTG/gis-intelligence/maps/thematic/calidad")
    business_filter = client.get(
        "/api/v1/companies/CRTG/gis-intelligence/maps/filter",
        params={"estado": "warning", "riesgo": "medium", "calidad": "true"},
    )
    filtered = client.get(
        "/api/v1/companies/CRTG/gis-intelligence/projects/filter",
        params={"indicator": "physical_progress", "minimum_value": 70},
    )
    dashboard = client.get("/api/v1/companies/CRTG/dashboard/executive")

    assert source.status_code == 201
    assert source.json()["service_kind"] == "wms"
    assert layer.status_code == 201
    assert layer.json()["layer_type"] == "physical_progress"
    assert quality_source.status_code == 201
    assert quality_layer.status_code == 201
    assert summary.status_code == 200
    assert summary.json()["total_projects_georeferenced"] == 1
    assert summary.json()["aggregated_spatial_progress"] == 78
    assert corporate_map.json()["layers"][0]["layer_id"] == "CGIS-LYR-001"
    assert company_map.json()["summary"]["projects_with_active_layers"] == 1
    assert regional_map.json()["summary"]["regions"]["Lima"] == 2
    assert program_map.json()["layers"][0]["program_id"] == "PRG-GIS"
    assert project_map.json()["layers"][0]["project_id"] == "PSZ-2026"
    assert thematic_map.json()["layers"][0]["layer_type"] == "quality"
    assert business_filter.json()["layers"][0]["layer_id"] == "CGIS-LYR-QUALITY"
    assert filtered.json()[0]["project_id"] == "PSZ-2026"
    assert dashboard.json()["gis_intelligence"]["projects_with_active_layers"] == 1


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
            "country": None,
            "region": None,
            "province": None,
            "district": None,
            "latitude": None,
            "longitude": None,
            "location_source": None,
            "location_validation_status": None,
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


def test_enterprise_auth_session_contract(tmp_path, monkeypatch) -> None:
    database_url = sqlite_url(tmp_path)
    client = TestClient(create_app(database_url=database_url))
    client.post(
        "/api/v1/companies",
        json={"company_id": "CRTG", "legal_name": "CRTG S.A.C.", "display_name": "CRTG"},
    )
    client.post(
        "/api/v1/users",
        json={"user_id": "USR-001", "email": "admin@example.com", "display_name": "Admin"},
    )
    client.post(
        "/api/v1/companies/CRTG/memberships",
        json={
            "membership_id": "MEM-001",
            "company_id": "CRTG",
            "user_id": "USR-001",
            "role": "portfolio_manager",
        },
    )
    client.post(
        "/api/v1/users/USR-001/auth-identities",
        json={
            "identity_id": "IDP-001",
            "user_id": "USR-001",
            "provider": "oidc",
            "subject": "aad|001",
            "email": "admin@example.com",
        },
    )
    login = client.post("/api/v1/auth/login", json={"provider": "oidc", "subject": "aad|001"})
    token = login.json()["access_token"]
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    logout = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    rejected_me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    assert login.json()["principal"]["user_id"] == "USR-001"
    assert login.json()["principal"]["company_ids"] == ["CRTG"]
    assert "portfolio_manager" in login.json()["claims"]["roles"]
    assert me.status_code == 200
    assert me.headers["X-Authenticated-User"] == "USR-001"
    assert logout.status_code == 200
    assert logout.json()["status"] == "logged_out"
    assert rejected_me.status_code == 401

    monkeypatch.setenv("CONTROL_TOWER_AUTH_REQUIRED", "true")
    monkeypatch.setenv("CONTROL_TOWER_AUTH_SECRET", "test-auth-secret-32-characters")
    protected_client = TestClient(create_app(database_url=database_url))
    unauthorized = protected_client.post(
        "/api/v1/companies",
        json={"company_id": "DENY", "legal_name": "Denied S.A.C.", "display_name": "DENY"},
    )
    health = protected_client.get("/health")

    assert unauthorized.status_code == 401
    assert health.status_code == 200


def test_rbac_blocks_unauthorized_api_action_and_audits(tmp_path, monkeypatch) -> None:
    database_url = sqlite_url(tmp_path)
    seed_client = TestClient(create_app(database_url=database_url))
    seed_client.post(
        "/api/v1/companies",
        json={"company_id": "CRTG", "legal_name": "CRTG S.A.C.", "display_name": "CRTG"},
    )
    seed_client.post(
        "/api/v1/users",
        json={"user_id": "USR-AUD", "email": "audit@example.com", "display_name": "Auditor"},
    )
    seed_client.post(
        "/api/v1/companies/CRTG/memberships",
        json={
            "membership_id": "MEM-AUD",
            "company_id": "CRTG",
            "user_id": "USR-AUD",
            "role": "auditor",
        },
    )
    seed_client.post(
        "/api/v1/users/USR-AUD/auth-identities",
        json={
            "identity_id": "IDP-AUD",
            "user_id": "USR-AUD",
            "provider": "oidc",
            "subject": "aad|audit",
            "email": "audit@example.com",
        },
    )

    monkeypatch.setenv("CONTROL_TOWER_AUTH_REQUIRED", "true")
    monkeypatch.setenv("CONTROL_TOWER_AUTH_SECRET", "test-auth-secret-32-characters")
    client = TestClient(create_app(database_url=database_url))
    login = client.post("/api/v1/auth/login", json={"provider": "oidc", "subject": "aad|audit"})
    token = login.json()["access_token"]
    read = client.get("/api/v1/companies/CRTG/dashboard/executive", headers={"Authorization": f"Bearer {token}"})
    denied = client.post(
        "/api/v1/companies/CRTG/websig-factory/execute",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company": {"company_id": "CRTG", "legal_name": "CRTG S.A.C.", "display_name": "CRTG"},
            "project": {"project_id": "PSZ-2026", "company_id": "CRTG", "name": "Proyecto Suiza"},
            "approved_by": "auditor",
        },
    )
    events = client.get("/api/v1/audit/events?limit=20", headers={"Authorization": f"Bearer {token}"})

    assert read.status_code in {200, 404}
    assert denied.status_code == 403
    assert denied.json()["detail"] == "Permission denied"
    assert "auth.permission.denied" in {event["action"] for event in events.json()}
