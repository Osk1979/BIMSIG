"""Operational flow domain models.

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0025: Corporate Portfolio Domain.
- ADR-0026: WEB SIG Factory controlled provisioning.
- ADR-0027: Corporate Control Tower operational flow.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class OperationalPhase(StrEnum):
    """Formal phases in the Corporate Control Tower operational flow."""

    INTAKE = "intake"
    GOVERNANCE_QUALIFICATION = "governance_qualification"
    PORTFOLIO_LIFECYCLE = "portfolio_lifecycle"
    FACTORY_DRY_RUN = "factory_dry_run"
    APPROVAL_GATE = "approval_gate"
    CONTROLLED_EXECUTION = "controlled_execution"
    REFERENCE_REGISTRATION = "reference_registration"
    DASHBOARD_PUBLICATION = "dashboard_publication"
    AUDIT_MONITORING = "audit_monitoring"
    CONTINUITY_BACKUP = "continuity_backup"


class OperationalState(StrEnum):
    """Corporate operational state derived from governed references."""

    INTAKE = "intake"
    QUALIFIED = "qualified"
    PLANNED = "planned"
    APPROVED = "approved"
    PROVISIONED = "provisioned"
    OBSERVED = "observed"
    ARCHIVED = "archived"


class OperationalFlowItem(BaseModel):
    """Operational flow status for one governed project."""

    project_id: str = Field(min_length=3)
    project_name: str = Field(min_length=3)
    company_id: str = Field(min_length=3)
    current_state: OperationalState
    active_phase: OperationalPhase
    completed_phases: list[OperationalPhase] = Field(default_factory=list)
    pending_controls: list[str] = Field(default_factory=list)
    next_action: str = Field(min_length=3)
    readiness_score: int = Field(ge=0, le=100)
    websig_registered: bool = False
    nas_registered: bool = False
    gis_registered: bool = False
    provisioning_requests: int = Field(ge=0)
    approved_by: str | None = None


class OperationalFlowSummary(BaseModel):
    """Company-level operational flow counters."""

    total_projects: int = Field(ge=0)
    intake: int = Field(ge=0)
    qualified: int = Field(ge=0)
    planned: int = Field(ge=0)
    approved: int = Field(ge=0)
    provisioned: int = Field(ge=0)
    observed: int = Field(ge=0)
    archived: int = Field(ge=0)
    average_readiness: int = Field(ge=0, le=100)


class CompanyOperationalFlow(BaseModel):
    """Company-scoped operational flow read model."""

    company_id: str = Field(min_length=3)
    summary: OperationalFlowSummary
    items: list[OperationalFlowItem] = Field(default_factory=list)
