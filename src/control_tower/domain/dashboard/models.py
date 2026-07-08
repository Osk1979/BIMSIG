"""Executive dashboard domain models.

ADR references:
- ADR-0014: Enterprise multitenancy.
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0016: Enterprise licensing.
- ADR-0018: Corporate executive dashboard.
- ADR-0025: Corporate Portfolio Domain.
- ADR-0027: Corporate Control Tower operational flow.
"""

from pydantic import BaseModel, Field

from control_tower.domain.corporate_gis_intelligence import CorporateGisSummary
from control_tower.domain.operations import CorporateOperatingModel, OperationalFlowItem


class DashboardMetric(BaseModel):
    """Single executive dashboard metric."""

    metric_id: str = Field(min_length=3)
    label: str = Field(min_length=3)
    value: str = Field(min_length=1)
    status: str = Field(default="nominal")
    trend: str = Field(default="stable")


class CorporateMapPoint(BaseModel):
    """Portfolio map point used by the corporate dashboard."""

    project_id: str = Field(min_length=3)
    name: str = Field(min_length=3)
    status: str = Field(min_length=3)
    latitude: float
    longitude: float
    country: str | None = None
    region: str | None = None
    province: str | None = None
    district: str | None = None
    location_source: str | None = None
    location_validation_status: str | None = None


class ProjectComparison(BaseModel):
    """Comparable portfolio row between projects."""

    project_id: str = Field(min_length=3)
    name: str = Field(min_length=3)
    governance_status: str = Field(min_length=3)
    kpi_score: int = Field(ge=0, le=100)
    production_score: int = Field(ge=0, le=100)
    schedule_score: int = Field(ge=0, le=100)
    risk_score: int = Field(ge=0, le=100)


class PortfolioGovernanceItem(BaseModel):
    """Project-level portfolio governance summary for the executive dashboard."""

    project_id: str = Field(min_length=3)
    project_name: str = Field(min_length=3)
    customer: str | None = None
    program: str | None = None
    lifecycle_stage: str = Field(min_length=3)
    governance_status: str = Field(min_length=3)
    websig: str = Field(min_length=1)
    nas: str = Field(min_length=1)
    gis: str = Field(min_length=1)
    provisioning_requests: int = Field(ge=0)
    nas_assets: int = Field(ge=0)
    gis_layers: int = Field(ge=0)


class CorporateDashboard(BaseModel):
    """Executive read model for one enterprise company."""

    company_id: str = Field(min_length=3)
    portfolio: dict[str, int]
    map_points: list[CorporateMapPoint]
    kpis: list[DashboardMetric]
    risks: list[DashboardMetric]
    production: list[DashboardMetric]
    schedule: list[DashboardMetric]
    environmental: list[DashboardMetric]
    ssoma: list[DashboardMetric]
    quality: list[DashboardMetric]
    users: list[DashboardMetric]
    licenses: list[DashboardMetric]
    ai: list[DashboardMetric]
    alerts: list[DashboardMetric]
    comparisons: list[ProjectComparison]
    portfolio_governance: list[PortfolioGovernanceItem] = Field(default_factory=list)
    operational_flow: list[OperationalFlowItem] = Field(default_factory=list)
    operating_model: CorporateOperatingModel | None = None
    gis_intelligence: CorporateGisSummary | None = None
