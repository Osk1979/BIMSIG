"""Corporate Workflow Engine domain models.

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0017: Project Provisioning Engine.
- ADR-0025: Corporate Portfolio Domain.
- ADR-0027: Corporate Control Tower operational flow.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class CorporateWorkflowStage(StrEnum):
    """Official corporate workflow stages governed by the Tower."""

    CREATE_COMPANY = "create_company"
    CREATE_PROGRAM = "create_program"
    CREATE_PROJECT = "create_project"
    PROVISION_WEB_SIG = "provision_websig"
    CREATE_NAS = "create_nas"
    CREATE_POSTGIS = "create_postgis"
    REGISTER_GEOSERVER = "register_geoserver"
    CREATE_DASHBOARD = "create_dashboard"
    ASSIGN_USERS = "assign_users"
    ASSIGN_SPECIALTIES = "assign_specialties"
    ACTIVATE_PROJECT = "activate_project"
    OPERATION = "operation"
    CLOSURE = "closure"
    ARCHIVE = "archive"


OFFICIAL_WORKFLOW_SEQUENCE: tuple[CorporateWorkflowStage, ...] = (
    CorporateWorkflowStage.CREATE_COMPANY,
    CorporateWorkflowStage.CREATE_PROGRAM,
    CorporateWorkflowStage.CREATE_PROJECT,
    CorporateWorkflowStage.PROVISION_WEB_SIG,
    CorporateWorkflowStage.CREATE_NAS,
    CorporateWorkflowStage.CREATE_POSTGIS,
    CorporateWorkflowStage.REGISTER_GEOSERVER,
    CorporateWorkflowStage.CREATE_DASHBOARD,
    CorporateWorkflowStage.ASSIGN_USERS,
    CorporateWorkflowStage.ASSIGN_SPECIALTIES,
    CorporateWorkflowStage.ACTIVATE_PROJECT,
    CorporateWorkflowStage.OPERATION,
    CorporateWorkflowStage.CLOSURE,
    CorporateWorkflowStage.ARCHIVE,
)


class CorporateWorkflowStatus(StrEnum):
    """Lifecycle status for a corporate workflow instance."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"


class CorporateWorkflowInstance(BaseModel):
    """Company-scoped corporate workflow state."""

    workflow_id: str = Field(min_length=3, examples=["CWF-001"])
    company_id: str = Field(min_length=3, examples=["CRTG"])
    project_id: str | None = Field(default=None, min_length=3, examples=["PSZ-2026"])
    program_id: str | None = Field(default=None, min_length=3)
    current_stage: CorporateWorkflowStage
    status: CorporateWorkflowStatus = CorporateWorkflowStatus.ACTIVE
    completed_stages: list[CorporateWorkflowStage] = Field(default_factory=list)
    rollback_available: bool = True
    created_by: str = Field(default="system", min_length=1)
    updated_by: str = Field(default="system", min_length=1)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CorporateWorkflowTransition(BaseModel):
    """Auditable transition inside one corporate workflow."""

    transition_id: str = Field(min_length=3, examples=["CWFT-001"])
    workflow_id: str = Field(min_length=3)
    company_id: str = Field(min_length=3)
    project_id: str | None = Field(default=None, min_length=3)
    from_stage: CorporateWorkflowStage | None = None
    to_stage: CorporateWorkflowStage
    actor: str = Field(min_length=1)
    reason: str = Field(min_length=3)
    rollback: bool = False
    rollback_of: str | None = Field(default=None, min_length=3)
    created_at: datetime | None = None


class CorporateWorkflowAdvance(BaseModel):
    """API payload to advance one corporate workflow."""

    to_stage: CorporateWorkflowStage
    actor: str = Field(default="system", min_length=1)
    reason: str = Field(default="Corporate workflow transition", min_length=3)


class CorporateWorkflowRollback(BaseModel):
    """API payload to perform controlled rollback."""

    actor: str = Field(default="system", min_length=1)
    reason: str = Field(default="Controlled rollback", min_length=3)
