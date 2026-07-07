"""FastAPI application factory for Corporate Control Tower REV12.

ADR references:
- ADR-0001: REV11 architecture baseline.
- ADR-0002: Layered modular API scaffold.
- ADR-0003: Project provisioning as a port.
- ADR-0005: Persistence strategy.
"""

import os

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from control_tower import __version__
from control_tower.application.portfolio_service import PortfolioService
from control_tower.application.provisioning_service import ProvisioningService
from control_tower.domain.audit import AuditEvent
from control_tower.domain.portfolio import PortfolioProject, ProjectStatus
from control_tower.domain.provisioning import ProvisioningRequest
from control_tower.infrastructure.database import (
    SqlAlchemyAuditEventRepository,
    SqlAlchemyPortfolioProjectRepository,
    SqlAlchemyProvisioningRequestRepository,
    SqlAlchemySessionProvider,
    check_database,
    create_database_engine,
    initialize_database,
)


class ProvisionWebSigPayload(BaseModel):
    """API payload to request a dedicated WEB SIG for a project."""

    project_id: str = Field(min_length=3)


class GovernanceStatusPayload(BaseModel):
    """API payload to change project governance status."""

    status: ProjectStatus


def create_app(database_url: str | None = None, initialize_schema: bool = True) -> FastAPI:
    """Create the Corporate Control Tower API application."""

    app = FastAPI(
        title="Corporate Control Tower REV12",
        version=__version__,
        description="Portfolio governance and WEB SIG provisioning API for BIMSIG Enterprise.",
    )
    resolved_database_url = database_url or os.getenv(
        "CONTROL_TOWER_DATABASE_URL",
        "sqlite:///./control_tower.db",
    )
    engine = create_database_engine(resolved_database_url)
    if initialize_schema:
        initialize_database(engine)
    sessions = SqlAlchemySessionProvider(engine)
    audit_repository = SqlAlchemyAuditEventRepository(sessions)
    portfolio_repository = SqlAlchemyPortfolioProjectRepository(sessions)
    provisioning_repository = SqlAlchemyProvisioningRequestRepository(sessions)
    portfolio = PortfolioService(portfolio_repository, audit_repository)
    provisioning = ProvisioningService(portfolio, provisioning_repository, audit_repository)

    @app.get("/health")
    def health() -> dict[str, str]:
        """Return service health metadata."""

        return {"status": "ok", "revision": "REV12", "service": "corporate-control-tower"}

    @app.get("/api/v1/operational/health")
    def operational_health() -> dict[str, str]:
        """Return operational health including database connectivity."""

        check_database(engine)
        return {
            "status": "ok",
            "revision": "REV12",
            "service": "corporate-control-tower",
            "database": "ok",
        }

    @app.get("/api/v1/portfolio/summary")
    def portfolio_summary() -> dict[str, int]:
        """Return portfolio status counts."""

        return portfolio.summary()

    @app.get("/api/v1/projects", response_model=list[PortfolioProject])
    def list_projects() -> list[PortfolioProject]:
        """List projects registered in the Corporate Control Tower portfolio."""

        return portfolio.list_projects()

    @app.get("/api/v1/projects/{project_id}", response_model=PortfolioProject)
    def get_project(project_id: str) -> PortfolioProject:
        """Return one portfolio project."""

        project = portfolio.get_project(project_id)
        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return project

    @app.post(
        "/api/v1/projects",
        response_model=PortfolioProject,
        status_code=status.HTTP_201_CREATED,
    )
    def register_project(project: PortfolioProject) -> PortfolioProject:
        """Register a project in the Corporate Control Tower portfolio."""

        return portfolio.register(project)

    @app.patch("/api/v1/projects/{project_id}/governance-status", response_model=PortfolioProject)
    def change_governance_status(
        project_id: str,
        payload: GovernanceStatusPayload,
    ) -> PortfolioProject:
        """Change project governance status."""

        try:
            return portfolio.change_status(project_id, payload.status)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post("/api/v1/provisioning/websig", status_code=status.HTTP_202_ACCEPTED)
    def provision_websig(payload: ProvisionWebSigPayload) -> dict[str, str]:
        """Request creation of a dedicated WEB SIG for a registered project."""

        try:
            request = provisioning.request_websig(payload.project_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return request.model_dump()

    @app.get("/api/v1/provisioning/websig", response_model=list[ProvisioningRequest])
    def list_websig_provisioning_requests() -> list[ProvisioningRequest]:
        """List WEB SIG provisioning requests."""

        return provisioning.list_requests()

    @app.get("/api/v1/audit/events", response_model=list[AuditEvent])
    def list_audit_events(limit: int = 100) -> list[AuditEvent]:
        """List recent audit events."""

        return audit_repository.list(limit=limit)

    return app
