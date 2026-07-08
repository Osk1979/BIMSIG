# Corporate GIS Intelligence Domain

## Purpose

Corporate GIS Intelligence consolidates GIS services published by project WEB
SIG instances and turns them into corporate spatial intelligence.

It is a governance and analysis domain. It does not edit project data, replace
WEB SIG, publish operational layers, or capture field information.

## Responsibilities

- Register project GIS sources by company, program, project, WEB SIG, service,
  discipline, layer type, status, and update date.
- Register WMS, WFS, WMTS, Vector Tiles, and GIS API references.
- Register corporate layers for physical progress, schedule, risks, quality,
  SSOMA, environmental, production, land parcels, restrictions, interferences,
  and spatial KPIs.
- Produce Corporate GIS Summary.
- Expose corporate map references.
- Filter projects by spatial indicator.
- Feed the Executive Dashboard with consolidated spatial intelligence.

## API Surface

- `GET /api/v1/companies/{company_id}/gis-intelligence/sources`
- `POST /api/v1/companies/{company_id}/gis-intelligence/sources`
- `GET /api/v1/companies/{company_id}/projects/{project_id}/gis-intelligence/sources`
- `GET /api/v1/companies/{company_id}/gis-intelligence/layers`
- `POST /api/v1/companies/{company_id}/gis-intelligence/layers`
- `GET /api/v1/companies/{company_id}/projects/{project_id}/gis-intelligence/layers/status`
- `GET /api/v1/companies/{company_id}/gis-intelligence/maps/corporate`
- `GET /api/v1/companies/{company_id}/gis-intelligence/projects/filter`
- `GET /api/v1/companies/{company_id}/gis-intelligence/summary`

## Acceptance Criteria

1. Corporate GIS sources are company and project scoped.
2. Corporate layers require a registered source.
3. Corporate layers expose discipline, layer type, status, spatial indicator,
   value, region, risk level, and update date.
4. Summary reports georeferenced projects, active layers, spatial risks,
   environmental alerts, active restrictions, and aggregated spatial progress.
5. Dashboard exposes Corporate GIS Intelligence metrics.
6. OpenAPI is versioned.
7. Unit, contract, and persistence tests pass.
8. No endpoint edits project GIS data or performs WEB SIG operations.

## ADR Traceability

- ADR-0009.
- ADR-0010.
- ADR-0011.
- ADR-0013.
- ADR-0028.
