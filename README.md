# Corporate Control Tower REV12

Corporate Control Tower REV12 is the portfolio governance layer of BIMSIG Enterprise Platform.

This repository starts F2 of the BIMSIG Enterprise master program: Corporate Control Tower and Project Provisioning Engine.

## Architectural Source

The implementation is constrained by the approved REV11 documents:

- `D:\Implementacion_BIMSIG\Documento_A_Arquitectura_Maestra_REV11.docx`
- `D:\Implementacion_BIMSIG\Documento_B_Programa_Maestro_REV11.docx`
- `D:\Implementacion_BIMSIG\Documento_C_Manual_Prompts_REV11.docx`

## Official Principles Applied

- WEB SIG administers each project.
- Corporate Control Tower administers the portfolio.
- Each project owns its own WEB SIG.
- Corporate Control Tower creates and registers new WEB SIG instances.
- The enterprise NAS is the master repository.

## Repository Layout

```text
docs/adr/                  Architecture Decision Records
docs/api/                  API contracts and OpenAPI documentation
docs/architecture/         Architecture notes derived from REV11
docs/backlog/              Phase backlog and delivery tracking
docs/traceability/         Traceability from REV11 documents to code
src/control_tower/api/     HTTP API boundary
src/control_tower/application/ Application services and use cases
src/control_tower/domain/  Pure domain model
tests/unit/                Unit tests
tests/contract/            Contract tests
```

## Development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
pytest
uvicorn control_tower.api.app:create_app --factory --reload
```

Set `CONTROL_TOWER_DATABASE_URL` to use PostgreSQL/PostGIS in an integrated environment:

```bash
CONTROL_TOWER_DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/bimsig
```

Apply database migrations:

```bash
python -m alembic upgrade head
```

Initial API groups:

- Health: `/health`, `/api/v1/operational/health`
- Portfolio: `/api/v1/portfolio/summary`
- Projects: `/api/v1/projects`
- Governance status: `/api/v1/projects/{project_id}/governance-status`
- WEB SIG provisioning: `/api/v1/provisioning/websig`
- Audit: `/api/v1/audit/events`

Regenerate the versioned OpenAPI contract:

```bash
python scripts/export_openapi.py
```

All implementation work must reference the relevant ADR and keep modules decoupled.

## Technical ADR Set

- ADR-0005: Persistence strategy.
- ADR-0006: Authentication and authorization.
- ADR-0007: NAS integration.
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0010: Google Workspace transition integration.
- ADR-0011: Deployment strategy.
- ADR-0012: CI/CD strategy.
- ADR-0013: Database schema and migrations.
- ADR-0014: Enterprise multitenancy.
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0016: Enterprise licensing.

## PROMPT MASTER 002

Enterprise architecture documents:

- `docs/architecture/prompt-002-enterprise-control-tower-architecture.md`
- `docs/architecture/prompt-002-domain-model.md`
- `docs/architecture/prompt-002-api-map.md`
- `docs/backlog/prompt-002-enterprise-build-backlog.md`

## Operational Flow

The governed Corporate Control Tower operating model is documented in:

- `docs/operations/corporate-control-tower-operational-flow.md`

It defines the enterprise path from corporate intake to WEB SIG Factory approval,
NAS/GIS registration, executive dashboard publication, audit, release, GitHub
push, and physical USB backup.

## Corporate Experience Platform

CTO-104 REV03 turns the existing domains into the first Enterprise user
experience for Corporate Control Tower. The `/dashboard` surface includes:

- Corporate Home for portfolio, GIS, NAS, provisioning, alerts, events, and
  pending actions.
- Corporate Navigation by business processes instead of internal domain names.
- Corporate Portfolio Explorer with company, program, project, WEB SIG, status,
  and dashboard readiness.
- Corporate GIS Dashboard consuming only published Corporate Layers in read-only
  mode.
- Corporate Wizard visual flow for enterprise project provisioning.
- Executive Dashboard questions for management review.
- Corporate Notifications for provisioning, GIS, NAS, status, security, and
  alert events.

This experience reuses existing services and API contracts. It does not create
new domains, modify ADRs, or add WEB SIG operational logic.

CTO-105 connects that experience to existing data flows:

- Portfolio Explorer consumes company projects and dashboard governance data.
- Corporate Wizard reads resumable Enterprise Wizard sessions.
- Corporate Notifications uses the audit event stream.
- Corporate GIS filters call the existing GIS Intelligence map filter endpoint.
- Executive Dashboard cards link to actionable portfolio, GIS, audit, NAS, and
  provisioning sections.

CTO-106 adds the visual link between the Project Radar and the Corporate GIS
map surface. Selecting a project signal in the radar highlights the same project
geometry on the GIS surface, while KPI cards activate related Corporate Layers.
The map surface remains read-only and prepared for WMS, WFS, WMTS, and Vector
Tiles published by WEB SIG Enterprise.

The Corporate GIS experience also includes a separate Peru administrative map
for executive location review. It shows projects by region, province, and
district using existing corporate map points and GIS intelligence references,
and synchronizes project selection with the radar and GIS map without editing
geometries.

Project administrative location is now formalized through the Enterprise Wizard
and Portfolio Domain. The Wizard location step captures country, region,
province, district, corporate coordinates, source, and validation status; Wizard
activation persists those values into the portfolio project so the Peru map can
prefer official corporate data over inferred coordinates.

CTO-104D completes the Enterprise Wizard product experience. The dashboard now
shows a guided corporate assistant with visible progress, resumable sessions,
independent step validation, partial save, activation readiness, permission-aware
blocked states, audit events, and a pre-activation summary that traces Workflow,
Portfolio, GIS, NAS, Audit, and WEB SIG references through existing services.

CTO-104E turns Portfolio Explorer into an Organization Navigator. The dashboard
now presents the corporate hierarchy as Empresa -> Programa -> Proyecto -> WEB
SIG -> Estado, with search, executive filters, persistent project selection,
project detail, and navigation to Dashboard, GIS, NAS, Reports, Audit, and
Wizard using the existing Portfolio, RBAC, and dashboard data flows.

CTO-107 introduces the Corporate Reporting & Print Engine. It exposes report
templates, preview, issued report manifests, print-ready HTML output, checksum
traceability, NAS logical references, and audit events for formal corporate
report issuance.

## WEB SIG Factory Template Adapter

The Project Provisioning Engine can provision WEB SIG instances from the
approved factory template
`WEB_SIG_ENTERPRISE_REPOSITORY_REV02_FACTORY_TEMPLATE_WEB-SIG-001`.

Configure physical template execution with:

```bash
CONTROL_TOWER_WEBSIG_FACTORY_TEMPLATE_PATH=D:\Implementacion_BIMSIG\WEBSIG\WEB_SIG_ENTERPRISE_REPOSITORY_REV02_FACTORY_TEMPLATE_WEB-SIG-001
CONTROL_TOWER_WEBSIG_FACTORY_OUTPUT_ROOT=D:\Implementacion_BIMSIG\WEBSIG\instances
```

When configured, controlled WEB SIG Factory execution copies the template into a
company/project instance and writes `websig.config.json` with company, project,
WEB SIG, PostGIS, GeoServer, NAS, dashboard, module, GIS service slot, and Tower
boundary metadata. When not configured, the Tower records governed references
without filesystem side effects.

## Enterprise Auth & SSO

HARDENING-001 adds signed Enterprise bearer sessions on top of the existing
local/OIDC/SAML identity records. The API exposes:

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/logout`

