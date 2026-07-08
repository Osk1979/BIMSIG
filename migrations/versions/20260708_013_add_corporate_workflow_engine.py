"""Add Corporate Workflow Engine tables.

Revision ID: 20260708_013
Revises: 20260708_012
Create Date: 2026-07-08

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0017: Project Provisioning Engine.
- ADR-0025: Corporate Portfolio Domain.
- ADR-0027: Corporate Control Tower operational flow.
- ADR-0029: Corporate Workflow Engine.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_013"
down_revision: str | None = "20260708_012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create Corporate Workflow Engine state and transition tables."""

    op.create_table(
        "corporate_workflows",
        sa.Column("workflow_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("project_id", sa.String(length=80), nullable=True),
        sa.Column("program_id", sa.String(length=80), nullable=True),
        sa.Column("current_stage", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("completed_stages_document", sa.Text(), nullable=False),
        sa.Column("rollback_available", sa.Boolean(), nullable=False),
        sa.Column("created_by", sa.String(length=160), nullable=False),
        sa.Column("updated_by", sa.String(length=160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.ForeignKeyConstraint(["project_id"], ["portfolio_projects.project_id"]),
        sa.PrimaryKeyConstraint("workflow_id"),
    )
    op.create_index("ix_corporate_workflows_company_id", "corporate_workflows", ["company_id"])
    op.create_index("ix_corporate_workflows_project_id", "corporate_workflows", ["project_id"])
    op.create_index("ix_corporate_workflows_program_id", "corporate_workflows", ["program_id"])
    op.create_index("ix_corporate_workflows_current_stage", "corporate_workflows", ["current_stage"])
    op.create_index("ix_corporate_workflows_status", "corporate_workflows", ["status"])

    op.create_table(
        "corporate_workflow_transitions",
        sa.Column("transition_id", sa.String(length=80), nullable=False),
        sa.Column("workflow_id", sa.String(length=80), nullable=False),
        sa.Column("company_id", sa.String(length=80), nullable=False),
        sa.Column("project_id", sa.String(length=80), nullable=True),
        sa.Column("from_stage", sa.String(length=80), nullable=True),
        sa.Column("to_stage", sa.String(length=80), nullable=False),
        sa.Column("actor", sa.String(length=160), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("rollback", sa.Boolean(), nullable=False),
        sa.Column("rollback_of", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["workflow_id"], ["corporate_workflows.workflow_id"]),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.ForeignKeyConstraint(["project_id"], ["portfolio_projects.project_id"]),
        sa.PrimaryKeyConstraint("transition_id"),
    )
    op.create_index("ix_corporate_workflow_transitions_workflow_id", "corporate_workflow_transitions", ["workflow_id"])
    op.create_index("ix_corporate_workflow_transitions_company_id", "corporate_workflow_transitions", ["company_id"])
    op.create_index("ix_corporate_workflow_transitions_project_id", "corporate_workflow_transitions", ["project_id"])
    op.create_index("ix_corporate_workflow_transitions_to_stage", "corporate_workflow_transitions", ["to_stage"])
    op.create_index("ix_corporate_workflow_transitions_rollback", "corporate_workflow_transitions", ["rollback"])


def downgrade() -> None:
    """Drop Corporate Workflow Engine tables."""

    op.drop_index("ix_corporate_workflow_transitions_rollback", table_name="corporate_workflow_transitions")
    op.drop_index("ix_corporate_workflow_transitions_to_stage", table_name="corporate_workflow_transitions")
    op.drop_index("ix_corporate_workflow_transitions_project_id", table_name="corporate_workflow_transitions")
    op.drop_index("ix_corporate_workflow_transitions_company_id", table_name="corporate_workflow_transitions")
    op.drop_index("ix_corporate_workflow_transitions_workflow_id", table_name="corporate_workflow_transitions")
    op.drop_table("corporate_workflow_transitions")
    op.drop_index("ix_corporate_workflows_status", table_name="corporate_workflows")
    op.drop_index("ix_corporate_workflows_current_stage", table_name="corporate_workflows")
    op.drop_index("ix_corporate_workflows_program_id", table_name="corporate_workflows")
    op.drop_index("ix_corporate_workflows_project_id", table_name="corporate_workflows")
    op.drop_index("ix_corporate_workflows_company_id", table_name="corporate_workflows")
    op.drop_table("corporate_workflows")
