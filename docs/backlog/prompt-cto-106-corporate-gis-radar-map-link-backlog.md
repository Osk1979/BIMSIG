# CTO-106 - Corporate GIS Real Map + Project Radar Link Backlog

## Objective

Connect the executive Project Radar with a Corporate GIS map surface while
consuming only existing Corporate Layers and published WEB SIG services.

## Implemented Scope

- Project Radar remains as the executive project signal view.
- Corporate GIS map surface is displayed next to the radar.
- Selecting a radar project highlights the matching geometry on the GIS map.
- Selecting a KPI bridge card activates the related GIS layer filter.
- Corporate layer legend remains visible.
- Selected project detail shows geometry source, state, active layer, and
  readiness.
- WMS, WFS, WMTS, and Vector Tiles service slots are prepared for published
  services.

## Constraints

- No new domains.
- No ADR changes.
- No architecture changes.
- No GIS editing.
- No geometry mutation.
- No WEB SIG operational logic.

## Acceptance Criteria

- `/dashboard` exposes both `projectRadar` and `gisMapSurface`.
- Project and map markers share the same project selection state.
- KPI cards are actionable and mapped to layer filters.
- The UI states that geometry is published by WEB SIG and remains read-only.
