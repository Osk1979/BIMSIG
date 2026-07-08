# CTO-106 Extension - Peru Administrative Map Backlog

## Objective

Add an executive Peru administrative map outside the Project Radar and the
Corporate GIS map surface.

## Implemented Scope

- Separate Peru administrative map section in Corporate GIS Dashboard.
- Project markers derived from existing corporate `map_points`.
- Region chips with project counts.
- Project detail with country, region, province, district, and data source.
- Selection synchronization with Project Radar and Corporate GIS map.

## Constraints

- No new domains.
- No ADR changes.
- No GIS editing.
- No geometry mutation.
- No WEB SIG operational logic.
- Administrative location is derived from existing corporate map data and may
  show pending registration when official province or district is not available.

## Acceptance Criteria

- `/dashboard` exposes `peruAdministrativeMap`.
- The Peru map is visually separate from `projectRadar` and `gisMapSurface`.
- Selecting a Peru marker updates the selected corporate project.
- The detail panel shows Region, Provincia, and Distrito.
