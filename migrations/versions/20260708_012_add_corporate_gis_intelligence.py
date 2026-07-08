"""Add Corporate GIS Intelligence tables.

Revision ID: 20260708_012
Revises: 20260708_011
Create Date: 2026-07-08

ADR references:
- ADR-0009: GeoServer integration.
- ADR-0010: Google Workspace transition integration.
- ADR-0011: Deployment strategy.
- ADR-0013: Corporate GIS Intelligence.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_012"
down_revision: str | None = "20260708_011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create Corporate GIS Intelligence source and layer tables."""

    op.create_table(
        "corporate_gis_sources",
        sa.Column("source_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("project_id", sa.String(length=80), nullable=False),
        sa.Column("program_id", sa.String(length=80), nullable=True),
        sa.Column("websig_instance_id", sa.String(length=120), nullable=True),
        sa.Column("service_kind", sa.String(length=80), nullable=False),
        sa.Column("service_url", sa.String(length=1000), nullable=False),
        sa.Column("discipline", sa.String(length=80), nullable=False),
        sa.Column("layer_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("updated_on", sa.Date(), nullable=False),
        sa.Column("metadata_document", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.ForeignKeyConstraint(["project_id"], ["portfolio_projects.project_id"]),
        sa.PrimaryKeyConstraint("source_id"),
    )
    op.create_index("ix_corporate_gis_sources_company_id", "corporate_gis_sources", ["company_id"])
    op.create_index("ix_corporate_gis_sources_project_id", "corporate_gis_sources", ["project_id"])
    op.create_index("ix_corporate_gis_sources_program_id", "corporate_gis_sources", ["program_id"])
    op.create_index("ix_corporate_gis_sources_websig_instance_id", "corporate_gis_sources", ["websig_instance_id"])
    op.create_index("ix_corporate_gis_sources_service_kind", "corporate_gis_sources", ["service_kind"])
    op.create_index("ix_corporate_gis_sources_discipline", "corporate_gis_sources", ["discipline"])
    op.create_index("ix_corporate_gis_sources_layer_type", "corporate_gis_sources", ["layer_type"])
    op.create_index("ix_corporate_gis_sources_status", "corporate_gis_sources", ["status"])

    op.create_table(
        "corporate_gis_layers",
        sa.Column("layer_id", sa.String(length=80), nullable=False),
        sa.Column("source_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("project_id", sa.String(length=80), nullable=False),
        sa.Column("program_id", sa.String(length=80), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("layer_type", sa.String(length=80), nullable=False),
        sa.Column("discipline", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("spatial_indicator", sa.String(length=120), nullable=False),
        sa.Column("indicator_value", sa.String(length=80), nullable=False),
        sa.Column("updated_on", sa.Date(), nullable=False),
        sa.Column("region", sa.String(length=120), nullable=True),
        sa.Column("risk_level", sa.String(length=80), nullable=False),
        sa.Column("metadata_document", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["corporate_gis_sources.source_id"]),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.ForeignKeyConstraint(["project_id"], ["portfolio_projects.project_id"]),
        sa.PrimaryKeyConstraint("layer_id"),
    )
    op.create_index("ix_corporate_gis_layers_source_id", "corporate_gis_layers", ["source_id"])
    op.create_index("ix_corporate_gis_layers_company_id", "corporate_gis_layers", ["company_id"])
    op.create_index("ix_corporate_gis_layers_project_id", "corporate_gis_layers", ["project_id"])
    op.create_index("ix_corporate_gis_layers_program_id", "corporate_gis_layers", ["program_id"])
    op.create_index("ix_corporate_gis_layers_layer_type", "corporate_gis_layers", ["layer_type"])
    op.create_index("ix_corporate_gis_layers_discipline", "corporate_gis_layers", ["discipline"])
    op.create_index("ix_corporate_gis_layers_status", "corporate_gis_layers", ["status"])
    op.create_index("ix_corporate_gis_layers_spatial_indicator", "corporate_gis_layers", ["spatial_indicator"])
    op.create_index("ix_corporate_gis_layers_region", "corporate_gis_layers", ["region"])
    op.create_index("ix_corporate_gis_layers_risk_level", "corporate_gis_layers", ["risk_level"])


def downgrade() -> None:
    """Drop Corporate GIS Intelligence tables."""

    op.drop_index("ix_corporate_gis_layers_risk_level", table_name="corporate_gis_layers")
    op.drop_index("ix_corporate_gis_layers_region", table_name="corporate_gis_layers")
    op.drop_index("ix_corporate_gis_layers_spatial_indicator", table_name="corporate_gis_layers")
    op.drop_index("ix_corporate_gis_layers_status", table_name="corporate_gis_layers")
    op.drop_index("ix_corporate_gis_layers_discipline", table_name="corporate_gis_layers")
    op.drop_index("ix_corporate_gis_layers_layer_type", table_name="corporate_gis_layers")
    op.drop_index("ix_corporate_gis_layers_program_id", table_name="corporate_gis_layers")
    op.drop_index("ix_corporate_gis_layers_project_id", table_name="corporate_gis_layers")
    op.drop_index("ix_corporate_gis_layers_company_id", table_name="corporate_gis_layers")
    op.drop_index("ix_corporate_gis_layers_source_id", table_name="corporate_gis_layers")
    op.drop_table("corporate_gis_layers")
    op.drop_index("ix_corporate_gis_sources_status", table_name="corporate_gis_sources")
    op.drop_index("ix_corporate_gis_sources_layer_type", table_name="corporate_gis_sources")
    op.drop_index("ix_corporate_gis_sources_discipline", table_name="corporate_gis_sources")
    op.drop_index("ix_corporate_gis_sources_service_kind", table_name="corporate_gis_sources")
    op.drop_index("ix_corporate_gis_sources_websig_instance_id", table_name="corporate_gis_sources")
    op.drop_index("ix_corporate_gis_sources_program_id", table_name="corporate_gis_sources")
    op.drop_index("ix_corporate_gis_sources_project_id", table_name="corporate_gis_sources")
    op.drop_index("ix_corporate_gis_sources_company_id", table_name="corporate_gis_sources")
    op.drop_table("corporate_gis_sources")
