from control_tower.application.portfolio_service import PortfolioService
from control_tower.domain.portfolio import PortfolioProject, ProjectStatus
from tests.unit.fakes import FakeAuditEventRepository, FakePortfolioProjectRepository


def test_register_project_keeps_portfolio_identity() -> None:
    audit = FakeAuditEventRepository()
    service = PortfolioService(FakePortfolioProjectRepository(), audit)
    project = PortfolioProject(
        project_id="PSZ-2026",
        company_id="CRTG",
        name="Proyecto Suiza",
        cui="CUI 2661613",
    )

    registered = service.register(project)

    assert registered.project_id == "PSZ-2026"
    assert registered.status == ProjectStatus.REGISTERED
    assert service.exists("PSZ-2026")
    assert audit.events[0].action == "project.registered"


def test_change_project_status() -> None:
    service = PortfolioService(FakePortfolioProjectRepository(), FakeAuditEventRepository())
    service.register(PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"))

    updated = service.change_status("PSZ-2026", ProjectStatus.ACTIVE)

    assert updated.status == ProjectStatus.ACTIVE


def test_list_projects_for_company_only_returns_tenant_projects() -> None:
    service = PortfolioService(FakePortfolioProjectRepository())
    service.register(PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"))
    service.register(PortfolioProject(project_id="OTHER-2026", company_id="OTHER", name="Other Project"))

    projects = service.list_projects_for_company("CRTG")

    assert [project.project_id for project in projects] == ["PSZ-2026"]
