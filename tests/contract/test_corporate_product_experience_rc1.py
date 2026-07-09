from fastapi.testclient import TestClient

from control_tower.api.app import create_app


def test_corporate_product_experience_rc1_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=f"sqlite:///{tmp_path / 'rc1.db'}"))

    html = client.get("/dashboard")

    assert html.status_code == 200
    page = html.text
    for marker in [
        "Corporate Control Tower REV13 RC1",
        "corporateHome",
        "corporateDashboard",
        "portfolioExplorer",
        "portfolioOrganizationTree",
        "corporateGisDashboard",
        "projectRadar",
        "gisMapSurface",
        "enterpriseWizard",
        "wizardCommandCenter",
        "corporateReporting",
        "reportingPreview",
        "corporateNotifications",
        "data-rbac-scope",
        'data-theme="dark"',
        "Light Mode",
    ]:
        assert marker in page

    for navigation in [
        'href="#corporateHome"',
        'href="#portfolioExplorer"',
        'href="#corporateGisDashboard"',
        'href="#enterpriseWizard"',
        'href="#corporateReporting"',
        'href="#corporateNotifications"',
    ]:
        assert navigation in page

    assert "Configuracion" not in page
    assert ">Administracion<" not in page
