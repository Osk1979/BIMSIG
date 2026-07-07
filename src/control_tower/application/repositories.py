"""Repository ports for durable Corporate Control Tower state.

ADR references:
- ADR-0002: Layered modular API scaffold.
- ADR-0005: Persistence strategy.
- ADR-0013: Database schema and migrations.
"""

from typing import Protocol

from control_tower.domain.audit import AuditEvent
from control_tower.domain.portfolio import PortfolioProject
from control_tower.domain.provisioning import ProvisioningRequest


class PortfolioProjectRepository(Protocol):
    """Persistence port for portfolio projects."""

    def save(self, project: PortfolioProject) -> PortfolioProject:
        """Persist a portfolio project."""

    def list(self) -> list[PortfolioProject]:
        """Return all persisted portfolio projects."""

    def get(self, project_id: str) -> PortfolioProject | None:
        """Return one persisted project when it exists."""

    def exists(self, project_id: str) -> bool:
        """Return whether a project exists."""


class ProvisioningRequestRepository(Protocol):
    """Persistence port for WEB SIG provisioning requests."""

    def save(self, request: ProvisioningRequest) -> ProvisioningRequest:
        """Persist a provisioning request."""

    def list(self) -> list[ProvisioningRequest]:
        """Return all persisted provisioning requests."""


class AuditEventRepository(Protocol):
    """Persistence port for audit events."""

    def save(self, event: AuditEvent) -> AuditEvent:
        """Persist an audit event."""

    def list(self, limit: int = 100) -> list[AuditEvent]:
        """Return recent audit events."""
