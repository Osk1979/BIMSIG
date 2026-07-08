# CTO-105 - Corporate Experience Data Flow Backlog

## Objective

Connect the CTO-104 Corporate Experience Platform with existing operational
data flows without creating new business capabilities.

## Implemented Scope

- Portfolio Explorer reads company projects and dashboard governance data, and
  exposes expandable company, program, project, WEB SIG, status, owner,
  contract, date, and dashboard readiness details.
- Portfolio Explorer filters operate on existing project and governance data.
- Corporate Wizard reads resumable sessions from the existing Enterprise Wizard
  API and falls back to derived dashboard state when no session exists.
- Corporate Notifications reads the existing audit event stream.
- Corporate GIS Dashboard filters call the existing corporate GIS map filter
  endpoint.
- Executive Dashboard cards link to actionable areas: portfolio, GIS,
  comparisons, notifications, and operational panels.

## Constraints

- No new domains.
- No architecture changes.
- No ADR changes.
- No WEB SIG operational logic.
- No GIS editing or geometry mutation.

## Acceptance Criteria

- `/dashboard` keeps the CTO-104 Enterprise experience.
- Data-driven modules use existing endpoints and read models.
- Filtering and navigation are user-facing but do not introduce new write
  behavior.
- Contract tests protect the CTO-105 markers.
