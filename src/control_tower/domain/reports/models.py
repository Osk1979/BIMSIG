"""Corporate reporting and print domain models.

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0018: Corporate executive dashboard.
- ADR-0019: NAS Corporate Information Center.
- ADR-0025: Corporate Portfolio Domain.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ReportTemplate(StrEnum):
    """Official Corporate Control Tower report templates."""

    EXECUTIVE_PORTFOLIO = "executive_portfolio"
    COMPANY_STATUS = "company_status"
    PROJECT_GOVERNANCE = "project_governance"
    GIS_CORPORATE = "gis_corporate"
    AUDIT_SUMMARY = "audit_summary"


class ReportScope(StrEnum):
    """Governed report scope."""

    COMPANY = "company"
    PROGRAM = "program"
    PROJECT = "project"
    PORTFOLIO = "portfolio"


class ReportFormat(StrEnum):
    """Supported print/export formats."""

    HTML_PRINT = "html_print"
    PDF = "pdf"


class ReportRequest(BaseModel):
    """Request to prepare or issue a corporate report."""

    company_id: str = Field(min_length=3, examples=["CRTG"])
    template: ReportTemplate = ReportTemplate.EXECUTIVE_PORTFOLIO
    scope: ReportScope = ReportScope.COMPANY
    project_id: str | None = Field(default=None, min_length=3, examples=["PSZ-2026"])
    program_id: str | None = Field(default=None, min_length=3, examples=["PRG-TRANSPORTE-2026"])
    requested_by: str = Field(default="system", min_length=1)
    output_format: ReportFormat = ReportFormat.HTML_PRINT
    filters: dict[str, str] = Field(default_factory=dict)
    register_nas_reference: bool = True


class ReportManifest(BaseModel):
    """Traceable manifest for a corporate report emission."""

    report_id: str = Field(min_length=3, examples=["RPT-CRTG-20260708-001"])
    company_id: str = Field(min_length=3)
    template: ReportTemplate
    scope: ReportScope
    title: str = Field(min_length=3)
    output_format: ReportFormat
    requested_by: str = Field(min_length=1)
    project_id: str | None = None
    program_id: str | None = None
    filters: dict[str, str] = Field(default_factory=dict)
    data_sources: list[str] = Field(default_factory=list)
    nas_logical_uri: str = Field(min_length=6)
    checksum_sha256: str = Field(min_length=64, max_length=64)
    status: str = Field(default="issued")
    created_at: datetime


class CorporatePrintReport(BaseModel):
    """Print-ready corporate report response."""

    manifest: ReportManifest
    html: str = Field(min_length=20)
    print_css: str = Field(default="")
    pdf_path: str | None = None
    pdf_size_bytes: int | None = Field(default=None, ge=0)
