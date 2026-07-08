"""Add WEB SIG Factory governance fields.

Revision ID: 20260708_011
Revises: 20260708_010
Create Date: 2026-07-08

ADR references:
- ADR-0017: Project Provisioning Engine.
- ADR-0025: Corporate Portfolio Domain.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_011"
down_revision: str | None = "20260708_010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add controlled execution metadata to provisioning requests."""

    with op.batch_alter_table("provisioning_requests") as batch_op:
        batch_op.add_column(
            sa.Column(
                "execution_mode",
                sa.String(length=80),
                nullable=False,
                server_default="controlled",
            )
        )
        batch_op.add_column(sa.Column("approved_by", sa.String(length=160), nullable=True))


def downgrade() -> None:
    """Remove controlled execution metadata from provisioning requests."""

    with op.batch_alter_table("provisioning_requests") as batch_op:
        batch_op.drop_column("approved_by")
        batch_op.drop_column("execution_mode")
