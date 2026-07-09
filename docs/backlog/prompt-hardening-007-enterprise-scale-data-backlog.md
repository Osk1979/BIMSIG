# PROMPT HARDENING-007 - Enterprise Scale Data

ADR references:
- ADR-0014: Enterprise multitenancy.
- ADR-0024: Corporate operating model.
- ADR-0025: Corporate Portfolio Domain.

## Objective

Prepare Corporate Control Tower for hundreds of companies and projects through controlled massive seed data, pagination, filtering, search, query indexes, isolation checks, and performance metrics.

## Delivered

- Enterprise-scale application service:
  - Controlled deterministic seed.
  - Paginated project queries.
  - Filters by company, program, customer, status, lifecycle, region, and free text.
  - Search across company, program, and project records.
  - Enterprise aggregate summary.
  - Multi-company isolation validation.
- API endpoints:
  - `POST /api/v1/enterprise-scale/seed`
  - `GET /api/v1/enterprise-scale/projects`
  - `GET /api/v1/enterprise-scale/search`
  - `GET /api/v1/enterprise-scale/summary`
  - `GET /api/v1/enterprise-scale/isolation`
- Query duration metrics returned in scale payloads.
- Compound database indexes for portfolio project scale queries:
  - `company_id + status`
  - `company_id + program_id`
  - `company_id + region`
  - `company_id + lifecycle_stage`
- Alembic migration:
  - `20260709_016_add_enterprise_scale_indexes.py`
- Unit and contract tests.

## Guardrails

- No WEB SIG operational logic was added.
- Existing non-paginated endpoints remain compatible.
- Seed is controlled by request payload and bounded for safe local/CI execution.
- Multi-company isolation remains company-scoped and validated.
