"""Scope portfolio projects by company.

Revision ID: 20260707_004
Revises: 20260707_003
Create Date: 2026-07-07

ADR references:
- ADR-0014: Enterprise multitenancy.
- ADR-0015: Tower vs WEB SIG operational boundary.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260707_004"
down_revision: str | None = "20260707_003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add tenant scope to portfolio projects."""

    op.add_column(
        "portfolio_projects",
        sa.Column("company_id", sa.String(length=80), nullable=False, server_default="DEFAULT"),
    )
    op.create_index("ix_portfolio_projects_company_id", "portfolio_projects", ["company_id"])
    with op.batch_alter_table("portfolio_projects") as batch_op:
        batch_op.create_foreign_key(
            "fk_portfolio_projects_company_id_companies",
            "companies",
            ["company_id"],
            ["company_id"],
        )


def downgrade() -> None:
    """Remove tenant scope from portfolio projects."""

    with op.batch_alter_table("portfolio_projects") as batch_op:
        batch_op.drop_constraint(
            "fk_portfolio_projects_company_id_companies",
            type_="foreignkey",
        )
    op.drop_index("ix_portfolio_projects_company_id", table_name="portfolio_projects")
    op.drop_column("portfolio_projects", "company_id")
