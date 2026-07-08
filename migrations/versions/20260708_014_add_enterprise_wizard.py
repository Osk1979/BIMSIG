"""Add Enterprise Wizard sessions.

Revision ID: 20260708_014
Revises: 20260708_013
Create Date: 2026-07-08

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0025: Corporate Portfolio Domain.
- ADR-0029: Corporate Workflow Engine.
- ADR-0030: Enterprise Wizard.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_014"
down_revision: str | None = "20260708_013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create Enterprise Wizard session table."""

    op.create_table(
        "enterprise_wizard_sessions",
        sa.Column("wizard_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=True),
        sa.Column("project_id", sa.String(length=80), nullable=True),
        sa.Column("workflow_id", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("current_step", sa.String(length=80), nullable=False),
        sa.Column("steps_document", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(length=160), nullable=False),
        sa.Column("updated_by", sa.String(length=160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("wizard_id"),
    )
    op.create_index("ix_enterprise_wizard_sessions_company_id", "enterprise_wizard_sessions", ["company_id"])
    op.create_index("ix_enterprise_wizard_sessions_project_id", "enterprise_wizard_sessions", ["project_id"])
    op.create_index("ix_enterprise_wizard_sessions_workflow_id", "enterprise_wizard_sessions", ["workflow_id"])
    op.create_index("ix_enterprise_wizard_sessions_status", "enterprise_wizard_sessions", ["status"])
    op.create_index("ix_enterprise_wizard_sessions_current_step", "enterprise_wizard_sessions", ["current_step"])


def downgrade() -> None:
    """Drop Enterprise Wizard session table."""

    op.drop_index("ix_enterprise_wizard_sessions_current_step", table_name="enterprise_wizard_sessions")
    op.drop_index("ix_enterprise_wizard_sessions_status", table_name="enterprise_wizard_sessions")
    op.drop_index("ix_enterprise_wizard_sessions_workflow_id", table_name="enterprise_wizard_sessions")
    op.drop_index("ix_enterprise_wizard_sessions_project_id", table_name="enterprise_wizard_sessions")
    op.drop_index("ix_enterprise_wizard_sessions_company_id", table_name="enterprise_wizard_sessions")
    op.drop_table("enterprise_wizard_sessions")
