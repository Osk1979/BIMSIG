# ADR-0017: Project Provisioning Engine

## Status

Accepted

## Context

PROMPT MASTER 003 requires BIMSIG Enterprise to provision a complete project stack from Corporate Control Tower without creating independent applications. The engine must coordinate enterprise records, project registration, WEB SIG, PostGIS, NAS, document structure, GeoServer, dashboard, users, roles, and catalogs.

Existing ADRs already constrain the implementation:

- ADR-0003 defines provisioning as an application port.
- ADR-0007 keeps NAS as logical enterprise storage.
- ADR-0008 keeps WEB SIG operational GIS data outside Tower ownership.
- ADR-0009 allows approved GeoServer workspace registration.
- ADR-0014 requires enterprise multitenancy.
- ADR-0015 preserves the Tower vs WEB SIG boundary.

## Decision

Corporate Control Tower REV12 adds `ProjectProvisioningEngine` inside the existing BIMSIG Enterprise application service layer.

The implementation provisions the control-plane registry automatically:

- Registers or updates the company.
- Registers the project inside the company.
- Registers users and company roles.
- Records logical references for WEB SIG, PostGIS, NAS, document structure, GeoServer, dashboard, and catalogs.
- Marks the project as active when the stack registry is provisioned.
- Stores auditable provisioning steps in the durable provisioning registry.

External infrastructure actions remain adapter-owned. The engine exposes a dry-run path that returns planned steps without state changes and an execution path that calls configured adapters.

Initial adapters are:

- NAS filesystem adapter, enabled with `CONTROL_TOWER_NAS_ROOT`.
- Document structure filesystem adapter, enabled with `CONTROL_TOWER_NAS_ROOT`.
- PostGIS schema adapter, enabled with `CONTROL_TOWER_POSTGIS_DATABASE_URL`.
- GeoServer workspace adapter, enabled with `CONTROL_TOWER_GEOSERVER_URL` and optional credentials.
- Reference adapters for WEB SIG, dashboard, and catalogs.

When an external adapter is not configured, the engine still records the approved logical reference instead of attempting uncontrolled side effects.

## Consequences

The WEB SIG is considered operational from the Tower control-plane perspective when all required registry steps are persisted and audited.

Production side effects must be enabled only by explicit environment configuration and must remain covered by adapter contract tests.

No separate application or service is created for Prompt 003.
