"""Add corporate GIS registry tables.

Revision ID: 20260708_009
Revises: 20260708_008
Create Date: 2026-07-08

ADR references:
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0023: Corporate GIS administration.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_009"
down_revision: str | None = "20260708_008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create corporate GIS registry tables."""

    op.create_table(
        "gis_postgis_schemas",
        sa.Column("schema_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("project_id", sa.String(length=80), nullable=False),
        sa.Column("schema_name", sa.String(length=160), nullable=False),
        sa.Column("database_ref", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.ForeignKeyConstraint(["project_id"], ["portfolio_projects.project_id"]),
        sa.PrimaryKeyConstraint("schema_id"),
    )
    op.create_index("ix_gis_postgis_schemas_company_id", "gis_postgis_schemas", ["company_id"])
    op.create_index("ix_gis_postgis_schemas_project_id", "gis_postgis_schemas", ["project_id"])

    op.create_table(
        "gis_geoserver_workspaces",
        sa.Column("workspace_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("project_id", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("geoserver_url", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.ForeignKeyConstraint(["project_id"], ["portfolio_projects.project_id"]),
        sa.PrimaryKeyConstraint("workspace_id"),
    )
    op.create_index("ix_gis_geoserver_workspaces_company_id", "gis_geoserver_workspaces", ["company_id"])
    op.create_index("ix_gis_geoserver_workspaces_project_id", "gis_geoserver_workspaces", ["project_id"])

    op.create_table(
        "gis_geoserver_datastores",
        sa.Column("datastore_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("project_id", sa.String(length=80), nullable=False),
        sa.Column("workspace_id", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("postgis_schema_id", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.ForeignKeyConstraint(["project_id"], ["portfolio_projects.project_id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["gis_geoserver_workspaces.workspace_id"]),
        sa.ForeignKeyConstraint(["postgis_schema_id"], ["gis_postgis_schemas.schema_id"]),
        sa.PrimaryKeyConstraint("datastore_id"),
    )
    op.create_index("ix_gis_geoserver_datastores_company_id", "gis_geoserver_datastores", ["company_id"])
    op.create_index("ix_gis_geoserver_datastores_project_id", "gis_geoserver_datastores", ["project_id"])
    op.create_index("ix_gis_geoserver_datastores_workspace_id", "gis_geoserver_datastores", ["workspace_id"])
    op.create_index("ix_gis_geoserver_datastores_postgis_schema_id", "gis_geoserver_datastores", ["postgis_schema_id"])

    op.create_table(
        "gis_geoserver_layers",
        sa.Column("layer_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("project_id", sa.String(length=80), nullable=False),
        sa.Column("workspace_id", sa.String(length=80), nullable=False),
        sa.Column("datastore_id", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("wms_url", sa.String(length=500), nullable=True),
        sa.Column("wfs_url", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.ForeignKeyConstraint(["project_id"], ["portfolio_projects.project_id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["gis_geoserver_workspaces.workspace_id"]),
        sa.ForeignKeyConstraint(["datastore_id"], ["gis_geoserver_datastores.datastore_id"]),
        sa.PrimaryKeyConstraint("layer_id"),
    )
    op.create_index("ix_gis_geoserver_layers_company_id", "gis_geoserver_layers", ["company_id"])
    op.create_index("ix_gis_geoserver_layers_project_id", "gis_geoserver_layers", ["project_id"])
    op.create_index("ix_gis_geoserver_layers_workspace_id", "gis_geoserver_layers", ["workspace_id"])
    op.create_index("ix_gis_geoserver_layers_datastore_id", "gis_geoserver_layers", ["datastore_id"])

    op.create_table(
        "gis_project_bindings",
        sa.Column("binding_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("project_id", sa.String(length=80), nullable=False),
        sa.Column("postgis_schema_id", sa.String(length=80), nullable=False),
        sa.Column("geoserver_workspace_id", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.ForeignKeyConstraint(["project_id"], ["portfolio_projects.project_id"]),
        sa.ForeignKeyConstraint(["postgis_schema_id"], ["gis_postgis_schemas.schema_id"]),
        sa.ForeignKeyConstraint(["geoserver_workspace_id"], ["gis_geoserver_workspaces.workspace_id"]),
        sa.PrimaryKeyConstraint("binding_id"),
        sa.UniqueConstraint("project_id"),
    )
    op.create_index("ix_gis_project_bindings_company_id", "gis_project_bindings", ["company_id"])
    op.create_index("ix_gis_project_bindings_project_id", "gis_project_bindings", ["project_id"])


def downgrade() -> None:
    """Drop corporate GIS registry tables."""

    op.drop_index("ix_gis_project_bindings_project_id", table_name="gis_project_bindings")
    op.drop_index("ix_gis_project_bindings_company_id", table_name="gis_project_bindings")
    op.drop_table("gis_project_bindings")
    op.drop_index("ix_gis_geoserver_layers_datastore_id", table_name="gis_geoserver_layers")
    op.drop_index("ix_gis_geoserver_layers_workspace_id", table_name="gis_geoserver_layers")
    op.drop_index("ix_gis_geoserver_layers_project_id", table_name="gis_geoserver_layers")
    op.drop_index("ix_gis_geoserver_layers_company_id", table_name="gis_geoserver_layers")
    op.drop_table("gis_geoserver_layers")
    op.drop_index("ix_gis_geoserver_datastores_postgis_schema_id", table_name="gis_geoserver_datastores")
    op.drop_index("ix_gis_geoserver_datastores_workspace_id", table_name="gis_geoserver_datastores")
    op.drop_index("ix_gis_geoserver_datastores_project_id", table_name="gis_geoserver_datastores")
    op.drop_index("ix_gis_geoserver_datastores_company_id", table_name="gis_geoserver_datastores")
    op.drop_table("gis_geoserver_datastores")
    op.drop_index("ix_gis_geoserver_workspaces_project_id", table_name="gis_geoserver_workspaces")
    op.drop_index("ix_gis_geoserver_workspaces_company_id", table_name="gis_geoserver_workspaces")
    op.drop_table("gis_geoserver_workspaces")
    op.drop_index("ix_gis_postgis_schemas_project_id", table_name="gis_postgis_schemas")
    op.drop_index("ix_gis_postgis_schemas_company_id", table_name="gis_postgis_schemas")
    op.drop_table("gis_postgis_schemas")
