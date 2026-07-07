from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_head_creates_initial_tables(tmp_path, monkeypatch) -> None:
    database_url = f"sqlite:///{tmp_path / 'migration.db'}"
    monkeypatch.setenv("CONTROL_TOWER_DATABASE_URL", database_url)
    config = Config("alembic.ini")

    command.upgrade(config, "head")

    engine = create_engine(database_url)
    inspector = inspect(engine)
    assert "portfolio_projects" in inspector.get_table_names()
    assert "provisioning_requests" in inspector.get_table_names()
    assert "ix_provisioning_requests_project_id" in {
        index["name"] for index in inspector.get_indexes("provisioning_requests")
    }
