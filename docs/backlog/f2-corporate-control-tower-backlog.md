# F2 Corporate Control Tower Backlog

## Scope

This backlog covers F2 of the BIMSIG Enterprise master program: Corporate Control Tower and Project Provisioning Engine.

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

## Milestone F2.1: Durable Portfolio Registry

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| F2-101 | Define database schema ADR and migrations | Done | ADR-0005, ADR-0013 | Schema ADR accepted; migration workflow documented. |
| F2-102 | Add repository ports for projects and provisioning | Done | ADR-0002, ADR-0005, ADR-0013 | Application services depend on interfaces, not concrete storage. |
| F2-103 | Implement SQLAlchemy project repository | Done | ADR-0005, ADR-0013 | Projects persist and reload across service restarts. |
| F2-104 | Implement provisioning request repository | Done | ADR-0003, ADR-0005, ADR-0013 | WEB SIG requests persist with status history. |
| F2-105 | Add audit event persistence | Planned | ADR-0005 | Project and provisioning changes create queryable audit events. |

## Milestone F2.2: Governance API

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| F2-201 | Expand project API | Planned | ADR-0002, ADR-0005 | CRUD/list/status endpoints documented in OpenAPI. |
| F2-202 | Add governance status workflow | Planned | ADR-0001, ADR-0005 | Projects can move through approved governance states. |
| F2-203 | Add portfolio dashboard read models | Planned | ADR-0002, ADR-0005 | API returns counts, status summaries, and provisioning queue. |
| F2-204 | Export OpenAPI contract to `docs/api/openapi.yaml` | Planned | ADR-0002 | Contract is generated and committed. |

## Milestone F2.3: Project Provisioning Engine

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| F2-301 | Define provisioning adapter contracts | Planned | ADR-0003 | Interfaces for GitHub, NAS, database, and GeoServer provisioning exist. |
| F2-302 | Create WEB SIG registry model | Planned | ADR-0001, ADR-0003, ADR-0005 | Tower can register WEB SIG instances per project. |
| F2-303 | Add dry-run provisioning plan endpoint | Planned | ADR-0003 | API returns planned actions without side effects. |
| F2-304 | Add provisioning execution audit trail | Planned | ADR-0003, ADR-0005 | Every provisioning step is recorded and queryable. |

## Milestone F2.4: Enterprise Integrations

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| F2-401 | Define NAS adapter ADR | Done | ADR-0001, ADR-0005, ADR-0007 | Logical path and metadata contract accepted. |
| F2-402 | Define GeoServer adapter ADR | Done | ADR-0001, ADR-0005, ADR-0009 | Workspace/layer publication contract accepted. |
| F2-403 | Define Google Workspace transition ADR | Done | ADR-0001, ADR-0010 | Sync boundaries and ownership are documented. |
| F2-404 | Define authentication and authorization ADR | Done | ADR-0002, ADR-0006 | Roles and access model are accepted before protected APIs. |
| F2-405 | Define PostGIS integration ADR | Done | ADR-0001, ADR-0005, ADR-0008 | Spatial ownership and portfolio metadata scope are documented. |

## Milestone F2.5: Operational Readiness

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| F2-501 | Add deployment ADR | Done | ADR-0002, ADR-0011 | Runtime target, environment variables, and release process accepted. |
| F2-502 | Add database backup and restore procedure | Planned | ADR-0005 | Restore drill is documented and testable. |
| F2-503 | Add observability baseline | Planned | ADR-0002 | Health, logs, and error reporting are documented. |
| F2-504 | Add release checklist | Planned | ADR-0001 | Each release includes docs, code, tests, version, GitHub push, and USB backup. |
