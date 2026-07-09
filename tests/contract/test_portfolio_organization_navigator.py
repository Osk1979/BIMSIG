from fastapi.testclient import TestClient

from control_tower.api.app import create_app


def test_portfolio_organization_navigator_contract(tmp_path) -> None:
    client = TestClient(create_app(database_url=f"sqlite:///{tmp_path / 'portfolio_nav.db'}"))

    html = client.get("/dashboard")

    assert html.status_code == 200
    page = html.text
    for marker in [
        "portfolioSearch",
        "portfolioOrganizationTree",
        "portfolioProjectDetail",
        "portfolio-navigator",
        "portfolioDecision",
        "Empresa / Programa / Proyecto / WEB SIG / Estado / Dashboard",
        "Decision operativa",
        "Dashboard",
        "GIS",
        "NAS",
        "Reportes",
        "Auditoria",
        "Wizard",
    ]:
        assert marker in page

    for filter_name in ["all", "active", "websig", "attention"]:
        assert f'data-portfolio-filter="{filter_name}"' in page
