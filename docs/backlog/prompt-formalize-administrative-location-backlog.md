# Formal Administrative Location Backlog

## Objective

Formalize project administrative location in Enterprise Wizard and Portfolio
Domain so the Peru administrative map consumes official corporate data instead
of relying on inferred coordinates.

## Implemented Scope

- Extended `PortfolioProject` with country, region, province, district,
  latitude, longitude, location source, and validation status.
- Extended Enterprise Wizard `location` step required fields.
- Wizard activation persists administrative location into Portfolio Domain.
- Dashboard `map_points` exposes formal administrative location fields.
- Peru administrative map displays official source and validation status when
  available.
- Added Alembic migration for portfolio location fields.

## Constraints

- No new domains.
- No ADR changes.
- No GIS editing.
- No geometry mutation.
- No WEB SIG operational logic.

## Acceptance Criteria

- Wizard location step requires administrative and coordinate data.
- Activated Wizard projects expose region, province, district, and validation
  status through project APIs.
- Dashboard map points include official administrative location fields.
- SQLAlchemy repository round-trips the new location fields.
