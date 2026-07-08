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
    assert "audit_events" in inspector.get_table_names()
    assert "companies" in inspector.get_table_names()
    assert "users" in inspector.get_table_names()
    assert "company_memberships" in inspector.get_table_names()
    assert "license_plans" in inspector.get_table_names()
    assert "company_licenses" in inspector.get_table_names()
    assert "information_assets" in inspector.get_table_names()
    assert "information_versions" in inspector.get_table_names()
    assert "information_snapshots" in inspector.get_table_names()
    assert "information_backups" in inspector.get_table_names()
    assert "company_id" in {
        column["name"] for column in inspector.get_columns("portfolio_projects")
    }
    provisioning_columns = {
        column["name"] for column in inspector.get_columns("provisioning_requests")
    }
    assert {"company_id", "operation", "steps_document"} <= provisioning_columns
    assert "ix_provisioning_requests_project_id" in {
        index["name"] for index in inspector.get_indexes("provisioning_requests")
    }
    assert "ix_provisioning_requests_company_id" in {
        index["name"] for index in inspector.get_indexes("provisioning_requests")
    }
    assert "ix_information_assets_company_id" in {
        index["name"] for index in inspector.get_indexes("information_assets")
    }
    assert "category" in {
        column["name"] for column in inspector.get_columns("information_assets")
    }
    assert "ix_information_assets_category" in {
        index["name"] for index in inspector.get_indexes("information_assets")
    }
