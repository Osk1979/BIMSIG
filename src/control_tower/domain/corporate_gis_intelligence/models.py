"""Corporate GIS Intelligence domain models.

ADR references:
- ADR-0009: GeoServer integration.
- ADR-0010: Google Workspace transition integration.
- ADR-0011: Deployment strategy.
- ADR-0013: Corporate GIS Intelligence.
- ADR-0015: Tower vs WEB SIG operational boundary.
"""

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class GisServiceKind(StrEnum):
    """GIS services published by project WEB SIG instances."""

    WMS = "wms"
    WFS = "wfs"
    WMTS = "wmts"
    VECTOR_TILES = "vector_tiles"
    GIS_API = "gis_api"


class GisDiscipline(StrEnum):
    """Corporate discipline used to classify GIS intelligence."""

    BIM = "bim"
    GIS = "gis"
    PMO = "pmo"
    QUALITY = "quality"
    SSOMA = "ssoma"
    ENVIRONMENTAL = "environmental"
    PRODUCTION = "production"
    LAND = "land"
    RISK = "risk"


class CorporateLayerType(StrEnum):
    """Corporate layer categories consolidated by the Tower."""

    PHYSICAL_PROGRESS = "physical_progress"
    SCHEDULE = "schedule"
    RISKS = "risks"
    QUALITY = "quality"
    SSOMA = "ssoma"
    ENVIRONMENTAL = "environmental"
    PRODUCTION = "production"
    LAND_PARCELS = "land_parcels"
    RESTRICTIONS = "restrictions"
    INTERFERENCES = "interferences"
    SPATIAL_KPIS = "spatial_kpis"


class CorporateGisSourceStatus(StrEnum):
    """Lifecycle status for a published project GIS source."""

    REGISTERED = "registered"
    ACTIVE = "active"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    ARCHIVED = "archived"


class CorporateLayerStatus(StrEnum):
    """Operational status for a corporate layer reference."""

    AVAILABLE = "available"
    WARNING = "warning"
    CRITICAL = "critical"
    DISABLED = "disabled"


class CorporateGisAvailability(StrEnum):
    """Availability status for published GIS services consumed by the Tower."""

    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    NOT_CONFIGURED = "not_configured"


class CorporateGisSource(BaseModel):
    """Published GIS source consumed by Corporate GIS Intelligence."""

    source_id: str = Field(min_length=3, examples=["CGIS-SRC-001"])
    company_id: str = Field(min_length=3, examples=["CRTG"])
    project_id: str = Field(min_length=3, examples=["PSZ-2026"])
    program_id: str | None = Field(default=None, min_length=3)
    websig_instance_id: str | None = Field(default=None, min_length=3)
    service_kind: GisServiceKind
    service_url: str = Field(min_length=6, examples=["https://websig.example.com/wms"])
    discipline: GisDiscipline
    layer_type: CorporateLayerType
    status: CorporateGisSourceStatus = CorporateGisSourceStatus.REGISTERED
    updated_on: date
    metadata: dict[str, str] = Field(default_factory=dict)


class CorporateGisServiceValidation(BaseModel):
    """Validation result for one published WEB SIG GIS service."""

    source_id: str = Field(min_length=3)
    service_kind: GisServiceKind
    service_url: str = Field(min_length=6)
    availability: CorporateGisAvailability
    status_code: int | None = None
    capability_detected: bool = False
    detail: str = Field(min_length=2)
    checked_url: str | None = None


class CorporateLayerLegendItem(BaseModel):
    """Legend item used by the Corporate GIS dashboard layer panel."""

    layer_id: str = Field(min_length=3)
    name: str = Field(min_length=3)
    service_kind: GisServiceKind
    layer_type: CorporateLayerType
    discipline: GisDiscipline
    status: CorporateLayerStatus
    availability: CorporateGisAvailability = CorporateGisAvailability.NOT_CONFIGURED
    risk_level: str = Field(default="none", min_length=3)
    indicator_value: float = Field(default=0, ge=0)
    service_url: str | None = None
    legend_url: str | None = None


class CorporateGisLayerPanel(BaseModel):
    """Read-only GIS layer panel assembled from published WEB SIG services."""

    company_id: str = Field(min_length=3)
    project_id: str | None = Field(default=None, min_length=3)
    layers: list[CorporateLayerLegendItem] = Field(default_factory=list)
    validations: list[CorporateGisServiceValidation] = Field(default_factory=list)
    filters: dict[str, list[str]] = Field(default_factory=dict)


class CorporateLayer(BaseModel):
    """Corporate layer read model backed by a published WEB SIG GIS source."""

    layer_id: str = Field(min_length=3, examples=["CGIS-LYR-001"])
    source_id: str = Field(min_length=3, examples=["CGIS-SRC-001"])
    company_id: str = Field(min_length=3, examples=["CRTG"])
    project_id: str = Field(min_length=3, examples=["PSZ-2026"])
    program_id: str | None = Field(default=None, min_length=3)
    name: str = Field(min_length=3, examples=["Avance fisico"])
    layer_type: CorporateLayerType
    discipline: GisDiscipline
    status: CorporateLayerStatus = CorporateLayerStatus.AVAILABLE
    spatial_indicator: str = Field(min_length=3, examples=["physical_progress"])
    indicator_value: float = Field(default=0, ge=0)
    updated_on: date
    region: str | None = Field(default=None, min_length=2)
    risk_level: str = Field(default="none", min_length=3)
    metadata: dict[str, str] = Field(default_factory=dict)


class ProjectSpatialIndicator(BaseModel):
    """Project-level spatial indicator used by executive filters."""

    company_id: str = Field(min_length=3)
    project_id: str = Field(min_length=3)
    project_name: str = Field(min_length=3)
    indicator: str = Field(min_length=3)
    value: float = Field(ge=0)
    risk_level: str = Field(min_length=3)
    layer_id: str = Field(min_length=3)


class CorporateGisSummary(BaseModel):
    """Portfolio-level spatial intelligence summary."""

    company_id: str = Field(min_length=3)
    total_projects_georeferenced: int = Field(ge=0)
    projects_with_active_layers: int = Field(ge=0)
    projects_with_spatial_risks: int = Field(ge=0)
    projects_with_environmental_alerts: int = Field(ge=0)
    projects_with_active_restrictions: int = Field(ge=0)
    aggregated_spatial_progress: float = Field(ge=0)
    layers_by_type: dict[str, int] = Field(default_factory=dict)
    layers_by_status: dict[str, int] = Field(default_factory=dict)
    regions: dict[str, int] = Field(default_factory=dict)


class CorporateGisIntelligenceMap(BaseModel):
    """Corporate spatial map assembled from project WEB SIG publications."""

    company_id: str = Field(min_length=3)
    sources: list[CorporateGisSource] = Field(default_factory=list)
    layers: list[CorporateLayer] = Field(default_factory=list)
    summary: CorporateGisSummary
