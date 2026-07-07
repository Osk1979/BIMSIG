# ADR-0012: CI/CD Strategy

## Status

Accepted

## Context

REV11 requires every phase to produce documentation, code, tests, and versioned delivery. Corporate Control Tower REV12 is now versioned in GitHub and needs automated verification to protect the main branch.

## Decision

Corporate Control Tower REV12 will use GitHub Actions as the CI/CD automation surface.

The initial CI workflow runs on `push` and `pull_request` to `main` and executes:

- Dependency installation.
- Ruff linting.
- Pytest test suite.

Deployment automation is deferred until ADR-0011 follow-up tasks define the container and runtime targets.

## Branch Rules

- `main` is the integration branch.
- Changes should be introduced through small commits or pull requests.
- CI must pass before production release.
- Failed CI blocks release until fixed or explicitly waived in a documented decision.

## Consequences

Future CI/CD work should add:

- OpenAPI contract generation check.
- Test coverage reporting.
- Security scanning.
- Container build verification.
- Deployment workflow after staging/production targets are approved.

## References

- ADR-0001: REV11 as architecture baseline.
- ADR-0002: Layered modular API scaffold.
- ADR-0011: Deployment strategy.
