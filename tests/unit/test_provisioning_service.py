import pytest

from control_tower.application.portfolio_service import PortfolioService
from control_tower.application.provisioning_service import ProvisioningService
from control_tower.domain.portfolio import PortfolioProject, ProjectStatus
from control_tower.domain.provisioning import ProvisioningStatus
from tests.unit.fakes import (
    FakeAuditEventRepository,
    FakePortfolioProjectRepository,
    FakeProvisioningRequestRepository,
)


def test_request_websig_requires_registered_project() -> None:
    portfolio = PortfolioService(FakePortfolioProjectRepository())
    provisioning = ProvisioningService(portfolio, FakeProvisioningRequestRepository())

    with pytest.raises(ValueError):
        provisioning.request_websig("MISSING")


def test_request_websig_for_registered_project() -> None:
    portfolio = PortfolioService(FakePortfolioProjectRepository())
    portfolio.register(PortfolioProject(project_id="PSZ-2026", name="Proyecto Suiza"))
    provisioning = ProvisioningService(portfolio, FakeProvisioningRequestRepository(), FakeAuditEventRepository())

    request = provisioning.request_websig("PSZ-2026")

    assert request.project_id == "PSZ-2026"
    assert request.target_revision == "REV12"
    assert request.status == ProvisioningStatus.REQUESTED
    assert portfolio.get_project("PSZ-2026").status == ProjectStatus.PROVISIONING_REQUESTED
