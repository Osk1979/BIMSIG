# Production Deploy Runbook

ADR references:
- ADR-0005: Persistence strategy.
- ADR-0007: NAS integration.
- ADR-0008: PostGIS integration.
- ADR-0011: Deployment strategy.
- ADR-0012: CI/CD strategy.
- ADR-0021: DevSecOps operating model.

## Scope

This runbook prepares Corporate Control Tower for controlled Docker deployment on a real server with PostGIS, NAS volume, health checks, optional reverse proxy, migrations, and operational backups.

The Tower governs, provisions, validates, and reports. It does not operate WEB SIG project data directly.

## Files

- `Dockerfile`: production image.
- `deploy/docker-entrypoint.sh`: controlled startup, database wait, and optional migrations.
- `docker-compose.prod.yml`: production compose stack.
- `.env.production.example`: environment template without real secrets.
- `deploy/nginx/conf.d/control-tower.conf`: reverse proxy preparation.
- `scripts/production_backup.sh`: operational backup helper.

## Server Prerequisites

1. Docker Engine and Docker Compose plugin.
2. Access to the production NAS mount path.
3. DNS/reverse proxy decision.
4. PostGIS credentials.
5. Strong `CONTROL_TOWER_AUTH_SECRET`.
6. Optional GeoServer and Google Workspace credentials.

## First Deploy

```bash
cp .env.production.example .env.production
```

Edit `.env.production` and replace:

- `POSTGRES_PASSWORD`
- `CONTROL_TOWER_DATABASE_URL`
- `CONTROL_TOWER_AUTH_SECRET`
- `CONTROL_TOWER_NAS_HOST_PATH`
- GeoServer credentials, if enabled.
- Google Workspace credentials, if enabled.

Create host paths:

```bash
sudo mkdir -p /srv/bimsig/nas /srv/bimsig/backups/control-tower /srv/bimsig/tls
sudo chown -R "$USER":"$USER" /srv/bimsig
```

Build and start:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

Run with reverse proxy profile:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production --profile reverse-proxy up -d --build
```

## Migrations

Startup migrations are controlled by:

```text
CONTROL_TOWER_RUN_MIGRATIONS=true
CONTROL_TOWER_WAIT_FOR_DB=true
```

For manual migration:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production exec control-tower alembic upgrade head
```

## Health

Container health:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production ps
```

Application health:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/v1/operational/readiness
curl http://127.0.0.1:8000/api/v1/observability/dashboard
```

## NAS Volumes

The production compose mounts:

```text
CONTROL_TOWER_NAS_HOST_PATH -> CONTROL_TOWER_NAS_ROOT
```

Default:

```text
/srv/bimsig/nas -> /mnt/nas
```

The database stores metadata and references only. Binary project files remain in NAS/Google Drive/WEB SIG infrastructure.

## Backup

Run operational backup:

```bash
chmod +x scripts/production_backup.sh
CONTROL_TOWER_NAS_HOST_PATH=/srv/bimsig/nas \
POSTGRES_USER=controltower \
POSTGRES_DB=controltower \
scripts/production_backup.sh /srv/bimsig/backups/control-tower
```

Backup output includes:

- PostGIS SQL dump.
- Redacted environment snapshot.
- Observability dashboard JSON.
- NAS runtime archive when the NAS path is available.
- API/ADR/operations contract archive.
- `SHA256SUMS`.

## Rollback

1. Stop app:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production stop control-tower
```

2. Restore previous image tag or Git revision.
3. Restore PostGIS dump if the migration changed database state.
4. Start stack and verify `/api/v1/operational/readiness`.

## Acceptance Checklist

- Docker image builds.
- Compose config validates.
- PostGIS healthcheck passes.
- Migrations run only when enabled.
- `/health` returns `ok`.
- `/api/v1/operational/readiness` returns `ready`.
- NAS mount is writable by the container user.
- Reverse proxy forwards `X-Forwarded-*` and `X-Request-ID`.
- Operational backup produces files and checksums.
- GitHub push and physical USB backup are completed.
