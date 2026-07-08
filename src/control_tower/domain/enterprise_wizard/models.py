"""Enterprise Wizard domain models.

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0025: Corporate Portfolio Domain.
- ADR-0029: Corporate Workflow Engine.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class EnterpriseWizardStep(StrEnum):
    """Official Enterprise Wizard steps."""

    COMPANY = "company"
    PROGRAM = "program"
    PROJECT = "project"
    LOCATION = "location"
    SPECIALTIES = "specialties"
    WEB_SIG = "web_sig"
    GIS = "gis"
    NAS = "nas"
    USERS = "users"
    ACTIVATION = "activation"


class EnterpriseWizardStatus(StrEnum):
    """Lifecycle status for one wizard session."""

    DRAFT = "draft"
    READY = "ready"
    ACTIVATED = "activated"


class EnterpriseWizardStepStatus(StrEnum):
    """Validation status for one wizard step."""

    PENDING = "pending"
    DRAFT = "draft"
    VALID = "valid"
    INVALID = "invalid"


class EnterpriseWizardStepDefinition(BaseModel):
    """Configurable step validation definition."""

    step: EnterpriseWizardStep
    required_fields: list[str] = Field(default_factory=list)


ENTERPRISE_WIZARD_STEPS: tuple[EnterpriseWizardStepDefinition, ...] = (
    EnterpriseWizardStepDefinition(
        step=EnterpriseWizardStep.COMPANY,
        required_fields=["company_id", "legal_name", "display_name"],
    ),
    EnterpriseWizardStepDefinition(
        step=EnterpriseWizardStep.PROGRAM,
        required_fields=["program_id", "name"],
    ),
    EnterpriseWizardStepDefinition(
        step=EnterpriseWizardStep.PROJECT,
        required_fields=["project_id", "name"],
    ),
    EnterpriseWizardStepDefinition(
        step=EnterpriseWizardStep.LOCATION,
        required_fields=[
            "country",
            "region",
            "province",
            "district",
            "latitude",
            "longitude",
            "location_source",
            "location_validation_status",
        ],
    ),
    EnterpriseWizardStepDefinition(
        step=EnterpriseWizardStep.SPECIALTIES,
        required_fields=["specialties"],
    ),
    EnterpriseWizardStepDefinition(
        step=EnterpriseWizardStep.WEB_SIG,
        required_fields=["template_id", "websig_slug"],
    ),
    EnterpriseWizardStepDefinition(
        step=EnterpriseWizardStep.GIS,
        required_fields=["postgis_schema", "geoserver_workspace"],
    ),
    EnterpriseWizardStepDefinition(
        step=EnterpriseWizardStep.NAS,
        required_fields=["nas_root_uri"],
    ),
    EnterpriseWizardStepDefinition(
        step=EnterpriseWizardStep.USERS,
        required_fields=["users"],
    ),
    EnterpriseWizardStepDefinition(
        step=EnterpriseWizardStep.ACTIVATION,
        required_fields=["approved_by"],
    ),
)


class EnterpriseWizardStepState(BaseModel):
    """Persisted partial state for one wizard step."""

    step: EnterpriseWizardStep
    status: EnterpriseWizardStepStatus = EnterpriseWizardStepStatus.PENDING
    data: dict[str, Any] = Field(default_factory=dict)
    validation_errors: list[str] = Field(default_factory=list)
    updated_at: datetime | None = None


class EnterpriseWizardSession(BaseModel):
    """Resumable Enterprise Wizard session."""

    wizard_id: str = Field(min_length=3, examples=["WIZ-001"])
    company_id: str | None = Field(default=None, min_length=3)
    project_id: str | None = Field(default=None, min_length=3)
    workflow_id: str | None = Field(default=None, min_length=3)
    status: EnterpriseWizardStatus = EnterpriseWizardStatus.DRAFT
    current_step: EnterpriseWizardStep = EnterpriseWizardStep.COMPANY
    steps: list[EnterpriseWizardStepState] = Field(default_factory=list)
    created_by: str = Field(default="system", min_length=1)
    updated_by: str = Field(default="system", min_length=1)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class EnterpriseWizardStepSubmission(BaseModel):
    """API payload to save one wizard step."""

    data: dict[str, Any] = Field(default_factory=dict)
    actor: str = Field(default="system", min_length=1)


class EnterpriseWizardActivation(BaseModel):
    """API payload to activate a ready wizard."""

    actor: str = Field(default="system", min_length=1)
    reason: str = Field(default="Enterprise Wizard activation", min_length=3)
