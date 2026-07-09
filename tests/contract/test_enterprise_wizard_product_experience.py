from fastapi.testclient import TestClient

from control_tower.api.app import create_app


def test_enterprise_wizard_product_experience_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=f"sqlite:///{tmp_path / 'wizard_product.db'}"))

    html = client.get("/dashboard")

    assert html.status_code == 200
    page = html.text
    for marker in [
        "wizardCommandCenter",
        "wizardProgressBar",
        "wizardResumePanel",
        "wizardStepDetail",
        "wizardValidationPanel",
        "wizardActivationSummary",
        "wizardAuditTrail",
        "Guardar avance",
        "Reanudacion",
        "Resumen antes de activar",
        "Validacion independiente",
        "api/v1/enterprise-wizard",
    ]:
        assert marker in page

    for step in [
        "Empresa",
        "Programa",
        "Proyecto",
        "Ubicacion administrativa",
        "Especialidades",
        "WEB SIG",
        "GIS",
        "NAS",
        "Usuarios",
        "Activacion",
    ]:
        assert step in page

    for trace in ["Workflow", "Portfolio", "GIS", "NAS", "Auditoria", "WEB SIG"]:
        assert trace in page