Configure production enforcement with:

```bash
CONTROL_TOWER_AUTH_REQUIRED=true
CONTROL_TOWER_AUTH_SECRET=<secret-from-vault-or-env>
CONTROL_TOWER_AUTH_TTL_MINUTES=480
```

When `CONTROL_TOWER_AUTH_REQUIRED=true`, protected API routes require a bearer
token. Local dashboard and contract-test flows remain compatible when the flag is
not enabled.

HARDENING-002 adds Enterprise RBAC alignment between API and UI. The shared role
matrix is available at `GET /api/v1/auth/permissions/matrix`; the dashboard uses
the same scopes/actions through `data-rbac-scope` and `data-rbac-action`, while
the API enforces denied actions with `403 Permission denied` when authentication
is required.

HARDENING-003 adds controlled real infrastructure connectors for PostGIS,
GeoServer, NAS filesystem, and Google Drive. The Tower now exposes connector
health, validation, dry-run, and approved execute endpoints under
`/api/v1/infrastructure/connectors`, with audit events and RBAC mapping to
provisioning permissions.

HARDENING-004 adds productive corporate PDF reporting. The Reporting & Print
Engine can issue PDF reports with cover page, index, KPIs, portfolio, GIS
summary, audit, metadata, binary checksum, download endpoint, and NAS metadata
registration for the emitted report artifact.

HARDENING-005 adds real GIS layer consumption for Corporate GIS Intelligence.
The Tower can register and validate WMS, WFS, WMTS, and Vector Tiles services
published by WEB SIG, expose a read-only layer panel with availability and
legend metadata, and drive the Corporate GIS Dashboard without editing geometry
or capturing field data.

HARDENING-006 adds production observability: structured logs, correlation ID,
API metrics, deep health, connector status, Prometheus text export, and an
OpenTelemetry-ready JSON payload.

HARDENING-007 adds Enterprise-scale data readiness through controlled massive
seed data, paginated project exploration, filters, search, query indexes,
multi-company isolation checks, and performance timing in the API responses.

HARDENING-008 adds Playwright-based visual E2E coverage for dashboard,
portfolio, GIS, wizard, reporting, responsive viewports, anti-overlap checks,
and dark/light mode. CI installs Chromium and uploads screenshots as artifacts.

HARDENING-009 prepares production deploy with Docker, PostGIS, NAS volumes,
controlled startup migrations, optional reverse proxy, health checks, backup
operations, environment template, and the runbook at
`docs/operations/production-deploy-runbook.md`.

CTO-104A turns Corporate Home into an Operations Center with a morning executive
brief, priority alerts, quick access to the main corporate flows, recent audit
activity, and recommended next actions built from existing Tower data.

CTO-104B completes the Executive Corporate Dashboard with a 60-second situation
summary, actionable status matrix for the 17 executive blocks, semaphores,
comparative cards, empty states, no-access states, and navigation toward the
main corporate flows without exposing technical domains as primary navigation.

CTO-104C turns Corporate GIS Dashboard into an executive geospatial viewer with
national, regional, company, program, and project views; thematic filters for
risk, production, schedule, quality, environmental, SSOMA, parcels, and
interferences; spatial summaries, project comparisons, published-layer legend,
and synchronized radar, GIS map, and Peru administrative map.
