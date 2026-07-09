# PROMPT HARDENING-003 - Real Infrastructure Connectors

ADR references:
- ADR-0007: NAS integration.
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0010: Google Workspace transition integration.
- ADR-0021: DevSecOps operating model.

## Objective

Move from governed references to controlled real connector checks and execution for PostGIS, GeoServer, NAS, and Google Drive.

## Delivered

- PostGIS connector with health, configuration validation, dry-run schema plan, and controlled schema execution.
- GeoServer connector with REST health, configuration validation, dry-run workspace plan, and controlled workspace execution.
- NAS filesystem connector with root validation, dry-run directory plan, and controlled directory creation.
- Google Drive connector with root and credential validation, optional REST health check, dry-run folder plan, and controlled folder creation when an access token is configured.
- Connector API:
  - `GET /api/v1/infrastructure/connectors/health`
  - `GET /api/v1/infrastructure/connectors/{connector}/health`
  - `POST /api/v1/infrastructure/connectors/{connector}/validate`
  - `POST /api/v1/infrastructure/connectors/{connector}/dry-run`
  - `POST /api/v1/infrastructure/connectors/{connector}/execute`
- Auditing for validate, dry-run, and execute operations.
- RBAC mapping for infrastructure connector endpoints under provisioning permissions.
- Unit tests with mock connector and real temporary NAS filesystem execution.
- API contract test for connector health, dry-run, approval gate, execute, and audit.

## Configuration

- `CONTROL_TOWER_POSTGIS_DATABASE_URL`
- `CONTROL_TOWER_GEOSERVER_URL`
- `CONTROL_TOWER_GEOSERVER_USER`
- `CONTROL_TOWER_GEOSERVER_PASSWORD`
- `CONTROL_TOWER_NAS_ROOT`
- `CONTROL_TOWER_GOOGLE_DRIVE_ROOT_ID`
- `CONTROL_TOWER_GOOGLE_DRIVE_ACCESS_TOKEN`
- `CONTROL_TOWER_GOOGLE_APPLICATION_CREDENTIALS` or `GOOGLE_APPLICATION_CREDENTIALS`

## Acceptance Criteria

- Dry-run must not mutate external infrastructure.
- Execute requires `approved_by`.
- Missing configuration returns controlled `misconfigured` results.
- Live failures return controlled errors and audit entries.
- No WEB SIG operational logic is implemented.
