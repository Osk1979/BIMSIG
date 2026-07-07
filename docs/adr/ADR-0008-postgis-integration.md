# ADR-0008: PostGIS Integration

## Status

Accepted

## Context

REV11 identifies PostGIS as part of the information core. Corporate Control Tower is a portfolio governance system, not the operational WEB SIG datastore, but it needs geospatial metadata for project location, portfolio maps, provisioning boundaries, and references to published geospatial resources.

## Decision

Corporate Control Tower REV12 will use PostgreSQL with PostGIS enabled for spatial portfolio metadata and geospatial references. WEB SIG operational geospatial datasets remain owned by their project-specific WEB SIG instances unless an approved ADR defines shared enterprise datasets.

## Initial Spatial Scope

Corporate Control Tower may persist:

- Project footprint geometry.
- Project centroid.
- Administrative area references.
- Linear infrastructure corridor references.
- GeoServer workspace and layer references.
- Spatial status metadata for portfolio dashboard views.

Corporate Control Tower must not become the primary editor for detailed operational GIS layers owned by WEB SIG.

## Data Rules

- Use explicit SRID for all geometry columns.
- Prefer SRID 4326 for portfolio-level web interoperability unless a schema ADR approves another SRID.
- Validate geometry before persistence.
- Keep geometry changes auditable.
- Use migrations for all spatial schema changes.

## Consequences

The database schema ADR must define geometry columns, indexes, and migration tooling before production persistence is implemented.

## References

- ADR-0001: REV11 as architecture baseline.
- ADR-0005: Persistence strategy.
- Documento A - Arquitectura Maestra REV11: NAS + PostGIS + GeoServer as information core.
