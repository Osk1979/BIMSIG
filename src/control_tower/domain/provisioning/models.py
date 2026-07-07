"""WEB SIG provisioning domain model.

ADR references:
- ADR-0001: REV11 architecture baseline.
- ADR-0003: Project provisioning as a port.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class ProvisioningStatus(StrEnum):
    """Lifecycle status for a WEB SIG provisioning request."""

    REQUESTED = "requested"
    APPROVED = "approved"
    PROVISIONED = "provisioned"
    FAILED = "failed"


class ProvisioningRequest(BaseModel):
    """Intent to create a dedicated WEB SIG for a portfolio project."""

    request_id: str = Field(min_length=3)
    project_id: str = Field(min_length=3)
    target_revision: str = Field(default="REV12")
    status: ProvisioningStatus = ProvisioningStatus.REQUESTED
