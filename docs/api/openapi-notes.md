# API Notes

The initial API is implemented with FastAPI and exposes OpenAPI at runtime.

## Endpoints

- `GET /health`: service health and REV marker.
- `GET /api/v1/projects`: list portfolio projects.
- `POST /api/v1/projects`: register a project in the portfolio.
- `POST /api/v1/provisioning/websig`: request WEB SIG provisioning for a registered project.

## ADR References

- ADR-0001 defines REV11 as the architecture baseline.
- ADR-0002 defines the layered module structure.
- ADR-0003 defines provisioning as a port.
- ADR-0005 defines PostgreSQL/PostGIS as the production persistence direction.
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
