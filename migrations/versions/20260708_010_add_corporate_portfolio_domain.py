"""Add corporate portfolio domain tables and project links.

Revision ID: 20260708_010
Revises: 20260708_009
Create Date: 2026-07-08

ADR references:
- ADR-0009: GeoServer integration.
- ADR-0010: Google Workspace transition integration.
- ADR-0015: Tower vs WEB SIG boundary.
- ADR-0024: REV13 corporate governance baseline.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_010"
down_revision: str | None = "20260708_009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create portfolio customer/program records and project integration links."""

    op.create_table(
        "portfolio_customers",
        sa.Column("customer_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("tax_id", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.PrimaryKeyConstraint("customer_id"),
    )
    op.create_index("ix_portfolio_customers_company_id", "portfolio_customers", ["company_id"])

    op.create_table(
        "portfolio_programs",
        sa.Column("program_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("customer_id", sa.String(length=80), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["portfolio_customers.customer_id"]),
        sa.PrimaryKeyConstraint("program_id"),
    )
    op.create_index("ix_portfolio_programs_company_id", "portfolio_programs", ["company_id"])
    op.create_index("ix_portfolio_programs_customer_id", "portfolio_programs", ["customer_id"])

    with op.batch_alter_table("portfolio_projects") as batch_op:
        batch_op.add_column(sa.Column("customer_id", sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column("program_id", sa.String(length=80), nullable=True))
        batch_op.add_column(
            sa.Column("lifecycle_stage", sa.String(length=80), nullable=False, server_default="intake")
        )
        batch_op.add_column(sa.Column("websig_instance_id", sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column("websig_url", sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column("nas_root_uri", sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column("gis_binding_id", sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column("google_drive_folder_id", sa.String(length=255), nullable=True))
        batch_op.create_index("ix_portfolio_projects_customer_id", ["customer_id"])
        batch_op.create_index("ix_portfolio_projects_program_id", ["program_id"])
        batch_op.create_foreign_key(
            "fk_portfolio_projects_customer_id",
            "portfolio_customers",
            ["customer_id"],
            ["customer_id"],
        )
        batch_op.create_foreign_key(
            "fk_portfolio_projects_program_id",
            "portfolio_programs",
            ["program_id"],
            ["program_id"],
        )


def downgrade() -> None:
    """Remove portfolio customer/program records and project integration links."""

    with op.batch_alter_table("portfolio_projects") as batch_op:
        batch_op.drop_constraint("fk_portfolio_projects_program_id", type_="foreignkey")
        batch_op.drop_constraint("fk_portfolio_projects_customer_id", type_="foreignkey")
        batch_op.drop_index("ix_portfolio_projects_program_id")
        batch_op.drop_index("ix_portfolio_projects_customer_id")
        batch_op.drop_column("google_drive_folder_id")
        batch_op.drop_column("gis_binding_id")
        batch_op.drop_column("nas_root_uri")
        batch_op.drop_column("websig_url")
        batch_op.drop_column("websig_instance_id")
        batch_op.drop_column("lifecycle_stage")
        batch_op.drop_column("program_id")
        batch_op.drop_column("customer_id")
    op.drop_index("ix_portfolio_programs_customer_id", table_name="portfolio_programs")
    op.drop_index("ix_portfolio_programs_company_id", table_name="portfolio_programs")
    op.drop_table("portfolio_programs")
    op.drop_index("ix_portfolio_customers_company_id", table_name="portfolio_customers")
    op.drop_table("portfolio_customers")
