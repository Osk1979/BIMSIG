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
from control_tower.domain.portfolio import PortfolioProject
from control_tower.infrastructure.database import (
    SqlAlchemyPortfolioProjectRepository,
    SqlAlchemyProvisioningRequestRepository,
    SqlAlchemySessionProvider,
    create_database_engine,
    initialize_database,
)


class ProvisionWebSigPayload(BaseModel):
    """API payload to request a dedicated WEB SIG for a project."""

    project_id: str = Field(min_length=3)


def create_app(database_url: str | None = None) -> FastAPI:
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
    initialize_database(engine)
    sessions = SqlAlchemySessionProvider(engine)
    portfolio_repository = SqlAlchemyPortfolioProjectRepository(sessions)
    provisioning_repository = SqlAlchemyProvisioningRequestRepository(sessions)
    portfolio = PortfolioService(portfolio_repository)
    provisioning = ProvisioningService(portfolio, provisioning_repository)

    @app.get("/health")
    def health() -> dict[str, str]:
        """Return service health metadata."""

        return {"status": "ok", "revision": "REV12", "service": "corporate-control-tower"}

    @app.get("/api/v1/projects", response_model=list[PortfolioProject])
    def list_projects() -> list[PortfolioProject]:
        """List projects registered in the Corporate Control Tower portfolio."""

        return portfolio.list_projects()

    @app.post(
        "/api/v1/projects",
        response_model=PortfolioProject,
        status_code=status.HTTP_201_CREATED,
    )
    def register_project(project: PortfolioProject) -> PortfolioProject:
        """Register a project in the Corporate Control Tower portfolio."""

        return portfolio.register(project)

    @app.post("/api/v1/provisioning/websig", status_code=status.HTTP_202_ACCEPTED)
    def provision_websig(payload: ProvisionWebSigPayload) -> dict[str, str]:
        """Request creation of a dedicated WEB SIG for a registered project."""

        try:
            request = provisioning.request_websig(payload.project_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return request.model_dump()

    return app
