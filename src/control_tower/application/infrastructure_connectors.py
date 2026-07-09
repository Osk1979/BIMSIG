"""Controlled infrastructure connector service.

ADR references:
- ADR-0007: NAS integration.
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0010: Google Workspace transition integration.
- ADR-0021: DevSecOps operating model.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, Field

from control_tower.domain.audit import AuditEvent

from .repositories import AuditEventRepository


class InfrastructureConnectorKind(StrEnum):
    """External infrastructure connectors governed by the Tower."""

    POSTGIS = "postgis"
    GEOSERVER = "geoserver"
    NAS = "nas"
    GOOGLE_DRIVE = "google_drive"


class InfrastructureConnectorAction(StrEnum):
    """Controlled action supported by infrastructure connectors."""

    HEALTH = "health"
    VALIDATE = "validate"
    DRY_RUN = "dry_run"
    EXECUTE = "execute"


class InfrastructureConnectorStatus(StrEnum):
    """Result status for one connector operation."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    CONFIGURED = "configured"
    MISCONFIGURED = "misconfigured"
    PLANNED = "planned"
    EXECUTED = "executed"
    FAILED = "failed"


class InfrastructureConnectorRequest(BaseModel):
    """Controlled request for an external infrastructure connector."""

    action: InfrastructureConnectorAction = InfrastructureConnectorAction.HEALTH
    company_id: str | None = Field(default=None, min_length=3)
    project_id: str | None = Field(default=None, min_length=3)
    target: dict[str, str] = Field(default_factory=dict)
    approved_by: str | None = Field(default=None, min_length=3)


class InfrastructureConnectorResult(BaseModel):
    """Auditable connector result without secret values."""

    connector: InfrastructureConnectorKind
    action: InfrastructureConnectorAction
    status: InfrastructureConnectorStatus
    configured: bool
    reference: str | None = None
    detail: str
    metadata: dict[str, str] = Field(default_factory=dict)


class InfrastructureConnector(Protocol):
    """Port implemented by real infrastructure connector adapters."""

    kind: InfrastructureConnectorKind

    def health(self) -> InfrastructureConnectorResult:
        """Check connector health."""

    def validate(self) -> InfrastructureConnectorResult:
        """Validate connector configuration without side effects."""

    def dry_run(self, request: InfrastructureConnectorRequest) -> InfrastructureConnectorResult:
        """Plan a controlled connector operation without side effects."""

    def execute(self, request: InfrastructureConnectorRequest) -> InfrastructureConnectorResult:
        """Execute a controlled connector operation."""


class InfrastructureConnectorService:
    """Coordinates controlled checks and actions across infrastructure connectors."""

    def __init__(
        self,
        connectors: list[InfrastructureConnector],
        audit_repository: AuditEventRepository | None = None,
    ) -> None:
        self._connectors = {connector.kind: connector for connector in connectors}
        self._audit_repository = audit_repository

    def health(self) -> list[InfrastructureConnectorResult]:
        """Return health for all configured connector slots."""

        return [connector.health() for connector in self._connectors.values()]

    def run(
        self,
        connector_kind: InfrastructureConnectorKind,
        request: InfrastructureConnectorRequest,
        actor: str = "system",
    ) -> InfrastructureConnectorResult:
        """Run one controlled connector action and audit the result."""

        connector = self._connectors.get(connector_kind)
        if connector is None:
            raise ValueError(f"Infrastructure connector is not registered: {connector_kind}")
        result = self._dispatch(connector, request)
        self._audit(actor, result, request)
        return result

    @staticmethod
    def _dispatch(
        connector: InfrastructureConnector,
        request: InfrastructureConnectorRequest,
    ) -> InfrastructureConnectorResult:
        if request.action == InfrastructureConnectorAction.HEALTH:
            return connector.health()
        if request.action == InfrastructureConnectorAction.VALIDATE:
            return connector.validate()
        if request.action == InfrastructureConnectorAction.DRY_RUN:
            return connector.dry_run(request)
        if request.action == InfrastructureConnectorAction.EXECUTE:
            if request.approved_by is None:
                return InfrastructureConnectorResult(
                    connector=connector.kind,
                    action=request.action,
                    status=InfrastructureConnectorStatus.FAILED,
                    configured=True,
                    detail="Controlled execute requires approved_by.",
                )
            return connector.execute(request)
        raise ValueError(f"Unsupported connector action: {request.action}")

    def _audit(
        self,
        actor: str,
        result: InfrastructureConnectorResult,
        request: InfrastructureConnectorRequest,
    ) -> None:
        if self._audit_repository is None:
            return
        scope = "/".join(part for part in [request.company_id, request.project_id] if part)
        self._audit_repository.save(
            AuditEvent(
                actor=actor,
                action=f"infrastructure.{result.connector.value}.{result.action.value}",
                entity_type="infrastructure_connector",
                entity_id=scope or result.connector.value,
                detail=f"{result.status.value}: {result.detail}",
            )
        )
