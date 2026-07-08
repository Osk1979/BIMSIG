"""Add formal project administrative location.

Revision ID: 20260708_015
Revises: 20260708_014
Create Date: 2026-07-08

ADR references:
- ADR-0025: Corporate Portfolio Domain.
- ADR-0030: Enterprise Wizard.
- ADR-0015: Tower vs WEB SIG operational boundary.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_015"
down_revision: str | None = "20260708_014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add administrative location fields to portfolio projects."""

    op.add_column("portfolio_projects", sa.Column("country", sa.String(length=16), nullable=True))
    op.add_column("portfolio_projects", sa.Column("region", sa.String(length=120), nullable=True))
    op.add_column("portfolio_projects", sa.Column("province", sa.String(length=120), nullable=True))
    op.add_column("portfolio_projects", sa.Column("district", sa.String(length=120), nullable=True))
    op.add_column("portfolio_projects", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("portfolio_projects", sa.Column("longitude", sa.Float(), nullable=True))
    op.add_column("portfolio_projects", sa.Column("location_source", sa.String(length=120), nullable=True))
    op.add_column("portfolio_projects", sa.Column("location_validation_status", sa.String(length=80), nullable=True))
    op.create_index("ix_portfolio_projects_region", "portfolio_projects", ["region"])


def downgrade() -> None:
    """Remove administrative location fields from portfolio projects."""

    op.drop_index("ix_portfolio_projects_region", table_name="portfolio_projects")
    op.drop_column("portfolio_projects", "location_validation_status")
    op.drop_column("portfolio_projects", "location_source")
    op.drop_column("portfolio_projects", "longitude")
    op.drop_column("portfolio_projects", "latitude")
    op.drop_column("portfolio_projects", "district")
    op.drop_column("portfolio_projects", "province")
    op.drop_column("portfolio_projects", "region")
    op.drop_column("portfolio_projects", "country")
