# PROMPT MASTER 011 - WEB SIG Factory / Advanced Provisioning Backlog

## Scope

Govern controlled creation of WEB SIG instances through Corporate Control Tower.
The Tower plans, approves, provisions references, and audits. It does not operate
WEB SIG.

## Delivery

| ID | Item | Status | Traceability |
| --- | --- | --- | --- |
| P11-001 | Add ADR for controlled WEB SIG Factory provisioning | Done | ADR-0026 |
| P11-002 | Add WEB SIG Factory blueprint model | Done | `WebSigFactoryBlueprint` |
| P11-003 | Add dry-run WEB SIG Factory endpoint | Done | `/api/v1/companies/{company_id}/websig-factory/dry-run` |
| P11-004 | Add controlled execute WEB SIG Factory endpoint | Done | `/api/v1/companies/{company_id}/websig-factory/execute` |
| P11-005 | Require approval for controlled execution | Done | `approved_by` |
| P11-006 | Persist execution mode and approver | Done | Alembic `20260708_011` |
| P11-007 | Update portfolio project WEB SIG, NAS, and GIS references after execution | Done | ADR-0025, ADR-0026 |
| P11-008 | Add unit, API, migration, and persistence tests | Done | `tests/` |

## Deferred

| ID | Item | Status | Reason |
| --- | --- | --- | --- |
| P11-101 | Real WEB SIG application scaffold generation | Planned | Must remain behind factory adapters and avoid creating independent apps |
| P11-102 | Real GeoServer/PostGIS/NAS integration tests against Docker services | Planned | Requires controlled local service orchestration |
| P11-103 | Approval workflow with named roles and digital signatures | Planned | Requires security policy expansion |
