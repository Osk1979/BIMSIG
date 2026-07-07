"""Provisioning application service.

ADR references:
- ADR-0001: REV11 architecture baseline.
- ADR-0003: Project provisioning as a port.
- ADR-0005: Persistence strategy.
"""

from uuid import uuid4

from control_tower.domain.audit import AuditEvent
from control_tower.domain.portfolio import ProjectStatus
from control_tower.domain.provisioning import ProvisioningRequest

from .portfolio_service import PortfolioService
from .repositories import AuditEventRepository, ProvisioningRequestRepository


class ProvisioningService:
    """Coordinates WEB SIG provisioning requests for registered projects."""

    def __init__(
        self,
        portfolio: PortfolioService,
        repository: ProvisioningRequestRepository,
        audit_repository: AuditEventRepository | None = None,
    ) -> None:
        self._portfolio = portfolio
        self._repository = repository
        self._audit_repository = audit_repository

    def request_websig(self, project_id: str) -> ProvisioningRequest:
        """Create a WEB SIG provisioning request for a registered project."""

        if not self._portfolio.exists(project_id):
            raise ValueError(f"Project is not registered: {project_id}")
        request = ProvisioningRequest(request_id=f"PPE-{uuid4().hex[:12]}", project_id=project_id)
        saved = self._repository.save(request)
        self._portfolio.change_status(project_id, ProjectStatus.PROVISIONING_REQUESTED)
        self._audit(
            action="provisioning.websig_requested",
            entity_id=saved.request_id,
            detail=f"WEB SIG provisioning requested for project {saved.project_id}.",
        )
        return saved

    def list_requests(self) -> list[ProvisioningRequest]:
        """Return all WEB SIG provisioning requests."""

        return self._repository.list()

    def _audit(self, action: str, entity_id: str, detail: str) -> None:
        if self._audit_repository is None:
            return
        self._audit_repository.save(
            AuditEvent(
                actor="system",
                action=action,
                entity_type="provisioning_request",
                entity_id=entity_id,
                detail=detail,
            )
        )
