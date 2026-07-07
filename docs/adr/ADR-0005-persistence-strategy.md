# ADR-0005: Persistence Strategy

## Status

Accepted

## Context

Corporate Control Tower REV12 must govern the portfolio and register WEB SIG provisioning activity. The REV11 architecture establishes NAS, PostGIS, and GeoServer as the enterprise information core, but the initial scaffold currently stores portfolio and provisioning state in memory.

The implementation needs a persistence direction before expanding APIs and use cases.

## Decision

Corporate Control Tower REV12 will use PostgreSQL as the primary transactional database and enable PostGIS for geospatial metadata, spatial project references, and future portfolio map views.

The NAS remains the enterprise master repository for files and deliverables. The database stores metadata, registry state, governance status, audit events, references to NAS logical paths, and references to GeoServer resources. It must not duplicate managed file binaries.

The application layer will depend on repository ports. Infrastructure modules will provide PostgreSQL/PostGIS adapters after schema ADRs and migrations are defined.

## Initial Persistence Boundaries

Persisted by PostgreSQL/PostGIS:

- Portfolio projects.
- WEB SIG provisioning requests.
- Governance status.
- Audit events.
- NAS logical path references.
- GeoServer workspace/layer references.
- Google Workspace synchronization references, when approved.

Stored in NAS:

- Source files.
- Deliverables.
- BIM/GIS/CDE artifacts.
- Backup exports.

Managed by GeoServer:

- Published geospatial workspaces.
- Published layers and services.

## Consequences

The current in-memory services remain acceptable for scaffold and contract tests only. Production workflows must introduce repository interfaces, migrations, and PostgreSQL/PostGIS adapters before they are treated as durable.

Follow-up ADRs are required for:

- Database schema and migration tool.
- Authentication and authorization.
- NAS adapter contract.
- GeoServer adapter contract.
- Backup and restore policy for database state.

## References

- ADR-0001: REV11 as architecture baseline.
- ADR-0002: Layered modular API scaffold.
- Documento A - Arquitectura Maestra REV11: NAS + PostGIS + GeoServer as information core.
