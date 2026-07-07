"""Initial portfolio and provisioning tables.

Revision ID: 20260707_001
Revises:
Create Date: 2026-07-07

ADR references:
- ADR-0005: Persistence strategy.
- ADR-0013: Database schema and migrations.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260707_001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create initial durable registry tables."""

    op.create_table(
        "portfolio_projects",
        sa.Column("project_id", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("cui", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("project_id"),
    )
    op.create_table(
        "provisioning_requests",
        sa.Column("request_id", sa.String(length=80), nullable=False),
        sa.Column("project_id", sa.String(length=80), nullable=False),
        sa.Column("target_revision", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["portfolio_projects.project_id"]),
        sa.PrimaryKeyConstraint("request_id"),
    )
    op.create_index(
        "ix_provisioning_requests_project_id",
        "provisioning_requests",
        ["project_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop initial durable registry tables."""

    op.drop_index("ix_provisioning_requests_project_id", table_name="provisioning_requests")
    op.drop_table("provisioning_requests")
    op.drop_table("portfolio_projects")
