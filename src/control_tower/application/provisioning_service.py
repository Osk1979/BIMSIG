"""Provisioning application service.

ADR references:
- ADR-0001: REV11 architecture baseline.
- ADR-0003: Project provisioning as a port.
"""

from uuid import uuid4

from control_tower.domain.provisioning import ProvisioningRequest

from .portfolio_service import PortfolioService


class ProvisioningService:
    """Coordinates WEB SIG provisioning requests for registered projects."""

    def __init__(self, portfolio: PortfolioService) -> None:
        self._portfolio = portfolio
        self._requests: dict[str, ProvisioningRequest] = {}

    def request_websig(self, project_id: str) -> ProvisioningRequest:
        """Create a WEB SIG provisioning request for a registered project."""

        if not self._portfolio.exists(project_id):
            raise ValueError(f"Project is not registered: {project_id}")
        request = ProvisioningRequest(request_id=f"PPE-{uuid4().hex[:12]}", project_id=project_id)
        self._requests[request.request_id] = request
        return request
