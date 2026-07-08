# PROMPT MASTER 009 - Corporate GIS Administration Backlog

## Scope

Evolve Corporate Control Tower REV12 from backend functionality into corporate GIS governance.

## Items

| ID | Item | Status | Traceability |
| --- | --- | --- | --- |
| P9-001 | Add corporate GIS domain model | Done | ADR-0023 |
| P9-002 | Register PostGIS schemas | Done | ADR-0008, ADR-0023 |
| P9-003 | Register GeoServer workspaces | Done | ADR-0009, ADR-0023 |
| P9-004 | Register GeoServer datastores | Done | ADR-0009, ADR-0023 |
| P9-005 | Register GeoServer layers with WMS/WFS references | Done | ADR-0009, ADR-0023 |
| P9-006 | Bind project, PostGIS schema, and GeoServer workspace | Done | ADR-0017, ADR-0023 |
| P9-007 | Add company/project scoped GIS API | Done | ADR-0023 |
| P9-008 | Add basic registry validation | Done | ADR-0023 |
| P9-009 | Add Alembic migration | Done | ADR-0013, ADR-0023 |
| P9-010 | Add unit and contract tests | Done | ADR-0023 |

## Out Of Scope

- WEB SIG operational publishing.
- Editing project geospatial datasets.
- GeoServer layer styling workflows.
- Direct map operation from Corporate Control Tower.
