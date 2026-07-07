# ADR-0007: NAS Integration

## Status

Accepted

## Context

REV11 defines the enterprise NAS as the master repository. Corporate Control Tower must not replace the NAS with application-local file storage. It should register, classify, reference, and audit file locations while leaving managed binaries in the enterprise storage layer.

## Decision

Corporate Control Tower REV12 will integrate with NAS through a dedicated infrastructure adapter. The domain and application layers will store logical references to NAS resources, not local filesystem paths as business truth.

NAS integration will use a logical path contract:

```text
nas://<portfolio>/<project_id>/<domain>/<category>/<resource_name>
```

Concrete Windows paths, SMB paths, mount points, or vendor-specific addresses must stay inside the NAS adapter.

## Responsibilities

Corporate Control Tower stores:

- Logical NAS URI.
- Project and portfolio ownership.
- File category and discipline.
- Version and status metadata.
- Hash/checksum when available.
- Actor and timestamp audit references.

The NAS stores:

- Source files.
- Deliverables.
- BIM/GIS/CDE artifacts.
- Exported backup packages.

## Consequences

The first production NAS adapter must include tests for logical path generation, invalid path rejection, metadata registration, and error mapping.

No API endpoint should expose raw local server paths unless an approved operational ADR allows it.

## References

- ADR-0001: REV11 as architecture baseline.
- ADR-0005: Persistence strategy.
- Documento A - Arquitectura Maestra REV11: enterprise NAS as master repository.
