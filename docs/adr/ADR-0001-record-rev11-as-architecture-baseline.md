# ADR-0001: Record REV11 as Architecture Baseline

## Status

Accepted

## Context

Corporate Control Tower REV12 must implement the approved BIMSIG Enterprise architecture. The available approved source documents are:

- Documento A - Arquitectura Maestra BIMSIG Enterprise REV11
- Documento B - Programa Maestro de Desarrollo REV11
- Documento C - Manual Oficial de Prompts REV11

These documents define Corporate Control Tower as the portfolio governance layer and Project Provisioning Engine as the mechanism that creates new WEB SIG instances.

## Decision

REV12 implementation will treat the REV11 documents as the architecture baseline until superseded by an approved ADR.

No code module may redefine the following principles:

- WEB SIG administers the project.
- Corporate Control Tower administers the portfolio.
- Each project has its own WEB SIG.
- Corporate Control Tower creates and registers WEB SIG instances.
- NAS, PostGIS, and GeoServer are the information core.
- Google Workspace integration is transitional.
- PWA field workflows and AI are cross-cutting platform capabilities.

## Consequences

Implementation can refine internal code structure, but architectural changes require a new ADR before code changes.
