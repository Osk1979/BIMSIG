# ADR-0014: Enterprise Multitenancy

## Status

Accepted

## Context

PROMPT MASTER 002 requires Corporate Control Tower REV12 to administer multiple companies. Each company administers multiple projects, and each project has one WEB SIG. The Tower must remain an enterprise platform and must not directly operate project-level workflows.

## Decision

Corporate Control Tower REV12 will be a multi-tenant enterprise platform with company-level tenancy.

The hierarchy is:

```text
Platform
  -> Company
      -> Project
          -> WEB SIG
```

Every durable business record that belongs to a tenant must be scoped by `company_id`. Project records must also carry `project_id`. Cross-company access is denied by default.

## Tenant Boundary Rules

- Users belong to one or more companies through memberships.
- Licenses are assigned at company level and consumed by enabled modules, users, projects, or WEB SIG instances.
- Portfolio, KPI, alert, report, dashboard, and audit data are partitioned by company.
- Platform administrators may operate across tenants only through explicit platform administration capabilities.
- Service accounts must be scoped to a company or to an approved platform integration role.

## Consequences

Follow-up migrations must introduce company, membership, license, and tenant-scoped project structures before production use.

All API routes that read or mutate tenant records must resolve company context before accessing persistence.

## References

- ADR-0006: Authentication and authorization.
- ADR-0013: Database schema and migrations.
- PROMPT MASTER 002.
