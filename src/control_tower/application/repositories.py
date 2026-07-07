"""Repository ports for durable Corporate Control Tower state.

ADR references:
- ADR-0002: Layered modular API scaffold.
- ADR-0005: Persistence strategy.
- ADR-0013: Database schema and migrations.
"""

from typing import Protocol

from control_tower.domain.portfolio import PortfolioProject
from control_tower.domain.provisioning import ProvisioningRequest


class PortfolioProjectRepository(Protocol):
    """Persistence port for portfolio projects."""

    def save(self, project: PortfolioProject) -> PortfolioProject:
        """Persist a portfolio project."""

    def list(self) -> list[PortfolioProject]:
        """Return all persisted portfolio projects."""

    def exists(self, project_id: str) -> bool:
        """Return whether a project exists."""


class ProvisioningRequestRepository(Protocol):
    """Persistence port for WEB SIG provisioning requests."""

    def save(self, request: ProvisioningRequest) -> ProvisioningRequest:
        """Persist a provisioning request."""
