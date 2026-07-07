from control_tower.application.portfolio_service import PortfolioService
from control_tower.domain.portfolio import PortfolioProject, ProjectStatus
from tests.unit.fakes import FakePortfolioProjectRepository


def test_register_project_keeps_portfolio_identity() -> None:
    service = PortfolioService(FakePortfolioProjectRepository())
    project = PortfolioProject(project_id="PSZ-2026", name="Proyecto Suiza", cui="CUI 2661613")

    registered = service.register(project)

    assert registered.project_id == "PSZ-2026"
    assert registered.status == ProjectStatus.REGISTERED
    assert service.exists("PSZ-2026")
