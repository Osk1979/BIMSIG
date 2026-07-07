"""Expand Project Provisioning Engine registry.

Revision ID: 20260707_005
Revises: 20260707_004
Create Date: 2026-07-07

ADR references:
- ADR-0003: Project provisioning as a port.
- ADR-0007: NAS integration.
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0014: Enterprise multitenancy.
- ADR-0015: Tower vs WEB SIG operational boundary.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260707_005"
down_revision: str | None = "20260707_004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add tenant scope, operation, and step document to provisioning requests."""

    op.add_column("provisioning_requests", sa.Column("company_id", sa.String(length=80), nullable=True))
    op.add_column(
        "provisioning_requests",
        sa.Column("operation", sa.String(length=80), nullable=False, server_default="websig"),
    )
    op.add_column(
        "provisioning_requests",
        sa.Column("steps_document", sa.Text(), nullable=False, server_default="[]"),
    )
    op.create_index("ix_provisioning_requests_company_id", "provisioning_requests", ["company_id"])
    with op.batch_alter_table("provisioning_requests") as batch_op:
        batch_op.create_foreign_key(
            "fk_provisioning_requests_company_id_companies",
            "companies",
            ["company_id"],
            ["company_id"],
        )


def downgrade() -> None:
    """Remove expanded Project Provisioning Engine registry fields."""

    with op.batch_alter_table("provisioning_requests") as batch_op:
        batch_op.drop_constraint(
            "fk_provisioning_requests_company_id_companies",
            type_="foreignkey",
        )
    op.drop_index("ix_provisioning_requests_company_id", table_name="provisioning_requests")
    op.drop_column("provisioning_requests", "steps_document")
    op.drop_column("provisioning_requests", "operation")
    op.drop_column("provisioning_requests", "company_id")
