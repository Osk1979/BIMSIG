# ADR-0002: Layered Modular API Scaffold

## Status

Accepted

## Context

F2 requires Corporate Control Tower services while preserving separation from WEB SIG operational modules.

## Decision

The scaffold uses a layered modular structure:

- `domain`: pure business concepts and invariants.
- `application`: use cases and orchestration.
- `api`: HTTP boundary and DTO mapping.
- `infrastructure`: adapters for NAS, GitHub, PostGIS, GeoServer, and Google Workspace.

## Consequences

Domain modules must not import API or infrastructure modules. External systems are represented by ports/adapters until concrete integrations are approved by later ADRs.
