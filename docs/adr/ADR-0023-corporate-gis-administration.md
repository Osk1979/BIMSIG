# ADR-0023: Corporate GIS Administration

## Status

Accepted

## Context

PROMPT MASTER 009 requires Corporate Control Tower REV12 to administer GeoServer and PostGIS as
corporate infrastructure. The Tower must govern, register, provision, and verify GIS resources
without taking over WEB SIG operations.

ADR-0008 defines PostGIS as enterprise geospatial infrastructure. ADR-0009 defines GeoServer
integration boundaries. ADR-0015 states that WEB SIG owns operational project GIS behavior.

## Decision

Corporate Control Tower REV12 will add a corporate GIS registry inside the existing Enterprise
architecture.

The registry persists:

- Project PostGIS schema references.
- GeoServer workspace references.
- GeoServer datastore references.
- GeoServer layer references.
- WMS and WFS service URLs.
- Project bindings that relate project, PostGIS schema, and GeoServer workspace.

The application service validates registry consistency only. It does not publish operational
layers, edit geospatial datasets, or replace WEB SIG operation.

## API Scope

The API exposes company and project scoped GIS administration endpoints for:

- Registering PostGIS schemas.
- Registering GeoServer workspaces.
- Registering datastores.
- Registering layers.
- Consulting project GIS resources.
- Binding project GIS infrastructure.
- Running basic registry validation.

## Consequences

- Corporate GIS resources become auditable and queryable by company and project.
- Provisioning can register infrastructure references after creating PostGIS schemas and GeoServer
  workspaces.
- WEB SIG remains the owner of operational GIS editing, publication rules, and day-to-day project
  map operations.

## Traceability

- PROMPT MASTER 009: Corporate GIS Administration.
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0015: Tower vs WEB SIG boundary.
- ADR-0017: Project Provisioning Engine.
- ADR-0022: Permanent architecture governance rule.
