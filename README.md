# Corporate Control Tower REV12

Corporate Control Tower REV12 is the portfolio governance layer of BIMSIG Enterprise Platform.

This repository starts F2 of the BIMSIG Enterprise master program: Corporate Control Tower and Project Provisioning Engine.

## Architectural Source

The implementation is constrained by the approved REV11 documents:

- `D:\Implementacion_BIMSIG\Documento_A_Arquitectura_Maestra_REV11.docx`
- `D:\Implementacion_BIMSIG\Documento_B_Programa_Maestro_REV11.docx`
- `D:\Implementacion_BIMSIG\Documento_C_Manual_Prompts_REV11.docx`

## Official Principles Applied

- WEB SIG administers each project.
- Corporate Control Tower administers the portfolio.
- Each project owns its own WEB SIG.
- Corporate Control Tower creates and registers new WEB SIG instances.
- The enterprise NAS is the master repository.

## Repository Layout

```text
docs/adr/                  Architecture Decision Records
docs/api/                  API contracts and OpenAPI documentation
docs/architecture/         Architecture notes derived from REV11
docs/backlog/              Phase backlog and delivery tracking
docs/traceability/         Traceability from REV11 documents to code
src/control_tower/api/     HTTP API boundary
src/control_tower/application/ Application services and use cases
src/control_tower/domain/  Pure domain model
tests/unit/                Unit tests
tests/contract/            Contract tests
```

## Development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
pytest
uvicorn control_tower.api.app:create_app --factory --reload
```

Set `CONTROL_TOWER_DATABASE_URL` to use PostgreSQL/PostGIS in an integrated environment:

```bash
CONTROL_TOWER_DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/bimsig
```

Apply database migrations:

```bash
python -m alembic upgrade head
```

All implementation work must reference the relevant ADR and keep modules decoupled.

## Technical ADR Set

- ADR-0005: Persistence strategy.
- ADR-0006: Authentication and authorization.
- ADR-0007: NAS integration.
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0010: Google Workspace transition integration.
- ADR-0011: Deployment strategy.
- ADR-0012: CI/CD strategy.
- ADR-0013: Database schema and migrations.
