# ADR-0022: Permanent Architecture Governance Rule

## Status

Accepted

## Context

PROMPT MASTER 008 establishes a permanent rule: before writing code, the Master Architecture must
be verified and no Enterprise structure may be broken.

New functionality must integrate with Corporate Control Tower, WEB SIG Factory, Project
Provisioning Engine, PostGIS, GeoServer, NAS, Google Workspace, and BIMSIG Field while preserving
scalability for hundreds of simultaneous projects.

## Decision

Corporate Control Tower REV12 will treat architecture verification as a required DevSecOps control.

Before implementing code, each change must verify:

- ADR-0001 as the Master Architecture baseline.
- ADR-0015 for the Tower vs WEB SIG operational boundary.
- ADR-0017 for Project Provisioning Engine integration.
- ADR-0005, ADR-0007, ADR-0008, ADR-0009, and ADR-0010 for persistence, NAS, PostGIS,
  GeoServer, and Google Workspace integration.
- ADR-0021 for DevSecOps delivery controls.

The repository will include an automated architecture guardrail script:

```bash
python scripts/validate_architecture.py
```

The guardrail checks required architecture artifacts, traceability terms, and prevents new
independent application directories for WEB SIG or BIMSIG Field. New modules must be integrated
through the existing Enterprise layers and adapters.

## Scalability Rule

All new features must be designed for hundreds of simultaneous projects by default:

- Company and project scope must be explicit where data is project-related.
- Long-running integration work must go through controlled provisioning or adapter boundaries.
- External systems must be referenced through ports/adapters, not hard-coded direct coupling.
- The Tower must consume consolidated information and must not take over project operations.

## Consequences

- Architectural drift becomes testable in CI/CD.
- New prompts must add ADR/backlog/traceability entries before or with implementation.
- Features that require a new application boundary need a new ADR and explicit approval.
- Violations block release until corrected or superseded by an accepted ADR.

## Traceability

- PROMPT MASTER 008: Regla Permanente.
- Documento A: Arquitectura Maestra REV11.
- ADR-0001: REV11 architecture baseline.
- ADR-0015: Tower vs WEB SIG boundary.
- ADR-0017: Project Provisioning Engine.
- ADR-0021: DevSecOps operating model.
