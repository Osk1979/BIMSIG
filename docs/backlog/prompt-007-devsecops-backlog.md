# PROMPT MASTER 007 - DevSecOps Backlog

## Scope

Build a complete DevSecOps baseline for Corporate Control Tower REV12 without changing the
business architecture.

## Items

| ID | Item | Status | Traceability |
| --- | --- | --- | --- |
| P7-001 | Keep GitHub as source of truth | Done | ADR-0021 |
| P7-002 | Expand GitHub Actions CI | Done | ADR-0012, ADR-0021 |
| P7-003 | Add OpenAPI contract drift check | Done | ADR-0012, ADR-0021 |
| P7-004 | Add migration smoke test in CI | Done | ADR-0013, ADR-0021 |
| P7-005 | Add Docker image definition | Done | ADR-0011, ADR-0021 |
| P7-006 | Add Docker Compose local runtime with PostGIS | Done | ADR-0011, ADR-0005 |
| P7-007 | Add release check script | Done | ADR-0012, ADR-0021 |
| P7-008 | Add readiness and version endpoints | Done | ADR-0011, ADR-0021 |
| P7-009 | Add request correlation and HTTP access logs | Done | ADR-0021 |
| P7-010 | Add baseline API security headers | Done | ADR-0006, ADR-0021 |
| P7-011 | Document release checklist | Done | ADR-0021 |
| P7-012 | Maintain daily USB backup procedure | Done | ADR-0004 |

## Deferred Hardening

- Dependency vulnerability scanning with an approved enterprise scanner.
- Container image signing.
- SBOM generation.
- Staging and production deployment workflows.
- Centralized log shipping.
- Metrics backend integration.
- Alert routing.
