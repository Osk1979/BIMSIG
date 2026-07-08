# PROMPT MASTER 013 - Corporate GIS Intelligence Backlog

## Scope

Implement ADR-0013 Corporate GIS Intelligence as a Corporate Control Tower
domain for consuming, consolidating, visualizing, and analyzing WEB SIG spatial
publications.

## Delivery

| ID | Item | Status | Traceability |
| --- | --- | --- | --- |
| P13-001 | Add ADR local for Corporate GIS Intelligence | Done | ADR-0028 |
| P13-002 | Add `corporate_gis_intelligence` domain models | Done | `src/control_tower/domain/corporate_gis_intelligence` |
| P13-003 | Register WMS, WFS, WMTS, Vector Tiles, and GIS API source references | Done | `CorporateGisSource` |
| P13-004 | Register Corporate Layers | Done | `CorporateLayer` |
| P13-005 | Add Corporate GIS Summary service | Done | `CorporateGisIntelligenceService.summary` |
| P13-006 | Add corporate map and spatial indicator filters | Done | API contract |
| P13-007 | Integrate dashboard with GIS Intelligence summary | Done | `CorporateDashboard.gis_intelligence` |
| P13-008 | Add SQLAlchemy persistence and Alembic migration | Done | `20260708_012` |
| P13-009 | Add unit, contract, and persistence tests | Done | `tests/` |
| P13-010 | Regenerate versioned OpenAPI | Done | `docs/api/openapi.yaml` |

## Deferred

| ID | Item | Status | Reason |
| --- | --- | --- | --- |
| P13-101 | Live WMS/WFS/WMTS availability checks | Planned | Requires network-safe integration policy |
| P13-102 | Region geometry aggregation | Planned | Requires corporate region catalog |
| P13-103 | Vector tile tilejson validation | Planned | Requires provider-specific validation adapters |
| P13-104 | Dashboard map layer toggles by discipline/status/risk | Planned | Requires richer frontend interaction model |
