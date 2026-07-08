# ADR-0024: Adopt REV13 Corporate Governance Baseline

## Status

Accepted

## Context

The REV13 master documents update the official BIMSIG Enterprise architecture.
Documento A REV13 defines Corporate Control Tower as the Corporate Governance System for BIMSIG
Enterprise, not as an ERP and not as a simple executive dashboard.

REV13 also introduces or formalizes additional enterprise pillars:

- WEB SIG SUITE as the operational system for each project.
- WEB SIG Factory as the Project Provisioning Engine phase.
- NAS, PostGIS, and GeoServer as the information core.
- BIMSIG Field as an offline-capable PWA.
- Discipline Hub.
- Corporate CDE.
- Integrated BIM Platform.
- PMO Digital.
- Transversal AI.
- Digital Twin.
- Commercialization of BIMSIG Enterprise as a product.

Documento A REV13 calls this decision `ADR-0009`. In this repository, `ADR-0009` already exists as
GeoServer Integration. Renumbering existing accepted ADRs would break local traceability.

## Decision

Corporate Control Tower REV12 will adopt REV13 as the current master architecture baseline through
this repository ADR, `ADR-0024`.

Local ADR numbering remains stable. The REV13 `ADR-0009` is mapped to local `ADR-0024`.

Corporate Control Tower scope is expanded and clarified as:

- Corporate governance: companies, clients, contracts, portfolio, and project lifecycle.
- Technology governance: WEB SIG Factory, NAS, GeoServer, PostGIS, APIs, DevSecOps, and integrations.
- Functional governance: users, roles, licenses, catalogs, permissions, and service access.
- Portfolio governance: KPIs, alerts, risks, comparisons, closures, and archives.
- Information governance: metadata, audit, traceability, continuity, CDE, and records.

The Tower must not administer daily project operation. WEB SIG SUITE remains the operational system
for each project.

## Consequences

- Future prompts must reference REV13 when changing architecture or phase scope.
- Guardrails must include the REV13 pillars.
- Backlogs must distinguish F2 Corporate Control Tower from F3 WEB SIG Factory and F4 WEB SIG
  Operacional.
- Google Workspace remains a pending architectural decision: transition integration or permanent
  integration must be decided in a future ADR.
- No existing ADR is renumbered.

## Traceability

- Documento A - Arquitectura Maestra BIMSIG Enterprise REV13.
- Documento B - Programa Maestro de Desarrollo REV13.
- Documento C - Manual Oficial de Prompts REV13.
- REV13 ADR-0009 maps to this repository ADR-0024.
- ADR-0022: Permanent architecture governance rule.
