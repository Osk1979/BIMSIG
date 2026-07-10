"""Portal Gateway domain models.

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0018: Corporate executive dashboard.
- ADR-0029: Enterprise portal gateway.
"""

from pydantic import BaseModel, Field

from control_tower.domain.dashboard import CorporateDashboard, DashboardMetric
from control_tower.domain.reports import ReportTemplateDescriptor


class PortalGatewayLink(BaseModel):
    """Navigable enterprise portal link governed by the Control Tower."""

    link_id: str = Field(min_length=3)
    label: str = Field(min_length=3)
    href: str = Field(min_length=6)
    description: str = Field(min_length=10)
    status: str = Field(default="available")
    target: str = Field(default="_blank")


class PortalGatewayConfig(BaseModel):
    """Runtime configuration consumed by the BIM-SIG enterprise portal."""

    portal_origin: str = Field(min_length=6)
    tower_base_url: str = Field(min_length=6)
    websig_base_url: str = Field(min_length=6)
    default_company_id: str = Field(min_length=3)
    links: list[PortalGatewayLink]


class PortalGatewayHealth(BaseModel):
    """Readiness contract between the portal and the Corporate Control Tower."""

    status: str = "ok"
    revision: str = "REV12"
    service: str = "portal-gateway"
    tower: str = "available"
    dashboard: str = "available"
    reports: str = "available"


class PortalGatewaySnapshot(BaseModel):
    """Single payload for the portal landing experience and Tower handoff."""

    company_id: str = Field(min_length=3)
    title: str = Field(min_length=3)
    metrics: list[DashboardMetric]
    links: list[PortalGatewayLink]
    dashboard: CorporateDashboard
    report_templates: list[ReportTemplateDescriptor]
