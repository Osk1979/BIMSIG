# ADR-0009: GeoServer Integration

## Status

Accepted

## Context

REV11 defines GeoServer as part of the information core. Corporate Control Tower must coordinate portfolio governance and provisioning without taking over WEB SIG operational publishing responsibilities.

## Decision

Corporate Control Tower REV12 will integrate with GeoServer through an infrastructure adapter that manages references and approved provisioning actions.

The Tower may create or register GeoServer workspaces during WEB SIG provisioning, but project-specific publication rules belong to each WEB SIG unless an approved ADR defines enterprise-wide publication behavior.

## Adapter Responsibilities

The GeoServer adapter may:

- Validate GeoServer connectivity.
- Create approved workspaces for new WEB SIG instances.
- Register workspace, store, layer, and service references.
- Report publication status to the portfolio dashboard.
- Map GeoServer errors into application-level provisioning failures.

The adapter must not:

- Publish arbitrary layers without an approved provisioning plan.
- Store GeoServer credentials in source code.
- Leak raw credentials or admin URLs through public API responses.

## Consequences

Provisioning implementation must include dry-run planning before executing GeoServer changes.

Contract tests should cover success, already-exists, permission-denied, and connectivity-failure cases with a fake adapter before real integration tests are added.

## References

- ADR-0001: REV11 as architecture baseline.
- ADR-0003: Project provisioning as a port.
- ADR-0005: Persistence strategy.
