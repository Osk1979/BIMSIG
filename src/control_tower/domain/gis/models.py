"""Corporate GIS administration domain models.

ADR references:
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0015: Tower vs WEB SIG boundary.
- ADR-0023: Corporate GIS administration.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class GisResourceStatus(StrEnum):
    """Corporate GIS registry status."""

    REGISTERED = "registered"
    VALIDATED = "validated"
    UNAVAILABLE = "unavailable"


class GisServiceType(StrEnum):
    """GeoServer service endpoint type governed by the Tower."""

    WMS = "wms"
    WFS = "wfs"


class PostgisSchema(BaseModel):
    """Corporate reference to a project PostGIS schema."""

    schema_id: str = Field(min_length=3, examples=["PGS-001"])
    company_id: str = Field(min_length=3, examples=["CRTG"])
    project_id: str = Field(min_length=3, examples=["PSZ-2026"])
    schema_name: str = Field(min_length=3, examples=["crtg_psz_2026"])
    database_ref: str = Field(min_length=6, examples=["postgis://CRTG/crtg_psz_2026"])
    status: GisResourceStatus = GisResourceStatus.REGISTERED


class GeoServerWorkspace(BaseModel):
    """Corporate reference to a GeoServer workspace."""

    workspace_id: str = Field(min_length=3, examples=["GWS-001"])
    company_id: str = Field(min_length=3, examples=["CRTG"])
    project_id: str = Field(min_length=3, examples=["PSZ-2026"])
    name: str = Field(min_length=3, examples=["CRTG_PSZ_2026"])
    geoserver_url: str = Field(min_length=6, examples=["https://geoserver.example.com"])
    status: GisResourceStatus = GisResourceStatus.REGISTERED


class GeoServerDatastore(BaseModel):
    """Corporate reference to a GeoServer datastore."""

    datastore_id: str = Field(min_length=3, examples=["GDS-001"])
    company_id: str = Field(min_length=3, examples=["CRTG"])
    project_id: str = Field(min_length=3, examples=["PSZ-2026"])
    workspace_id: str = Field(min_length=3, examples=["GWS-001"])
    name: str = Field(min_length=3, examples=["postgis_psz"])
    postgis_schema_id: str = Field(min_length=3, examples=["PGS-001"])
    status: GisResourceStatus = GisResourceStatus.REGISTERED


class GeoServerLayer(BaseModel):
    """Corporate reference to a GeoServer layer and service URLs."""

    layer_id: str = Field(min_length=3, examples=["GLY-001"])
    company_id: str = Field(min_length=3, examples=["CRTG"])
    project_id: str = Field(min_length=3, examples=["PSZ-2026"])
    workspace_id: str = Field(min_length=3, examples=["GWS-001"])
    datastore_id: str = Field(min_length=3, examples=["GDS-001"])
    name: str = Field(min_length=3, examples=["frentes_obra"])
    title: str = Field(min_length=3, examples=["Frentes de obra"])
    wms_url: str | None = Field(default=None, min_length=6)
    wfs_url: str | None = Field(default=None, min_length=6)
    status: GisResourceStatus = GisResourceStatus.REGISTERED


class ProjectGisBinding(BaseModel):
    """Binding between one project, one PostGIS schema, and one GeoServer workspace."""

    binding_id: str = Field(min_length=3, examples=["GBD-001"])
    company_id: str = Field(min_length=3, examples=["CRTG"])
    project_id: str = Field(min_length=3, examples=["PSZ-2026"])
    postgis_schema_id: str = Field(min_length=3, examples=["PGS-001"])
    geoserver_workspace_id: str = Field(min_length=3, examples=["GWS-001"])
    status: GisResourceStatus = GisResourceStatus.REGISTERED


class ProjectGisResources(BaseModel):
    """Read model for corporate GIS resources scoped to one project."""

    company_id: str = Field(min_length=3)
    project_id: str = Field(min_length=3)
    binding: ProjectGisBinding | None = None
    postgis_schema: PostgisSchema | None = None
    geoserver_workspace: GeoServerWorkspace | None = None
    datastores: list[GeoServerDatastore] = Field(default_factory=list)
    layers: list[GeoServerLayer] = Field(default_factory=list)


class GisResourceValidation(BaseModel):
    """Validation result for one corporate GIS resource."""

    resource_type: str = Field(min_length=3)
    resource_id: str = Field(min_length=3)
    valid: bool
    detail: str = Field(min_length=3)
