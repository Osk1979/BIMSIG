"""Portfolio project domain model.

ADR references:
- ADR-0001: REV11 architecture baseline.
- ADR-0002: Layered modular API scaffold.
- ADR-0009: GeoServer integration.
- ADR-0010: Google Workspace transition integration.
- ADR-0014: Enterprise multitenancy.
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0024: REV13 corporate governance baseline.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class ProjectStatus(StrEnum):
    """Governance status for a portfolio project."""

    REGISTERED = "registered"
    PROVISIONING_REQUESTED = "provisioning_requested"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class ProjectLifecycleStage(StrEnum):
    """Corporate lifecycle stage governed by the Tower."""

    INTAKE = "intake"
    PLANNING = "planning"
    PROVISIONING = "provisioning"
    EXECUTION = "execution"
    CLOSURE = "closure"
    ARCHIVED = "archived"


class CustomerStatus(StrEnum):
    """Lifecycle status for a corporate customer record."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class ProgramStatus(StrEnum):
    """Governance status for a corporate program."""

    PLANNED = "planned"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class CorporateCustomer(BaseModel):
    """Client governed by the Corporate Control Tower portfolio domain."""

    customer_id: str = Field(min_length=3, examples=["CLI-MTC"])
    company_id: str = Field(min_length=3, examples=["CRTG"])
    legal_name: str = Field(min_length=3, examples=["Ministerio de Transportes"])
    display_name: str = Field(min_length=3, examples=["MTC"])
    tax_id: str | None = Field(default=None, examples=["20131379944"])
    status: CustomerStatus = CustomerStatus.ACTIVE


class CorporateProgram(BaseModel):
    """Program that groups multiple projects for corporate governance."""

    program_id: str = Field(min_length=3, examples=["PRG-TRANSPORTE-2026"])
    company_id: str = Field(min_length=3, examples=["CRTG"])
    customer_id: str | None = Field(default=None, min_length=3, examples=["CLI-MTC"])
    name: str = Field(min_length=3, examples=["Programa Transporte 2026"])
    status: ProgramStatus = ProgramStatus.PLANNED


class PortfolioProject(BaseModel):
    """Project registered at Corporate Control Tower portfolio level."""

    project_id: str = Field(min_length=3, examples=["PSZ-2026"])
    company_id: str = Field(min_length=3, examples=["CRTG"])
    name: str = Field(min_length=3, examples=["Proyecto Suiza"])
    cui: str | None = Field(default=None, examples=["CUI 2661613"])
    customer_id: str | None = Field(default=None, min_length=3, examples=["CLI-MTC"])
    program_id: str | None = Field(default=None, min_length=3, examples=["PRG-TRANSPORTE-2026"])
    status: ProjectStatus = ProjectStatus.REGISTERED
    lifecycle_stage: ProjectLifecycleStage = ProjectLifecycleStage.INTAKE
    websig_instance_id: str | None = Field(default=None, min_length=3, examples=["WEB-PSZ-2026"])
    websig_url: str | None = Field(default=None, min_length=6, examples=["https://websig.example.com/psz"])
    nas_root_uri: str | None = Field(default=None, min_length=6, examples=["nas://CRTG/PSZ-2026"])
    gis_binding_id: str | None = Field(default=None, min_length=3, examples=["GBD-001"])
    google_drive_folder_id: str | None = Field(default=None, min_length=3, examples=["drive-folder-id"])
    country: str | None = Field(default=None, min_length=2, examples=["PE"])
    region: str | None = Field(default=None, min_length=2, examples=["Lima"])
    province: str | None = Field(default=None, min_length=2, examples=["Lima"])
    district: str | None = Field(default=None, min_length=2, examples=["Miraflores"])
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    location_source: str | None = Field(default=None, min_length=3, examples=["enterprise_wizard"])
    location_validation_status: str | None = Field(default=None, min_length=3, examples=["validated"])


class PortfolioLifecycleTransition(BaseModel):
    """Allowed corporate lifecycle transition request."""

    lifecycle_stage: ProjectLifecycleStage
    status: ProjectStatus | None = None


class ProjectIntegrationSummary(BaseModel):
    """Read model for project integrations governed by the Tower."""

    websig_instance_id: str | None = None
    websig_url: str | None = None
    nas_root_uri: str | None = None
    gis_binding_id: str | None = None
    google_drive_folder_id: str | None = None
    provisioning_requests: int = 0
    nas_assets: int = 0
    gis_layers: int = 0


class CorporatePortfolioProjectView(BaseModel):
    """Integrated governance view for one project without operating WEB SIG."""

    project: PortfolioProject
    customer: CorporateCustomer | None = None
    program: CorporateProgram | None = None
    integrations: ProjectIntegrationSummary
