# PROMPT MASTER 005 NAS Information Center Backlog

## Goal

Design and build the NAS module as the Corporate Information Center for BIMSIG Enterprise.

## Milestone P5.1: Corporate Information Registry

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| P5-101 | Add NAS information domain model | Done | ADR-0019 | Domain supports assets, versions, snapshots, backups, permissions, metadata, and external references. |
| P5-102 | Add asset registry API | Done | ADR-0019 | Company-scoped API registers and lists information assets. |
| P5-103 | Add version registry | Done | ADR-0019 | Assets can register immutable version records. |
| P5-104 | Add snapshot registry | Done | ADR-0019 | Company/project information snapshots can be created and listed. |
| P5-105 | Add backup registry | Done | ADR-0019 | Backup manifests can be registered and listed. |
| P5-106 | Add permissions and metadata operations | Done | ADR-0019 | API can update asset permissions and metadata. |

## Milestone P5.2: Information Types and Integrations

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| P5-201 | Support BIM/CAD/geospatial/media asset types | Done | ADR-0019 | IFC, DWG, LandXML, photography, video, Shapefile, GeoJSON, and documentation are typed. |
| P5-202 | Register Google Drive references | Done | ADR-0010, ADR-0019 | Assets can store transitional Google Drive identifiers. |
| P5-203 | Register GeoServer references | Done | ADR-0009, ADR-0019 | Assets can store GeoServer references. |
| P5-204 | Register PostGIS references | Done | ADR-0008, ADR-0019 | Assets can store PostGIS references. |
| P5-205 | Register Docker references | Done | ADR-0017, ADR-0019 | Assets can store Docker/runtime references. |

## Milestone P5.3: Physical Validation and Automation

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| P5-301 | Add physical NAS adapter validation | Planned | ADR-0007, ADR-0019 | Adapter validates logical URI to physical path mapping without exposing local paths. |
| P5-302 | Add checksum calculation adapter | Planned | ADR-0007, ADR-0019 | Adapter calculates SHA256 for registered binaries. |
| P5-303 | Add Drive sync metadata adapter | Planned | ADR-0010, ADR-0019 | Adapter verifies Google Drive folder/file references. |
| P5-304 | Add GeoServer/PostGIS validation | Planned | ADR-0008, ADR-0009, ADR-0019 | Adapter validates referenced geospatial resources. |
| P5-305 | Add retention policy engine | Planned | ADR-0004, ADR-0019 | Snapshots and backups follow retention and audit policy. |
