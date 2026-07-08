# ADR-0029: Corporate Workflow Engine

## Status

Accepted

## Context

Corporate Control Tower REV13 requires an official orchestration layer for
corporate governance processes. ADR-0027 defines the operational flow, but the
platform also needs persisted workflow instances, auditable transitions, and
controlled rollback for the official sequence from company creation to project
archive.

The Tower must not implement WEB SIG project operation logic. It may govern,
register, provision, verify, and audit transitions across portfolio, WEB SIG
Factory, NAS, PostGIS, GeoServer, dashboard, users, specialties, activation,
operation, closure, and archive.

## Decision

Corporate Control Tower will include a `corporate_workflow` domain and a
`CorporateWorkflowEngine` application service.

The official stage sequence is:

1. `create_company`
2. `create_program`
3. `create_project`
4. `provision_websig`
5. `create_nas`
6. `create_postgis`
7. `register_geoserver`
8. `create_dashboard`
9. `assign_users`
10. `assign_specialties`
11. `activate_project`
12. `operation`
13. `closure`
14. `archive`

Each workflow instance is company-scoped and may be project-scoped. Each
transition is persisted in `corporate_workflow_transitions` and also written to
the audit event stream. Rollback is controlled by moving only to the previous
completed stage and recording a rollback transition linked to the prior
transition.

Portfolio lifecycle updates are applied only at corporate lifecycle boundaries:
activation and operation map to execution, closure maps to closure, and archive
maps to archived state.

## Consequences

The Tower gains a formal process engine without becoming the WEB SIG runtime.
Skipping stages is rejected by the application service and API. Rollback is
auditable and cannot jump arbitrarily across the sequence.

Future automation can attach adapter execution to a stage only through existing
governance ports, especially Project Provisioning Engine and WEB SIG Factory.

## References

- ADR-0015: Tower vs WEB SIG boundary.
- ADR-0017: Project Provisioning Engine.
- ADR-0025: Corporate Portfolio Domain.
- ADR-0026: WEB SIG Factory controlled provisioning.
- ADR-0027: Corporate Control Tower operational flow.
- ADR-0028: Corporate GIS Intelligence.
