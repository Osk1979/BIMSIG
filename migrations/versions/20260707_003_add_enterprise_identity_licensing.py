"""Add enterprise tenant, identity, and licensing tables.

Revision ID: 20260707_003
Revises: 20260707_002
Create Date: 2026-07-07

ADR references:
- ADR-0006: Authentication and authorization.
- ADR-0014: Enterprise multitenancy.
- ADR-0016: Enterprise licensing.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260707_003"
down_revision: str | None = "20260707_002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create initial enterprise tenant, user, membership, and licensing tables."""

    op.create_table(
        "companies",
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("tax_id", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("company_id"),
    )
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("identity_provider_subject", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "license_plans",
        sa.Column("plan_id", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("max_users", sa.Integer(), nullable=False),
        sa.Column("max_projects", sa.Integer(), nullable=False),
        sa.Column("max_websig_instances", sa.Integer(), nullable=False),
        sa.Column("enabled_modules", sa.String(length=1000), nullable=False),
        sa.Column("ai_enabled", sa.Boolean(), nullable=False),
        sa.Column("reporting_enabled", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("plan_id"),
    )
    op.create_table(
        "company_memberships",
        sa.Column("membership_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("user_id", sa.String(length=80), nullable=False),
        sa.Column("role", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("membership_id"),
    )
    op.create_index("ix_company_memberships_company_id", "company_memberships", ["company_id"])
    op.create_index("ix_company_memberships_user_id", "company_memberships", ["user_id"])
    op.create_table(
        "company_licenses",
        sa.Column("company_license_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("plan_id", sa.String(length=80), nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.ForeignKeyConstraint(["plan_id"], ["license_plans.plan_id"]),
        sa.PrimaryKeyConstraint("company_license_id"),
    )
    op.create_index("ix_company_licenses_company_id", "company_licenses", ["company_id"])


def downgrade() -> None:
    """Drop enterprise tenant, user, membership, and licensing tables."""

    op.drop_index("ix_company_licenses_company_id", table_name="company_licenses")
    op.drop_table("company_licenses")
    op.drop_index("ix_company_memberships_user_id", table_name="company_memberships")
    op.drop_index("ix_company_memberships_company_id", table_name="company_memberships")
    op.drop_table("company_memberships")
    op.drop_table("license_plans")
    op.drop_table("users")
    op.drop_table("companies")
