# ADR-0018: Corporate Executive Dashboard

## Status

Accepted

## Context

PROMPT MASTER 004 requires an enterprise executive dashboard for Corporate Control Tower REV12. The dashboard must show portfolio, corporate map, KPIs, risks, production, schedule, environmental, SSOMA, quality, users, licenses, AI, alerts, and comparisons between projects.

Existing ADRs constrain the implementation:

- ADR-0014 requires company-scoped tenancy.
- ADR-0015 keeps the Tower as a corporate control plane, not the operational project system.
- ADR-0016 defines licensing as an enterprise concern.
- ADR-0017 provides provisioning read data for WEB SIG and infrastructure state.

## Decision

Corporate Control Tower adds a company-scoped executive dashboard read model and an integrated FastAPI-served dashboard UI.

The dashboard is built inside BIMSIG Enterprise:

- `GET /api/v1/companies/{company_id}/dashboard/executive` returns the executive read model.
- `GET /dashboard` serves the responsive dashboard shell.
- The UI supports dark mode and light mode.
- The dashboard uses portfolio, users, licenses, provisioning, and Corporate Portfolio Domain data to produce executive summaries.
- The dashboard exposes `portfolio_governance` so clients can show customers, programs, lifecycle, WEB SIG, NAS, and GIS references without operating WEB SIG.

No separate dashboard application is created.

## Consequences

The first implementation provides deterministic corporate read models even while KPI, alert, AI, SSOMA, quality, environmental, and production modules mature.

Future work must replace placeholder-derived metrics with persisted module-specific snapshots as those modules are implemented.
