# PROMPT MASTER 004 Corporate Dashboard Backlog

## Goal

Build an enterprise executive dashboard integrated into BIMSIG Enterprise.

## Milestone P4.1: Executive Dashboard Foundation

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| P4-101 | Add corporate dashboard read model | Done | ADR-0018 | API returns company-scoped portfolio, KPIs, risk, production, schedule, environmental, SSOMA, quality, users, licenses, AI, alerts, and comparisons. |
| P4-102 | Add dashboard API endpoint | Done | ADR-0018 | `GET /api/v1/companies/{company_id}/dashboard/executive` returns the read model. |
| P4-103 | Add integrated dashboard UI | Done | ADR-0018 | `GET /dashboard` serves an enterprise dashboard shell. |
| P4-104 | Add responsive layout | Done | ADR-0018 | Dashboard adapts to desktop, tablet, and mobile widths. |
| P4-105 | Add dark and light modes | Done | ADR-0018 | Dashboard can toggle between dark and light mode. |

## Milestone P4.2: Metric Hardening

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| P4-201 | Persist KPI snapshots | Planned | ADR-0015, ADR-0018 | Dashboard KPIs come from stored WEB SIG summary snapshots. |
| P4-202 | Persist alerts | Planned | ADR-0015, ADR-0018 | Dashboard alerts come from alert entities and rules. |
| P4-203 | Persist risk register | Planned | ADR-0015, ADR-0018 | Dashboard risk cards come from company/project risk records. |
| P4-204 | Persist production and schedule snapshots | Planned | ADR-0015, ADR-0018 | Dashboard production and schedule values come from module snapshots. |
| P4-205 | Persist environmental, SSOMA, and quality snapshots | Planned | ADR-0015, ADR-0018 | Dashboard compliance values come from module-specific snapshots. |
| P4-206 | Add AI usage metrics | Planned | ADR-0016, ADR-0018 | Dashboard AI usage comes from governed interaction records. |
