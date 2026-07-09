# PROMPT HARDENING-009 - Production Deploy

ADR references:
- ADR-0005: Persistence strategy.
- ADR-0007: NAS integration.
- ADR-0008: PostGIS integration.
- ADR-0011: Deployment strategy.
- ADR-0012: CI/CD strategy.
- ADR-0021: DevSecOps operating model.

## Objective

Prepare Corporate Control Tower for controlled production deployment on Docker/server/NAS infrastructure.

## Delivered

- Production Dockerfile hardening:
  - Non-root runtime user.
  - NAS and report output paths.
  - Docker healthcheck.
  - Controlled entrypoint.
- Controlled startup entrypoint:
  - Optional PostGIS wait.
  - Optional Alembic migrations.
- Production compose:
  - `docker-compose.prod.yml`.
  - Corporate Control Tower service.
  - PostGIS service.
  - NAS host mount.
  - App output volume.
  - Optional reverse proxy profile.
- Environment template:
  - `.env.production.example`.
- Reverse proxy preparation:
  - `deploy/nginx/conf.d/control-tower.conf`.
- Operational backup:
  - `scripts/production_backup.sh`.
  - PostGIS dump.
  - Redacted env snapshot.
  - Observability dashboard capture.
  - NAS runtime archive when mounted.
  - SHA256 checksums.
- Runbook:
  - `docs/operations/production-deploy-runbook.md`.
- Contract tests for deploy assets.

## Guardrails

- No real secrets are stored in Git.
- `.env.production` remains ignored.
- Startup migrations are controlled by environment variables.
- Reverse proxy is prepared but optional.
- The Tower still stores metadata/references; it does not operate WEB SIG project data directly.
