# Database Migrations

Alembic owns database schema changes for Corporate Control Tower REV12.

## Apply Migrations

```powershell
$env:CONTROL_TOWER_DATABASE_URL = "postgresql+psycopg://user:password@localhost:5432/bimsig"
python -m alembic upgrade head
```

For local SQLite development:

```powershell
$env:CONTROL_TOWER_DATABASE_URL = "sqlite:///./control_tower.db"
python -m alembic upgrade head
```

## Rules

- Production schema changes must be committed as reviewed Alembic revision files.
- `metadata.create_all()` is only a dev/test fallback and must not be used as a production migration path.
- Migration changes must reference ADR-0013.
