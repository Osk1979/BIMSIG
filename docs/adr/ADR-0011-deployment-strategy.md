# ADR-0011: Deployment Strategy

## Status

Accepted

## Context

Corporate Control Tower REV12 needs a deployment direction before production integrations are introduced. The available REV11 documents define platform responsibilities but do not prescribe a runtime host.

## Decision

Corporate Control Tower REV12 will be packaged as a Python API service and deployed as a containerized service when moving beyond local development.

The deployment unit is the API service plus its environment configuration. PostgreSQL/PostGIS, NAS, GeoServer, and Google Workspace remain external dependencies.

## Environments

The project will distinguish:

- `local`: developer machine, in-memory or local adapter defaults.
- `staging`: integration validation with non-production external services.
- `production`: controlled operational deployment.

## Configuration Rules

- Runtime configuration must come from environment variables.
- Secrets must not be committed.
- Environment-specific values must not be hard-coded in domain or application modules.
- Health checks must expose service status without leaking secrets.
- Deployment changes require tests and documentation.

## Consequences

Follow-up work must add:

- Container build definition.
- Environment variable documentation.
- Staging deployment procedure.
- Production release checklist.
- Rollback procedure.

## References

- ADR-0002: Layered modular API scaffold.
- ADR-0005: Persistence strategy.
- ADR-0006: Authentication and authorization.
