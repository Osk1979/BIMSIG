# F2 Corporate Control Tower Backlog

## Scope

This backlog covers F2 of the BIMSIG Enterprise master program: Corporate Control Tower as the
Corporate Governance System defined by REV13 and local ADR-0024.

## Delivery Rules

- Every implementation item must reference an ADR.
- Every module must include tests.
- Every public API must be documented.
- Every durable state decision must follow ADR-0005.
- GitHub must remain the versioned source of truth.
- A daily USB backup must be created according to ADR-0004.

## Milestone F2.0: Foundation

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| F2-001 | Create GitHub repository and local scaffold | Done | ADR-0001, ADR-0002 | Repo exists, `main` pushed, scaffold documented. |
| F2-002 | Register REV11 baseline and traceability | Done | ADR-0001 | Traceability document maps REV11 mandates to REV12 artifacts. |
| F2-003 | Add API scaffold and base tests | Done | ADR-0002, ADR-0003 | Health, project registration, and provisioning contracts pass tests. |
| F2-004 | Add daily USB backup procedure | Done | ADR-0004 | Script creates ZIP and checksum. |
| F2-005 | Add CI pipeline | Done | ADR-0002, ADR-0012 | GitHub Actions runs lint and tests on push and PR. |
| F2-006 | Adopt REV13 Corporate Governance baseline | Done | ADR-0024 | F2 scope reflects corporate, technology, functional, portfolio, and information governance. |

## Milestone F2.1: Durable Portfolio Registry

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| F2-101 | Define database schema ADR and Alembic migrations | Done | ADR-0005, ADR-0013 | Schema ADR accepted; migration workflow documented and initial revision exists. |
| F2-102 | Add repository ports for projects and provisioning | Done | ADR-0002, ADR-0005, ADR-0013 | Application services depend on interfaces, not concrete storage. |
| F2-103 | Implement SQLAlchemy project repository | Done | ADR-0005, ADR-0013 | Projects persist and reload across service restarts. |
| F2-104 | Implement provisioning request repository | Done | ADR-0003, ADR-0005, ADR-0013 | WEB SIG requests persist with status history. |
| F2-105 | Add audit event persistence | Done | ADR-0005, ADR-0006, ADR-0013 | Project and provisioning changes create queryable audit events. |
| F2-106 | Implement Corporate Portfolio Domain | Done | ADR-0009, ADR-0010, ADR-0025 | Customers, programs, project lifecycle, WEB SIG, NAS, GIS, and dashboard references are governed without operating WEB SIG. |

## Milestone F2.2: Governance API

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| F2-201 | Expand project API | Done | ADR-0002, ADR-0005 | Register/list/get/status endpoints documented in OpenAPI notes. |
| F2-202 | Add governance status workflow | Done | ADR-0001, ADR-0005, ADR-0006 | Projects can move through approved governance states. |
| F2-203 | Add portfolio dashboard read models | Done | ADR-0002, ADR-0005 | API returns counts, status summaries, and provisioning queue. |
| F2-204 | Export OpenAPI contract to `docs/api/openapi.yaml` | Done | ADR-0002, ADR-0012 | Contract is generated, committed, and checked by tests. |

## Milestone F2.3: Project Provisioning Engine

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| F2-301 | Define provisioning adapter contracts | Planned | ADR-0003 | Interfaces for GitHub, NAS, database, and GeoServer provisioning exist. |
| F2-302 | Create WEB SIG registry model | Planned | ADR-0001, ADR-0003, ADR-0005 | Tower can register WEB SIG instances per project. |
| F2-303 | Add dry-run provisioning plan endpoint | Planned | ADR-0003 | API returns planned actions without side effects. |
| F2-304 | Add provisioning request audit trail | Done | ADR-0003, ADR-0005, ADR-0006 | Provisioning requests are recorded and queryable through audit events. |

## Milestone F2.4: Enterprise Integrations

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| F2-401 | Define NAS adapter ADR | Done | ADR-0001, ADR-0005, ADR-0007 | Logical path and metadata contract accepted. |
| F2-402 | Define GeoServer adapter ADR | Done | ADR-0001, ADR-0005, ADR-0009 | Workspace/layer publication contract accepted. |
| F2-403 | Define Google Workspace transition ADR | Done | ADR-0001, ADR-0010 | Sync boundaries and ownership are documented. |
| F2-404 | Define authentication and authorization ADR | Done | ADR-0002, ADR-0006 | Roles and access model are accepted before protected APIs. |
| F2-405 | Define PostGIS integration ADR | Done | ADR-0001, ADR-0005, ADR-0008 | Spatial ownership and portfolio metadata scope are documented. |
| F2-406 | Define Corporate GIS Administration registry | Done | ADR-0023 | PostGIS schemas, GeoServer workspaces, datastores, layers, and project GIS bindings are governed. |
| F2-407 | Decide Google Workspace transition closure or permanence | Planned | ADR-0010, ADR-0024 | Architecture states whether Google Workspace is temporary or permanent. |

## Milestone F2.5: Operational Readiness

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| F2-501 | Add deployment ADR | Done | ADR-0002, ADR-0011 | Runtime target, environment variables, and release process accepted. |
| F2-502 | Add database backup and restore procedure | Planned | ADR-0005 | Restore drill is documented and testable. |
| F2-503 | Add observability baseline | Done | ADR-0021 | Health, readiness, version, request IDs, logs, and security headers are exposed. |
| F2-504 | Add release checklist | Done | ADR-0021 | Each release includes docs, code, tests, OpenAPI, Docker build, GitHub push, and USB backup. |
