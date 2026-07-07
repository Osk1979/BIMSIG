# ADR-0016: Enterprise Licensing

## Status

Accepted

## Context

PROMPT MASTER 002 requires the Tower to administer licenses. Licensing controls must work across companies, users, projects, modules, integrations, and WEB SIG instances.

## Decision

Corporate Control Tower REV12 will implement company-scoped licensing with module entitlements.

License plans define which enterprise capabilities are enabled:

- Company administration.
- Project portfolio size.
- WEB SIG provisioning quota.
- User seats.
- KPI and alert modules.
- Executive dashboards.
- Report generation.
- AI capabilities.
- GeoServer/PostGIS/NAS/Google Drive integrations.

License enforcement belongs to the application layer through policy services. Domain models express entitlements and limits; API and infrastructure layers must not hard-code commercial rules.

## Consequences

Follow-up implementation must introduce:

- License plan model.
- Company license assignment.
- Entitlement checks.
- Usage counters.
- Audit events for license changes and limit violations.

## References

- ADR-0006: Authentication and authorization.
- ADR-0014: Enterprise multitenancy.
- PROMPT MASTER 002.
