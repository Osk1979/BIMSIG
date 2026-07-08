# ADR-0021: DevSecOps Operating Model

## Status

Accepted

## Context

PROMPT MASTER 007 requires a complete DevSecOps foundation for Corporate Control Tower REV12.
The project already has GitHub source control, ADRs, tests, a basic GitHub Actions workflow, and
daily physical USB backup controls. The next step is to make delivery, security, observability, and
release operations repeatable.

## Decision

Corporate Control Tower REV12 will use GitHub as the source of truth and GitHub Actions as the
primary DevSecOps automation plane.

The DevSecOps baseline includes:

- GitHub version control on `main`.
- CI on push and pull request.
- Ruff linting.
- Pytest unit, contract, and infrastructure tests.
- OpenAPI contract drift detection.
- Alembic migration smoke testing.
- Docker image build verification.
- Containerized local runtime with PostGIS through Docker Compose.
- Runtime readiness and version endpoints.
- Request correlation through `X-Request-ID`.
- Baseline HTTP security headers.
- HTTP access logging through the API middleware.
- Daily USB backup procedure from ADR-0004.
- Release checklist executed before production tagging.

## Consequences

- Every code change must pass automated quality checks before release.
- The OpenAPI contract remains versioned and reproducible.
- Container packaging is validated even before production deployment automation is enabled.
- Security controls are visible in both API behavior and CI/CD.
- Production deployment remains governed by ADR-0011 and must not hard-code secrets.

## Traceability

- PROMPT MASTER 007: DevSecOps.
- ADR-0004: Daily physical USB backup.
- ADR-0011: Deployment strategy.
- ADR-0012: CI/CD strategy.
- ADR-0013: Database schema and migrations.
