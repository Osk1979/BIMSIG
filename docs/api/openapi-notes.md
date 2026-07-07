# API Notes

The initial API is implemented with FastAPI and exposes OpenAPI at runtime.

## Endpoints

- `GET /health`: service health and REV marker.
- `GET /api/v1/operational/health`: operational service and database health.
- `GET /api/v1/portfolio/summary`: portfolio counts by governance status.
- `GET /api/v1/projects`: list portfolio projects.
- `POST /api/v1/projects`: register a project in the portfolio.
- `GET /api/v1/projects/{project_id}`: get one portfolio project.
- `PATCH /api/v1/projects/{project_id}/governance-status`: change project governance status.
- `POST /api/v1/provisioning/websig`: request WEB SIG provisioning for a registered project.
- `GET /api/v1/provisioning/websig`: list WEB SIG provisioning requests.
- `GET /api/v1/audit/events`: list recent audit events.

## ADR References

- ADR-0001 defines REV11 as the architecture baseline.
- ADR-0002 defines the layered module structure.
- ADR-0003 defines provisioning as a port.
- ADR-0005 defines PostgreSQL/PostGIS as the production persistence direction.
- ADR-0006 defines actor and authorization requirements for protected operations.
- ADR-0013 defines the first durable portfolio/provisioning schema.

## Configuration

The API reads `CONTROL_TOWER_DATABASE_URL`.

Default local development value:

```text
sqlite:///./control_tower.db
```

Production target:

```text
postgresql+psycopg://<user>:<password>@<host>:5432/<database>
```

Schema changes are managed through Alembic:

```bash
python -m alembic upgrade head
```
