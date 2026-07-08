"""Corporate Information Center NAS domain models.

ADR references:
- ADR-0007: NAS integration.
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0010: Google Workspace transition integration.
- ADR-0019: NAS Corporate Information Center.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class InformationAssetType(StrEnum):
    """Information asset file and resource classes governed through NAS."""

    DOCUMENTATION = "documentation"
    IFC = "ifc"
    DWG = "dwg"
    LANDXML = "landxml"
    PHOTOGRAPHY = "photography"
    VIDEO = "video"
    SHAPEFILE = "shapefile"
    GEOJSON = "geojson"
    GEOSERVER = "geoserver"
    POSTGIS = "postgis"
    DOCKER = "docker"
    GOOGLE_DRIVE = "google_drive"
    BACKUP = "backup"


class InformationCategory(StrEnum):
    """Corporate information categories governed by NAS."""

    BIM = "bim"
    GIS = "gis"
    CDE = "cde"
    FIELD = "field"
    QA_QC = "qa_qc"
    ENVIRONMENTAL = "environmental"
    SSOMA = "ssoma"
    PMO = "pmo"


class InformationAssetStatus(StrEnum):
    """Lifecycle status for a registered information asset."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    ARCHIVED = "archived"


class InformationPermission(StrEnum):
    """Coarse-grained permission levels for information assets."""

    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class InformationAsset(BaseModel):
    """Enterprise information asset registered by the Corporate Information Center."""

    asset_id: str = Field(min_length=3, examples=["NAS-001"])
    company_id: str = Field(min_length=3, examples=["CRTG"])
    project_id: str | None = Field(default=None, min_length=3, examples=["PSZ-2026"])
    name: str = Field(min_length=3, examples=["Modelo federado IFC"])
    asset_type: InformationAssetType
    category: InformationCategory = InformationCategory.CDE
    logical_uri: str = Field(min_length=6, examples=["nas://CRTG/PSZ-2026/bim/ifc/model.ifc"])
    version: str = Field(default="v1")
    status: InformationAssetStatus = InformationAssetStatus.DRAFT
    metadata: dict[str, str] = Field(default_factory=dict)
    permissions: dict[str, InformationPermission] = Field(default_factory=dict)
    google_drive_id: str | None = None
    geoserver_reference: str | None = None
    postgis_reference: str | None = None
    docker_reference: str | None = None
    checksum_sha256: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class InformationVersion(BaseModel):
    """Immutable version reference for an information asset."""

    version_id: str = Field(min_length=3)
    asset_id: str = Field(min_length=3)
    version: str = Field(min_length=1)
    logical_uri: str = Field(min_length=6)
    checksum_sha256: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class InformationSnapshot(BaseModel):
    """Snapshot manifest for a company or project information state."""

    snapshot_id: str = Field(min_length=3)
    company_id: str = Field(min_length=3)
    project_id: str | None = Field(default=None, min_length=3)
    name: str = Field(min_length=3)
    asset_ids: list[str] = Field(default_factory=list)
    logical_uri: str = Field(min_length=6)
    metadata: dict[str, str] = Field(default_factory=dict)


class InformationBackup(BaseModel):
    """Backup manifest registered by the Corporate Information Center."""

    backup_id: str = Field(min_length=3)
    company_id: str = Field(min_length=3)
    project_id: str | None = Field(default=None, min_length=3)
    snapshot_id: str | None = Field(default=None, min_length=3)
    logical_uri: str = Field(min_length=6)
    checksum_sha256: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)
