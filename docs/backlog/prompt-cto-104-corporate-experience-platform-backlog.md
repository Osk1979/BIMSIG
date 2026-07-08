# CTO-104 REV03 - Corporate Experience Platform Backlog

## Objective

Build the first Enterprise user experience for Corporate Control Tower using
only existing domains and API contracts.

## Scope

- Corporate Home for portfolio, companies, programs, projects, GIS, NAS,
  provisioning, alerts, recent events, and pending actions.
- Corporate Navigation organized by business processes.
- Corporate Portfolio Explorer with company, program, project, WEB SIG, status,
  dashboard readiness, and visual filters.
- Corporate GIS Dashboard with national, regional, company, program, and project
  map modes.
- Read-only Corporate Layers for progress, risk, quality, environmental, SSOMA,
  production, parcels, interferences, and restrictions.
- Corporate Wizard visual steps for company, program, project, location,
  specialties, provisioning, GIS, NAS, users, and activation.
- Executive Dashboard questions for management.
- Corporate Notifications panel for provisioning, GIS, NAS, status, security,
  alerts, and actions.

## Constraints

- No new domains.
- No architecture changes.
- No ADR changes.
- No WEB SIG editing logic.
- No GIS editing, digitizing, or geometry mutation.
- No field capture or operational BIM implementation.

## Acceptance Criteria

- `/dashboard` feels like an Enterprise product rather than an API shell.
- Navigation exposes business processes instead of internal architecture.
- The GIS experience is read-only and consumes Corporate Layers.
- The Portfolio Explorer shows the corporate hierarchy from company to dashboard.
- The visual wizard communicates progress, validation, autosave, and resume
  states without adding new backend capabilities.
- Contract tests protect the CTO-104 REV03 UI markers.
