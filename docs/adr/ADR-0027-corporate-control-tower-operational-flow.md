# ADR-0027: Corporate Control Tower Operational Flow

## Status

Accepted

## Context

Corporate Control Tower REV12/REV13 must operate as the Corporate Governance
System for BIMSIG Enterprise. The Tower already governs portfolio, WEB SIG
Factory provisioning, NAS references, GIS references, dashboard visibility,
audit, DevSecOps, and physical backups.

The next operational need is a single governed flow that defines how an
enterprise portfolio event moves from intake to executive control without
turning the Tower into a project operations application.

## Decision

Corporate Control Tower will use a formal operational flow with these phases:

1. Corporate intake and identity.
2. Governance qualification.
3. Portfolio lifecycle registration.
4. Controlled WEB SIG Factory planning.
5. Approval gate.
6. Controlled provisioning execution.
7. Reference registration for WEB SIG, NAS, GIS, PostGIS, GeoServer, and
   Google Workspace.
8. Executive dashboard publication.
9. Operational monitoring and audit.
10. Release, backup, and continuity.

The flow is documented in
`docs/operations/corporate-control-tower-operational-flow.md`.

## Consequences

The Tower continues to govern, register, provision, validate, observe, audit,
and report. It does not operate project production workflows and does not
become an independent WEB SIG, NAS, GeoServer, PostGIS, Google Workspace, or
BIMSIG Field application.

Future endpoints and adapters must reference this flow when they affect
corporate intake, provisioning, dashboard readiness, audit, or continuity.

## References

- ADR-0014: Enterprise multitenancy.
- ADR-0015: Tower vs WEB SIG boundary.
- ADR-0017: Project Provisioning Engine.
- ADR-0019: NAS Corporate Information Center.
- ADR-0021: DevSecOps operating model.
- ADR-0022: Permanent architecture governance rule.
- ADR-0023: Corporate GIS Administration.
- ADR-0024: REV13 corporate governance baseline.
- ADR-0025: Corporate Portfolio Domain.
- ADR-0026: WEB SIG Factory controlled provisioning.
