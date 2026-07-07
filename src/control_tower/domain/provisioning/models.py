"""WEB SIG provisioning domain model.

ADR references:
- ADR-0001: REV11 architecture baseline.
- ADR-0003: Project provisioning as a port.
- ADR-0007: NAS integration.
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0014: Enterprise multitenancy.
- ADR-0015: Tower vs WEB SIG operational boundary.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class ProvisioningStatus(StrEnum):
    """Lifecycle status for a WEB SIG provisioning request."""

    REQUESTED = "requested"
    APPROVED = "approved"
    PROVISIONED = "provisioned"
    FAILED = "failed"


class ProvisioningOperation(StrEnum):
    """Supported provisioning orchestration operations."""

    WEB_SIG = "websig"
    PROJECT_STACK = "project_stack"


class ProvisioningStepStatus(StrEnum):
    """Lifecycle status for one provisioning step."""

    PLANNED = "planned"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ProvisioningResourceType(StrEnum):
    """Resource classes created or registered by Project Provisioning Engine."""

    COMPANY = "company"
    PROJECT = "project"
    WEB_SIG = "websig"
    POSTGIS = "postgis"
    NAS = "nas"
    DOCUMENT_STRUCTURE = "document_structure"
    GEOSERVER = "geoserver"
    DASHBOARD = "dashboard"
    USER = "user"
    ROLE = "role"
    CATALOG = "catalog"


class ProvisioningStep(BaseModel):
    """Auditable step produced by Project Provisioning Engine."""

    step_id: str = Field(min_length=3)
    resource_type: ProvisioningResourceType
    name: str = Field(min_length=3)
    status: ProvisioningStepStatus = ProvisioningStepStatus.SUCCEEDED
    reference: str | None = None


class ProvisioningRequest(BaseModel):
    """Intent to create a dedicated WEB SIG for a portfolio project."""

    request_id: str = Field(min_length=3)
    project_id: str = Field(min_length=3)
    company_id: str | None = Field(default=None, min_length=3)
    target_revision: str = Field(default="REV12")
    status: ProvisioningStatus = ProvisioningStatus.REQUESTED
    operation: ProvisioningOperation = ProvisioningOperation.WEB_SIG
    steps: list[ProvisioningStep] = Field(default_factory=list)
