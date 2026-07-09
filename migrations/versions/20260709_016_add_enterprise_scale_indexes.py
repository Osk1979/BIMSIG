"""Add Enterprise-scale portfolio indexes.

Revision ID: 20260709_016
Revises: 20260708_015
Create Date: 2026-07-09

ADR references:
- ADR-0014: Enterprise multitenancy.
- ADR-0024: Corporate operating model.
- ADR-0025: Corporate Portfolio Domain.
"""

from collections.abc import Sequence

from alembic import op


revision: str = "20260709_016"
down_revision: str | None = "20260708_015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create compound indexes used by Enterprise-scale portfolio queries."""

    op.create_index(
        "ix_portfolio_projects_company_status",
        "portfolio_projects",
        ["company_id", "status"],
    )
    op.create_index(
        "ix_portfolio_projects_company_program",
        "portfolio_projects",
        ["company_id", "program_id"],
    )
    op.create_index(
        "ix_portfolio_projects_company_region",
        "portfolio_projects",
        ["company_id", "region"],
    )
    op.create_index(
        "ix_portfolio_projects_company_lifecycle",
        "portfolio_projects",
        ["company_id", "lifecycle_stage"],
    )


def downgrade() -> None:
    """Drop Enterprise-scale portfolio indexes."""

    op.drop_index("ix_portfolio_projects_company_lifecycle", table_name="portfolio_projects")
    op.drop_index("ix_portfolio_projects_company_region", table_name="portfolio_projects")
    op.drop_index("ix_portfolio_projects_company_program", table_name="portfolio_projects")
    op.drop_index("ix_portfolio_projects_company_status", table_name="portfolio_projects")
