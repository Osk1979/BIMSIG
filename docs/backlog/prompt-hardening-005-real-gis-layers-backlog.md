# PROMPT HARDENING-005 - Real GIS Layers

ADR references:
- ADR-0009: GeoServer integration.
- ADR-0013: Corporate GIS Intelligence.
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0023: Corporate GIS Administration.
- ADR-0028: Corporate GIS Intelligence.

## Objective

Enable the Corporate GIS Dashboard to consume and validate real GIS services published by WEB SIG instances, without editing geometries or capturing field data.

## Delivered

- Real GIS service registration endpoint:
  - `POST /api/v1/companies/{company_id}/gis-intelligence/real-services`
- WMS validator through `GetCapabilities`.
- WFS validator through `GetCapabilities`.
- WMTS validator through `GetCapabilities`.
- Vector Tiles slot validator using tile metadata signatures.
- Service validation endpoints:
  - `POST /api/v1/companies/{company_id}/gis-intelligence/sources/{source_id}/validate`
  - `POST /api/v1/companies/{company_id}/gis-intelligence/sources/validate`
- Corporate layer panel endpoint:
  - `GET /api/v1/companies/{company_id}/gis-intelligence/layer-panel`
- Layer panel includes:
  - Published layer list.
  - Service kind.
  - Availability.
  - Legend URL for WMS layers.
  - Filters by discipline, status, risk, and layer type.
- Dashboard UI now consumes the layer panel for service slots and layer legend.
- Unit and contract tests using mocked WMS, WFS, WMTS, and Vector Tiles responses.

## Guardrails

- No geometry editing.
- No field capture.
- No WEB SIG operational logic.
- Corporate Control Tower only consumes, validates, filters, and displays published layers.
