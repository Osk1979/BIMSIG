# ADR-0010: Google Workspace Transition Integration

## Status

Accepted

## Context

REV11 states that BIMSIG integrates with Google Workspace during the transition. Corporate Control Tower must support this transition without making Google Workspace the architectural source of truth for enterprise records.

## Decision

Corporate Control Tower REV12 will treat Google Workspace as a transitional collaboration surface. The Tower may store references to Google Drive folders, Docs, Sheets, and related synchronization metadata, but authoritative portfolio state remains in Corporate Control Tower persistence and authoritative files remain in NAS where applicable.

## Integration Boundaries

Allowed:

- Store external Google Workspace identifiers.
- Link project records to transitional collaboration folders.
- Record synchronization status.
- Import approved metadata from transition documents or sheets.
- Generate documents for review when explicitly requested.

Not allowed:

- Treat Google Workspace as the master registry.
- Store secrets in documents or sheets.
- Drive provisioning decisions from unvalidated spreadsheet state.
- Bypass audit logging for changes imported from Google Workspace.

## Consequences

Any Google Workspace sync job must be idempotent, auditable, and reversible where practical. Imports must validate source, actor, timestamp, and target project identity.

## References

- ADR-0001: REV11 as architecture baseline.
- ADR-0005: Persistence strategy.
- Documento A - Arquitectura Maestra REV11: Google Workspace integration during transition.
