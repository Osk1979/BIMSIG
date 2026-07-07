import pytest

from control_tower.application.portfolio_service import PortfolioService
from control_tower.application.provisioning_service import ProvisioningService
from control_tower.domain.portfolio import PortfolioProject
from control_tower.domain.provisioning import ProvisioningStatus


def test_request_websig_requires_registered_project() -> None:
    portfolio = PortfolioService()
    provisioning = ProvisioningService(portfolio)

    with pytest.raises(ValueError):
        provisioning.request_websig("MISSING")


def test_request_websig_for_registered_project() -> None:
    portfolio = PortfolioService()
    portfolio.register(PortfolioProject(project_id="PSZ-2026", name="Proyecto Suiza"))
    provisioning = ProvisioningService(portfolio)

    request = provisioning.request_websig("PSZ-2026")

    assert request.project_id == "PSZ-2026"
    assert request.target_revision == "REV12"
    assert request.status == ProvisioningStatus.REQUESTED
