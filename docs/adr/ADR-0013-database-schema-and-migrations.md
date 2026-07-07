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

Schema creation is performed by infrastructure bootstrapping in the initial implementation. Formal migration tooling is required before production deployment.

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

## Migration Rule

`metadata.create_all()` is acceptable only for scaffold, local development, and CI. Production requires an explicit migration tool and reviewed migration scripts before deployment.

## Consequences

Application services depend on repository ports, not SQLAlchemy. Infrastructure owns SQLAlchemy engines, sessions, table definitions, and database-specific behavior.

Follow-up work must add:

- Alembic or equivalent migration workflow.
- PostGIS geometry columns for portfolio spatial metadata.
- Audit event table.
- Database backup and restore procedure.

## References

- ADR-0002: Layered modular API scaffold.
- ADR-0005: Persistence strategy.
- ADR-0008: PostGIS integration.
- ADR-0011: Deployment strategy.
