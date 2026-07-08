# PROMPT MASTER 010 - Corporate Portfolio Domain Backlog

## Scope

Implement the Corporate Portfolio Domain as the governance layer for companies,
customers, programs, projects, lifecycle, provisioning references, WEB SIG Factory
relationships, NAS, GIS, and dashboard consumption.

The Tower governs and provisions. It does not operate WEB SIG.

## Delivery

| ID | Item | Status | Traceability |
| --- | --- | --- | --- |
| P10-001 | Add ADR for Corporate Portfolio Domain | Done | ADR-0025 |
| P10-002 | Model corporate customers and programs | Done | ADR-0025 |
| P10-003 | Extend portfolio projects with lifecycle and integration references | Done | ADR-0009, ADR-0010, ADR-0025 |
| P10-004 | Add lifecycle transition service | Done | ADR-0025 |
| P10-005 | Add integrated portfolio governance view | Done | ADR-0009, ADR-0010, ADR-0025 |
| P10-006 | Add API endpoints for customers, programs, lifecycle, and governance view | Done | OpenAPI |
| P10-007 | Add Alembic migration for formal persistence | Done | `20260708_010` |
| P10-008 | Add unit, contract, and persistence tests | Done | `tests/` |

## Deferred

| ID | Item | Status | Reason |
| --- | --- | --- | --- |
| P10-101 | Dashboard widgets backed by the new governance view | Planned | Prompt 004 dashboard can consume this in a focused increment |
| P10-102 | Real WEB SIG Factory execution adapter enrichment | Planned | Must remain behind provisioning ports |
| P10-103 | Google Workspace synchronization job | Planned | ADR-0010 requires idempotent, auditable sync design |
