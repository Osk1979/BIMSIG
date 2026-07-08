# ADR-0019: NAS Corporate Information Center

## Status

Accepted

## Context

PROMPT MASTER 005 requires the NAS module to be designed as the Corporate Information Center, not as simple storage. It must integrate NAS, versioning, snapshots, backups, Google Drive, GeoServer, PostGIS, Docker, documentation, IFC, DWG, LandXML, photography, videos, Shapefile, GeoJSON, permissions, and metadata.

Existing ADRs define key boundaries:

- ADR-0007 establishes NAS as the master information repository.
- ADR-0008 defines PostGIS as geospatial infrastructure.
- ADR-0009 defines GeoServer integration boundaries.
- ADR-0010 keeps Google Drive transitional and non-authoritative.
- ADR-0014 requires company-scoped tenancy.

## Decision

Corporate Control Tower REV12 adds a `nas` domain module and a `NasInformationCenterService`.

The Tower stores corporate information registry records:

- Logical NAS URI.
- Company and optional project scope.
- Corporate category: BIM, GIS, CDE, Field, QA/QC, Environmental, SSOMA, or PMO.
- Asset type.
- Version and document lifecycle status: draft, review, approved, or archived.
- Metadata.
- Permissions.
- Checksums.
- Google Drive, GeoServer, PostGIS, and Docker references.
- Snapshot manifests.
- Backup manifests.

The NAS remains the source of truth for binaries. Corporate Control Tower governs references, metadata, permissions, version registry, snapshots, and backups.

## Consequences

The first implementation is a durable registry and governance layer. It does not copy or mutate large binaries directly through the API.

Future adapter work may validate physical NAS paths, calculate file hashes, synchronize Google Drive references, and verify GeoServer/PostGIS/Docker resources.
