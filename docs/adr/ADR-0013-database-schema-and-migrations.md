# ADR-0013: Database Schema and Migrations

## Status

Accepted

## Context

ADR-0005 selects PostgreSQL with PostGIS as the durable persistence direction for Corporate Control Tower REV12. The scaffold currently has portfolio and provisioning use cases and needs a first real persistence adapter without breaking the layered architecture.

## Decision

Corporate Control Tower REV12 will introduce SQLAlchemy-based repositories for durable state. PostgreSQL is the production database target. SQLite may be used only for fast local and CI tests of repository behavior.

The first schema contains:

- `portfolio_projects`: portfolio-level project registry.
- `provisioning_requests`: Project Provisioning Engine request registry.
- `audit_events`: state-changing action log.

Schema changes are managed with Alembic migrations. Infrastructure bootstrapping may still use `metadata.create_all()` only as an explicit dev/test fallback.

## Initial Tables

### `portfolio_projects`

| Column | Purpose |
| --- | --- |
| `project_id` | Stable project identifier and primary key. |
| `name` | Project display name. |
| `cui` | Optional project CUI. |
| `status` | Portfolio governance status. |
| `created_at` | First persistence timestamp. |
| `updated_at` | Last persistence timestamp. |

### `provisioning_requests`

| Column | Purpose |
| --- | --- |
| `request_id` | Stable provisioning request identifier and primary key. |
| `project_id` | Project receiving a dedicated WEB SIG. |
| `target_revision` | Target WEB SIG revision. |
| `status` | Provisioning request status. |
| `created_at` | First persistence timestamp. |
| `updated_at` | Last persistence timestamp. |

### `audit_events`

| Column | Purpose |
| --- | --- |
| `event_id` | Stable audit event primary key. |
| `actor` | Actor responsible for the operation. |
| `action` | State-changing action name. |
| `entity_type` | Entity category affected by the action. |
| `entity_id` | Entity identifier affected by the action. |
| `detail` | Optional human-readable detail. |
| `created_at` | Event timestamp. |

## Migration Rule

Alembic is the formal migration tool. Production and staging schema changes must be applied through committed Alembic revision files.

`metadata.create_all()` is acceptable only as a scaffold, local development, or CI fallback. It is not a production migration path.

## Consequences

Application services depend on repository ports, not SQLAlchemy. Infrastructure owns SQLAlchemy engines, sessions, table definitions, and database-specific behavior.

Follow-up work must add:

- PostGIS geometry columns for portfolio spatial metadata.
- Database backup and restore procedure.

## References

- ADR-0002: Layered modular API scaffold.
- ADR-0005: Persistence strategy.
- ADR-0008: PostGIS integration.
- ADR-0011: Deployment strategy.
