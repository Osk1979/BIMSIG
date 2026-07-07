"""Portfolio project domain model.

ADR references:
- ADR-0001: REV11 architecture baseline.
- ADR-0002: Layered modular API scaffold.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class ProjectStatus(StrEnum):
    """Governance status for a portfolio project."""

    REGISTERED = "registered"
    PROVISIONING_REQUESTED = "provisioning_requested"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class PortfolioProject(BaseModel):
    """Project registered at Corporate Control Tower portfolio level."""

    project_id: str = Field(min_length=3, examples=["PSZ-2026"])
    name: str = Field(min_length=3, examples=["Proyecto Suiza"])
    cui: str | None = Field(default=None, examples=["CUI 2661613"])
    status: ProjectStatus = ProjectStatus.REGISTERED
