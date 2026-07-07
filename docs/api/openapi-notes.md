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
