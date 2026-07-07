"""Alembic environment for Corporate Control Tower REV12.

ADR references:
- ADR-0005: Persistence strategy.
- ADR-0013: Database schema and migrations.
"""

from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import engine_from_config, pool

from control_tower.infrastructure.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_database_url() -> str:
    """Resolve the database URL for migrations."""

    return os.getenv(
        "CONTROL_TOWER_DATABASE_URL",
        config.get_main_option("sqlalchemy.url"),
    )


def run_migrations_offline() -> None:
    """Run migrations without creating an Engine."""

    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations with a live database connection."""

    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
