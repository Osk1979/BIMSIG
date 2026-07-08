"""Add corporate user security tables.

Revision ID: 20260708_008
Revises: 20260708_007
Create Date: 2026-07-08

ADR references:
- ADR-0006: Authentication and authorization.
- ADR-0014: Enterprise multitenancy.
- ADR-0016: Enterprise licensing.
- ADR-0020: Corporate user security system.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_008"
down_revision: str | None = "20260708_007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create corporate user security tables."""

    op.create_table(
        "specialties",
        sa.Column("specialty_id", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.PrimaryKeyConstraint("specialty_id"),
    )
    op.create_table(
        "user_specialties",
        sa.Column("user_specialty_id", sa.String(length=80), nullable=False),
        sa.Column("user_id", sa.String(length=80), nullable=False),
        sa.Column("specialty_id", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["specialty_id"], ["specialties.specialty_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("user_specialty_id"),
    )
    op.create_index("ix_user_specialties_specialty_id", "user_specialties", ["specialty_id"])
    op.create_index("ix_user_specialties_user_id", "user_specialties", ["user_id"])
    op.create_table(
        "project_memberships",
        sa.Column("project_membership_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("project_id", sa.String(length=80), nullable=False),
        sa.Column("user_id", sa.String(length=80), nullable=False),
        sa.Column("role", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.ForeignKeyConstraint(["project_id"], ["portfolio_projects.project_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("project_membership_id"),
    )
    op.create_index("ix_project_memberships_company_id", "project_memberships", ["company_id"])
    op.create_index("ix_project_memberships_project_id", "project_memberships", ["project_id"])
    op.create_index("ix_project_memberships_user_id", "project_memberships", ["user_id"])
    op.create_table(
        "role_permissions",
        sa.Column("role_permission_id", sa.String(length=80), nullable=False),
        sa.Column("role", sa.String(length=80), nullable=False),
        sa.Column("scope", sa.String(length=80), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint("role_permission_id"),
    )
    op.create_index("ix_role_permissions_role", "role_permissions", ["role"])
    op.create_table(
        "auth_identities",
        sa.Column("identity_id", sa.String(length=80), nullable=False),
        sa.Column("user_id", sa.String(length=80), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("identity_id"),
        sa.UniqueConstraint("provider", "subject"),
    )
    op.create_index("ix_auth_identities_provider", "auth_identities", ["provider"])
    op.create_index("ix_auth_identities_subject", "auth_identities", ["subject"])
    op.create_index("ix_auth_identities_user_id", "auth_identities", ["user_id"])
    op.create_table(
        "user_history_events",
        sa.Column("history_id", sa.String(length=120), nullable=False),
        sa.Column("user_id", sa.String(length=80), nullable=False),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("detail", sa.String(length=1000), nullable=True),
        sa.Column("company_id", sa.String(length=80), nullable=True),
        sa.Column("project_id", sa.String(length=80), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("history_id"),
    )
    op.create_index("ix_user_history_events_action", "user_history_events", ["action"])
    op.create_index("ix_user_history_events_company_id", "user_history_events", ["company_id"])
    op.create_index("ix_user_history_events_project_id", "user_history_events", ["project_id"])
    op.create_index("ix_user_history_events_user_id", "user_history_events", ["user_id"])


def downgrade() -> None:
    """Drop corporate user security tables."""

    op.drop_index("ix_user_history_events_user_id", table_name="user_history_events")
    op.drop_index("ix_user_history_events_project_id", table_name="user_history_events")
    op.drop_index("ix_user_history_events_company_id", table_name="user_history_events")
    op.drop_index("ix_user_history_events_action", table_name="user_history_events")
    op.drop_table("user_history_events")
    op.drop_index("ix_auth_identities_user_id", table_name="auth_identities")
    op.drop_index("ix_auth_identities_subject", table_name="auth_identities")
    op.drop_index("ix_auth_identities_provider", table_name="auth_identities")
    op.drop_table("auth_identities")
    op.drop_index("ix_role_permissions_role", table_name="role_permissions")
    op.drop_table("role_permissions")
    op.drop_index("ix_project_memberships_user_id", table_name="project_memberships")
    op.drop_index("ix_project_memberships_project_id", table_name="project_memberships")
    op.drop_index("ix_project_memberships_company_id", table_name="project_memberships")
    op.drop_table("project_memberships")
    op.drop_index("ix_user_specialties_user_id", table_name="user_specialties")
    op.drop_index("ix_user_specialties_specialty_id", table_name="user_specialties")
    op.drop_table("user_specialties")
    op.drop_table("specialties")
