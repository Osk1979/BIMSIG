"""Audit event domain model.

ADR references:
- ADR-0005: Persistence strategy.
- ADR-0006: Authentication and authorization.
- ADR-0013: Database schema and migrations.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    """State-changing action recorded by Corporate Control Tower."""

    event_id: int | None = None
    actor: str = Field(min_length=1, examples=["system"])
    action: str = Field(min_length=3, examples=["project.registered"])
    entity_type: str = Field(min_length=3, examples=["project"])
    entity_id: str = Field(min_length=1, examples=["PSZ-2026"])
    detail: str | None = None
    created_at: datetime | None = None
