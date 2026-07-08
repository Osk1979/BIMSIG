# ADR-0026: WEB SIG Factory Controlled Provisioning

## Status

Accepted

## Context

PROMPT MASTER 011 requires WEB SIG Factory and advanced Project Provisioning so the
Corporate Control Tower can govern controlled creation of new WEB SIG instances.

The Tower must not operate WEB SIG. It governs intent, blueprint, approval,
provisioning references, and audit.

## Decision

Corporate Control Tower will add a controlled WEB SIG Factory workflow:

- Dry-run plans are available without side effects.
- Controlled execution requires `approved_by`.
- A WEB SIG Factory blueprint defines template, slug, URL, NAS root, PostGIS schema,
  GeoServer workspace, and enabled modules.
- Execution records governance gate and blueprint steps.
- Execution updates portfolio project references for WEB SIG, NAS, and GIS so the
  dashboard can report governed readiness.

## Consequences

Provisioning requests persist `execution_mode` and `approved_by` through Alembic
migration `20260708_011`.

Existing project-stack provisioning also follows the controlled execution gate.

The Tower continues to store references only. It does not publish layers, edit WEB
SIG business logic, or administer project operations.

## References

- ADR-0003: Project provisioning as a port.
- ADR-0007: NAS integration.
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0015: Tower vs WEB SIG boundary.
- ADR-0017: Project Provisioning Engine.
- ADR-0025: Corporate Portfolio Domain.
