"""Add NAS Corporate Information Center tables.

Revision ID: 20260708_006
Revises: 20260707_005
Create Date: 2026-07-08

ADR references:
- ADR-0007: NAS integration.
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0010: Google Workspace transition integration.
- ADR-0019: NAS Corporate Information Center.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_006"
down_revision: str | None = "20260707_005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create Corporate Information Center registry tables."""

    op.create_table(
        "information_assets",
        sa.Column("asset_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("project_id", sa.String(length=80), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("asset_type", sa.String(length=80), nullable=False),
        sa.Column("logical_uri", sa.String(length=1000), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("metadata_document", sa.Text(), nullable=False),
        sa.Column("permissions_document", sa.Text(), nullable=False),
        sa.Column("google_drive_id", sa.String(length=255), nullable=True),
        sa.Column("geoserver_reference", sa.String(length=1000), nullable=True),
        sa.Column("postgis_reference", sa.String(length=1000), nullable=True),
        sa.Column("docker_reference", sa.String(length=1000), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.ForeignKeyConstraint(["project_id"], ["portfolio_projects.project_id"]),
        sa.PrimaryKeyConstraint("asset_id"),
    )
    op.create_index("ix_information_assets_asset_type", "information_assets", ["asset_type"])
    op.create_index("ix_information_assets_company_id", "information_assets", ["company_id"])
    op.create_index("ix_information_assets_project_id", "information_assets", ["project_id"])
    op.create_table(
        "information_versions",
        sa.Column("version_id", sa.String(length=80), nullable=False),
        sa.Column("asset_id", sa.String(length=80), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.Column("logical_uri", sa.String(length=1000), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=128), nullable=True),
        sa.Column("metadata_document", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["information_assets.asset_id"]),
        sa.PrimaryKeyConstraint("version_id"),
    )
    op.create_index("ix_information_versions_asset_id", "information_versions", ["asset_id"])
    op.create_table(
        "information_snapshots",
        sa.Column("snapshot_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("project_id", sa.String(length=80), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("asset_ids_document", sa.Text(), nullable=False),
        sa.Column("logical_uri", sa.String(length=1000), nullable=False),
        sa.Column("metadata_document", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.ForeignKeyConstraint(["project_id"], ["portfolio_projects.project_id"]),
        sa.PrimaryKeyConstraint("snapshot_id"),
    )
    op.create_index("ix_information_snapshots_company_id", "information_snapshots", ["company_id"])
    op.create_index("ix_information_snapshots_project_id", "information_snapshots", ["project_id"])
    op.create_table(
        "information_backups",
        sa.Column("backup_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("project_id", sa.String(length=80), nullable=True),
        sa.Column("snapshot_id", sa.String(length=80), nullable=True),
        sa.Column("logical_uri", sa.String(length=1000), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=128), nullable=True),
        sa.Column("metadata_document", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.ForeignKeyConstraint(["project_id"], ["portfolio_projects.project_id"]),
        sa.ForeignKeyConstraint(["snapshot_id"], ["information_snapshots.snapshot_id"]),
        sa.PrimaryKeyConstraint("backup_id"),
    )
    op.create_index("ix_information_backups_company_id", "information_backups", ["company_id"])
    op.create_index("ix_information_backups_project_id", "information_backups", ["project_id"])


def downgrade() -> None:
    """Drop Corporate Information Center registry tables."""

    op.drop_index("ix_information_backups_project_id", table_name="information_backups")
    op.drop_index("ix_information_backups_company_id", table_name="information_backups")
    op.drop_table("information_backups")
    op.drop_index("ix_information_snapshots_project_id", table_name="information_snapshots")
    op.drop_index("ix_information_snapshots_company_id", table_name="information_snapshots")
    op.drop_table("information_snapshots")
    op.drop_index("ix_information_versions_asset_id", table_name="information_versions")
    op.drop_table("information_versions")
    op.drop_index("ix_information_assets_project_id", table_name="information_assets")
    op.drop_index("ix_information_assets_company_id", table_name="information_assets")
    op.drop_index("ix_information_assets_asset_type", table_name="information_assets")
    op.drop_table("information_assets")
