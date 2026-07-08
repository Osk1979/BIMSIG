# ADR-0030: Enterprise Wizard

## Status

Accepted

## Context

Corporate Control Tower REV13 needs a guided enterprise assistant to create a
complete new project from corporate intake through activation. The assistant
must support partial progress, independent step validation, later resume, and
integration with the Corporate Workflow Engine.

The Tower must not embed WEB SIG operational logic or replace the WEB SIG
Factory, NAS, PostGIS, GeoServer, or project execution applications.

## Decision

The platform will add an `enterprise_wizard` domain with persisted wizard
sessions. Each session stores step states as structured JSON and exposes API
operations to start, list, resume, validate a step, save a step, and activate a
ready wizard.

The official steps are:

1. Empresa
2. Programa
3. Proyecto
4. Ubicacion
5. Especialidades
6. WEB SIG
7. GIS
8. NAS
9. Usuarios
10. Activacion

Validation rules are centralized as step definitions in the domain layer. The
API and future UI consume those domain rules instead of duplicating hardcoded
logic.

Activation creates governed enterprise records through existing services:
Company, Program, Portfolio Project, Users, Memberships, and Corporate
Workflow. WEB SIG, GIS, and NAS are stored as governed references and remain
outside project operation logic.

## Consequences

The Enterprise Wizard becomes the primary guided intake assistant for new
projects while preserving the Tower boundary. Incomplete sessions can be
resumed, each step can be validated independently, and activation leaves an
auditable workflow trail through ADR-0029.

Future UI work should render steps from the API contract and not reimplement
validation rules in the presentation layer.

## References

- ADR-0015: Tower vs WEB SIG boundary.
- ADR-0025: Corporate Portfolio Domain.
- ADR-0026: WEB SIG Factory controlled provisioning.
- ADR-0027: Corporate Control Tower operational flow.
- ADR-0029: Corporate Workflow Engine.
