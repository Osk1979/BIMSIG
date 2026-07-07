# ADR-0004: Daily Physical USB Backup

## Status

Accepted

## Context

Corporate Control Tower REV12 is a strategic project. GitHub protects the remote history, but the project also requires an end-of-day physical backup to reduce operational risk from account access loss, network outage, accidental deletion, or workstation failure.

## Decision

At the end of each workday, the repository must be exported to a timestamped ZIP file and copied to a USB drive.

The backup package must include:

- Source code.
- Documentation.
- ADRs.
- Tests.
- Git metadata.

The backup package must exclude:

- Virtual environments.
- Python caches.
- Test and lint caches.
- Generated backup ZIP files.
- Build artifacts.

## Consequences

The repository includes an operator script at `scripts/backup_to_usb.ps1` and an operating procedure at `docs/operations/daily-usb-backup.md`.

The physical backup does not replace GitHub. Both controls are required: GitHub for versioned collaboration and USB backup for daily offline continuity.
