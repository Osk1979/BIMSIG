# PROMPT MASTER 002: Enterprise Corporate Control Tower Architecture

## Objective

Design Corporate Control Tower REV12 as a complete enterprise platform for BIMSIG.

The Tower administers companies, users, licensing, portfolio governance, consolidated KPIs, alerts, provisioning, integrations, executive dashboards, AI, reports, security, and audit.

The Tower does not directly operate projects. Each project is operated by its own WEB SIG.

## Architecture Principles

1. Enterprise first: the Tower is multi-company and multi-project.
2. Company tenancy: every business record is scoped by company unless it is platform-level configuration.
3. Project operation boundary: WEB SIG owns project operations.
4. Consolidated consumption: the Tower consumes project facts, KPIs, alerts, and integration status.
5. Provisioning control: the Tower creates, registers, and governs WEB SIG instances.
6. Integration by adapters: NAS, PostGIS, GeoServer, Google Drive, and AI are accessed through infrastructure adapters.
7. Audit everything: state-changing actions create audit events.
8. API first: public behavior is expressed through versioned APIs and OpenAPI.
9. ADR governed: architectural changes require ADRs before implementation.

## Enterprise Hierarchy

```text
BIMSIG Platform
  -> Company
      -> Users and memberships
      -> Licenses and entitlements
      -> Portfolio
          -> Project
              -> WEB SIG instance
              -> Consolidated KPI feed
              -> Alert feed
              -> Report feed
              -> Integration references
```

## Bounded Contexts

### Identity and Access

Responsibilities:

- Users.
- Company memberships.
- Roles.
- Service accounts.
- Authentication provider integration.
- Authorization policies.

Primary ADRs:

- ADR-0006.
- ADR-0014.

### Company Administration

Responsibilities:

- Companies.
- Company settings.
- Tenant boundaries.
- Company-level integrations.
- Company license assignment.

Primary ADRs:

- ADR-0014.
- ADR-0016.

### Licensing

Responsibilities:

- Plans.
- Entitlements.
- User seats.
- Project limits.
- WEB SIG provisioning quota.
- Module enablement.
- Usage counters.

Primary ADR:

- ADR-0016.

### Portfolio

Responsibilities:

- Projects.
- Governance status.
- WEB SIG registry.
- Project health summary.
- Consolidated project metadata.

Primary ADRs:

- ADR-0001.
- ADR-0005.
- ADR-0015.

### KPI and Alerts

Responsibilities:

- KPI catalog.
- KPI snapshots.
- Alert rules.
- Alert events.
- Thresholds.
- Company/project rollups.

Data source:

- Consolidated WEB SIG feeds and enterprise integration adapters.

### Project Provisioning Engine

Responsibilities:

- Provisioning request.
- Dry-run plan.
- Approval workflow.
- Execution steps.
- WEB SIG registry.
- Adapter orchestration.
- Audit trail.

Adapters:

- GitHub repository/worktree adapter.
- NAS folder adapter.
- PostgreSQL/PostGIS schema adapter.
- GeoServer workspace adapter.
- Google Drive transition folder adapter.

Primary ADR:

- ADR-0003.

### Integration Hub

Responsibilities:

- NAS metadata and logical path references.
- PostGIS portfolio spatial metadata.
- GeoServer workspaces/layers references.
- Google Drive transitional collaboration references.
- Integration health checks.

Primary ADRs:

- ADR-0007.
- ADR-0008.
- ADR-0009.
- ADR-0010.

### Executive Dashboard

Responsibilities:

- Company portfolio summary.
- Project health.
- KPI rollups.
- Alert summary.
- License usage.
- Provisioning queue.
- Integration status.

Reads:

- Materialized read models and consolidated snapshots.

### AI Services

Responsibilities:

- Portfolio summarization.
- Alert explanation.
- Report drafting.
- Risk and anomaly assistance.
- Natural-language query over governed metadata.

Rules:

- AI cannot bypass authorization.
- AI outputs are advisory unless explicitly approved by workflow.
- AI actions are audited when they affect persisted state.

### Corporate Reports

Responsibilities:

- Executive portfolio reports.
- Company status reports.
- Project rollup reports.
- KPI and alert reports.
- License and usage reports.
- Audit exports.

Outputs:

- Versioned report records.
- File references to NAS or Google Drive as approved by integration policy.

### Security and Audit

Responsibilities:

- Authentication.
- Authorization.
- Tenant isolation.
- Service account scoping.
- Audit events.
- Security events.
- Compliance exports.

Primary ADR:

- ADR-0006.

## Data Architecture

### Production Persistence

PostgreSQL with PostGIS is the durable database target.

Core schemas:

- Identity and membership.
- Companies.
- Licenses.
- Portfolio.
- WEB SIG registry.
- KPI snapshots.
- Alerts.
- Integration references.
- AI interaction logs.
- Reports.
- Audit events.

### File and Deliverable Storage

NAS remains the enterprise master repository for files and deliverables.

Google Drive is transitional collaboration storage and must not become the master registry.

### Spatial Data

The Tower stores portfolio-level spatial metadata only:

- Project footprint.
- Centroid.
- Corridor references.
- GeoServer references.

WEB SIG owns operational GIS layers.

## API Architecture

API namespace:

```text
/api/v1
```

Planned API groups:

- `/companies`
- `/users`
- `/licenses`
- `/portfolio`
- `/projects`
- `/projects/{project_id}/websig`
- `/provisioning/websig`
- `/kpis`
- `/alerts`
- `/integrations/nas`
- `/integrations/postgis`
- `/integrations/geoserver`
- `/integrations/google-drive`
- `/dashboard/executive`
- `/ai`
- `/reports`
- `/security`
- `/audit`
- `/operational/health`

## Dashboard Architecture

The executive dashboard is a read model over consolidated data. It must be optimized for scanning, portfolio comparison, and repeated decision-making.

Dashboard panels:

- Company selector.
- Portfolio status.
- Active projects.
- WEB SIG provisioning status.
- KPI health.
- Critical alerts.
- License consumption.
- Integration health.
- Recent audit events.
- AI executive summary.

## Deployment Architecture

Deployment unit:

- FastAPI API service.
- PostgreSQL/PostGIS database.
- External NAS.
- External GeoServer.
- Google Drive connector/integration.
- AI provider integration.

Staging and production must use Alembic migrations, environment variables, and secret-managed credentials.

## Non-Goals

The Tower will not:

- Replace WEB SIG operations.
- Edit operational GIS layers directly.
- Store enterprise files as database blobs.
- Treat Google Drive as authoritative enterprise registry.
- Allow cross-company data access by default.
- Execute AI actions without authorization and audit.

## Implementation Sequence

1. Multi-company model and tenant scoping.
2. Users, memberships, and roles.
3. Licensing and entitlements.
4. Project and WEB SIG registry.
5. Provisioning dry-run and execution plan.
6. Integration adapter contracts.
7. KPI and alert ingestion.
8. Executive dashboard read models.
9. Report generation.
10. AI-assisted summaries and diagnostics.
11. Security hardening.
12. Operational release checklist.
