"""Deployment Target Manager domain models.

ADR references:
- ADR-0011: Deployment strategy.
- ADR-0021: DevSecOps operating model.
- ADR-0031: Deployment Target Manager.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class DeploymentTargetType(StrEnum):
    """Supported backend runtime target families."""

    LOCAL_DOCKER = "local_docker"
    VPS = "vps"
    CLOUD_CONTAINER = "cloud_container"
    TEMPORARY_TUNNEL = "temporary_tunnel"
    PENDING = "pending"


class DeploymentTargetStatus(StrEnum):
    """Governed status for one deployment target."""

    VALIDATED = "validated"
    DEGRADED = "degraded"
    NOT_CONFIGURED = "not_configured"
    UNREACHABLE = "unreachable"


class DeploymentTarget(BaseModel):
    """One selectable backend target for the Corporate Control Tower API."""

    target_id: str = Field(min_length=3)
    label: str = Field(min_length=3)
    target_type: DeploymentTargetType
    backend_url: str | None = Field(default=None, min_length=6)
    public: bool = False
    active: bool = False
    status: DeploymentTargetStatus = DeploymentTargetStatus.NOT_CONFIGURED
    description: str = Field(min_length=10)
    health_endpoints: list[str] = Field(default_factory=list)
    last_validated_at: datetime | None = None


class DeploymentTargetCatalog(BaseModel):
    """Deployment target catalog exposed to operators and UI surfaces."""

    revision: str = "REV12"
    active_target_id: str
    targets: list[DeploymentTarget]


class DeploymentTargetActivation(BaseModel):
    """Request to activate one known deployment target."""

    activated_by: str = Field(default="system", min_length=1)
    reason: str = Field(default="Deployment target selected", min_length=3)


class DeploymentTargetCheck(BaseModel):
    """One endpoint validation check."""

    endpoint: str = Field(min_length=1)
    status: DeploymentTargetStatus
    status_code: int | None = Field(default=None, ge=100, le=599)
    detail: str = Field(min_length=1)


class DeploymentTargetValidation(BaseModel):
    """Validation result for one deployment target."""

    target_id: str = Field(min_length=3)
    backend_url: str | None = Field(default=None, min_length=6)
    status: DeploymentTargetStatus
    checked_at: datetime
    checks: list[DeploymentTargetCheck]
