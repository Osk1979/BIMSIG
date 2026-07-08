# ADR-0025: Corporate Portfolio Domain

## Status

Accepted

## Context

PROMPT MASTER 010 requires Corporate Control Tower to govern the complete corporate
portfolio lifecycle: companies, customers, programs, projects, statuses, lifecycle,
Project Provisioning Engine, WEB SIG Factory relationships, NAS, GIS, and dashboard.

REV13 positions the Tower as a Corporate Governance System. It must not operate the
project WEB SIG directly. GeoServer governance remains constrained by ADR-0009 and
Google Workspace references remain transitional under ADR-0010.

## Decision

Corporate Control Tower will implement a Corporate Portfolio Domain that:

- Registers customers and programs inside a company portfolio.
- Extends portfolio projects with customer, program, lifecycle, WEB SIG, NAS, GIS,
  and Google Workspace reference fields.
- Exposes lifecycle transitions as governance state changes.
- Provides an integrated project governance view that summarizes provisioning, NAS,
  GIS, and WEB SIG references.
- Stores only references to WEB SIG, NAS, GIS, and Google Workspace resources.

The Tower will not implement WEB SIG operational behavior. WEB SIG Factory and
Project Provisioning Engine remain responsible for creation/provisioning flows.

## Consequences

Portfolio persistence requires Alembic migration `20260708_010`.

Project records remain backward-compatible because new integration fields are
nullable and lifecycle defaults to `intake`.

Future dashboard work may consume the integrated portfolio governance view instead
of duplicating NAS/GIS/provisioning aggregation logic.

## References

- ADR-0009: GeoServer Integration.
- ADR-0010: Google Workspace Transition Integration.
- ADR-0015: Tower vs WEB SIG Boundary.
- ADR-0024: REV13 Corporate Governance Baseline.
