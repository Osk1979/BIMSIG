# F2 Corporate Control Tower Scope

## Objective

Implement Corporate Control Tower as the BIMSIG Enterprise portfolio governance layer.

## In Scope for Initial Scaffold

- Portfolio project registry.
- WEB SIG provisioning request model.
- Governance status model.
- Health endpoint.
- API contract documentation.
- ADR-based traceability.
- Unit and contract tests.

## Out of Scope Until Later ADRs

- Real NAS writes.
- Real PostGIS schema creation.
- Real GeoServer workspace creation.
- Real Google Workspace synchronization.
- Real GitHub repository creation.
- Production authentication and authorization.

## REV11 Traceability

This scope implements F2 from Documento B and respects the Corporate Control Tower responsibility defined in Documento A.

## PROMPT MASTER 002 Expansion

The complete Enterprise Tower architecture is defined in:

- `docs/architecture/prompt-002-enterprise-control-tower-architecture.md`
- `docs/architecture/prompt-002-domain-model.md`
- `docs/architecture/prompt-002-api-map.md`
- `docs/backlog/prompt-002-enterprise-build-backlog.md`

PROMPT MASTER 002 expands the Tower from an initial portfolio/provisioning scaffold into a multi-company enterprise platform while preserving the rule that WEB SIG operates projects and the Tower consumes consolidated information.
