"""Add NAS information category.

Revision ID: 20260708_007
Revises: 20260708_006
Create Date: 2026-07-08

ADR references:
- ADR-0007: NAS integration.
- ADR-0019: NAS Corporate Information Center.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_007"
down_revision: str | None = "20260708_006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add corporate information category to NAS assets."""

    op.add_column(
        "information_assets",
        sa.Column("category", sa.String(length=80), nullable=False, server_default="cde"),
    )
    op.create_index("ix_information_assets_category", "information_assets", ["category"])


def downgrade() -> None:
    """Remove corporate information category from NAS assets."""

    op.drop_index("ix_information_assets_category", table_name="information_assets")
    op.drop_column("information_assets", "category")
