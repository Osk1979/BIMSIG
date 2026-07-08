# ADR-0028: Corporate GIS Intelligence

## Status

Accepted

## Context

The REV13 architecture introduces ADR-0013: Corporate GIS Intelligence. Corporate
Control Tower must evolve from portfolio dashboard into a Corporate Geospatial
Intelligence Center that consumes GIS publications from all WEB SIG instances.

The Tower must not edit project GIS data, replace WEB SIG, capture field data, or
operate project workflows. It consolidates, analyzes, filters, and reports
published spatial intelligence.

## Decision

Corporate Control Tower will add the `corporate_gis_intelligence` domain.

The domain registers:

- Project WEB SIG GIS sources.
- WMS, WFS, WMTS, Vector Tiles, and GIS API references.
- Corporate layers for progress, schedule, risks, quality, SSOMA,
  environmental, production, land parcels, restrictions, interferences, and
  spatial KPIs.
- Spatial indicators used by executive filters and dashboard summaries.

The domain exposes company-scoped APIs for sources, layers, layer status,
corporate maps, project filtering, and portfolio spatial summary.

## Consequences

The existing Corporate GIS Administration domain remains responsible for
PostGIS, GeoServer, workspaces, datastores, layers, and project bindings.

Corporate GIS Intelligence consumes published project references and stores only
metadata, URLs, statuses, classifications, and indicators.

No geometry editing, project GIS operation, WEB SIG application logic, or field
capture is introduced.

## References

- ADR-0009: GeoServer integration.
- ADR-0010: Google Workspace transition integration.
- ADR-0011: Deployment strategy.
- ADR-0013: Corporate GIS Intelligence.
- ADR-0015: Tower vs WEB SIG boundary.
- ADR-0023: Corporate GIS Administration.
- ADR-0025: Corporate Portfolio Domain.
- ADR-0027: Corporate Control Tower operational flow.
