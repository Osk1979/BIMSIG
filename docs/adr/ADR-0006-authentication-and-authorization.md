# ADR-0006: Authentication and Authorization

## Status

Accepted

## Context

Corporate Control Tower governs the BIMSIG Enterprise portfolio and will later trigger provisioning actions that affect WEB SIG instances, NAS metadata, PostGIS state, GeoServer resources, and Google Workspace references. These actions require controlled access before the API becomes operational.

## Decision

Corporate Control Tower REV12 will use token-based authentication at the API boundary and role-based authorization inside the application layer.

The initial authorization model defines these roles:

- `platform_admin`: manages platform configuration, integrations, and operational recovery.
- `portfolio_manager`: registers projects, changes governance status, and approves provisioning.
- `project_operator`: reads assigned projects and submits operational updates.
- `auditor`: reads portfolio, provisioning, and audit records without write access.
- `service_account`: executes approved system-to-system integration tasks.

Authorization checks must be implemented in application services or dedicated policy modules. Domain models remain independent from authentication frameworks.

## Non-Negotiable Rules

- No production write endpoint may remain unauthenticated.
- Service accounts must have scoped permissions.
- Audit events must record actor identity for state-changing operations.
- Authentication provider details must be isolated behind infrastructure adapters.
- Secrets must come from environment variables or a secret manager, not source code.

## Initial Implementation Direction

The scaffold may keep unauthenticated endpoints for local contract tests while protected API behavior is developed. Before any production deployment, API routes must enforce authentication and role checks.

## Consequences

Follow-up implementation must add:

- Auth configuration.
- Role policy tests.
- API dependency for current actor resolution.
- Audit linkage between actor and state-changing command.

## References

- ADR-0001: REV11 as architecture baseline.
- ADR-0002: Layered modular API scaffold.
- ADR-0005: Persistence strategy.
