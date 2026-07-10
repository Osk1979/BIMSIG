"""Connection Center domain models.

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0021: DevSecOps operating model.
- ADR-0029: Enterprise portal gateway.
- ADR-0030: Connection Center.
"""

from enum import StrEnum

from pydantic import BaseModel, Field

from control_tower.application.infrastructure_connectors import InfrastructureConnectorResult
from control_tower.domain.portal_gateway import PortalGatewayLink


class ConnectionStatus(StrEnum):
    """Normalized status for one enterprise connection."""

    READY = "ready"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


class ConnectionKind(StrEnum):
    """Known connection families governed by the Tower."""

    PORTAL = "portal"
    CONTROL_TOWER = "control_tower"
    WEB_SIG = "web_sig"
    REPORTING = "reporting"
    INFRASTRUCTURE = "infrastructure"


class ConnectionNode(BaseModel):
    """One node in the enterprise connection topology."""

    node_id: str = Field(min_length=3)
    label: str = Field(min_length=3)
    kind: ConnectionKind
    status: ConnectionStatus = ConnectionStatus.READY
    url: str | None = Field(default=None, min_length=6)
    description: str = Field(min_length=10)


class ConnectionEdge(BaseModel):
    """Directed connection between two governed nodes."""

    source: str = Field(min_length=3)
    target: str = Field(min_length=3)
    status: ConnectionStatus = ConnectionStatus.READY
    contract: str = Field(min_length=3)


class ConnectionCenterTopology(BaseModel):
    """Enterprise integration map consumed by operational UIs."""

    revision: str = "REV12"
    nodes: list[ConnectionNode]
    edges: list[ConnectionEdge]
    links: list[PortalGatewayLink]


class ConnectionCenterHealth(BaseModel):
    """Connection Center health and connector readiness."""

    status: ConnectionStatus
    revision: str = "REV12"
    portal_gateway: ConnectionStatus
    infrastructure: ConnectionStatus
    connectors: list[InfrastructureConnectorResult]


class ConnectionCenterReadiness(BaseModel):
    """Company-scoped readiness for Portal, Tower, WEB SIG, and infrastructure."""

    company_id: str = Field(min_length=3)
    status: ConnectionStatus
    topology: ConnectionCenterTopology
    health: ConnectionCenterHealth
