# ADR-0015: Tower vs WEB SIG Operational Boundary

## Status

Accepted

## Context

PROMPT MASTER 002 states that every project has a WEB SIG and that the Tower never directly administers project operation. This boundary protects the enterprise architecture from mixing portfolio governance with operational project execution.

## Decision

Corporate Control Tower REV12 governs the portfolio and consumes consolidated information. WEB SIG owns operational project workflows.

The Tower may:

- Register companies, projects, licenses, users, and WEB SIG instances.
- Request, track, and audit WEB SIG provisioning.
- Consume consolidated KPIs, alerts, reports, and health status from WEB SIG.
- Display executive dashboards.
- Coordinate integrations with NAS, PostGIS, GeoServer, Google Drive, and AI.
- Enforce enterprise security, licensing, and audit controls.

The Tower must not:

- Edit operational project GIS layers directly.
- Replace WEB SIG field workflows.
- Approve detailed project deliverables as an operational system of record.
- Mutate project-level CDE files outside approved enterprise metadata or provisioning flows.
- Bypass WEB SIG APIs or adapters for project operations.

## Consequences

All operational project commands must be routed to the responsible WEB SIG or integration adapter. The Tower stores consolidated facts, references, statuses, and audit trails.

## References

- ADR-0001: REV11 as architecture baseline.
- ADR-0003: Project provisioning as a port.
- ADR-0007: NAS integration.
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- PROMPT MASTER 002.
