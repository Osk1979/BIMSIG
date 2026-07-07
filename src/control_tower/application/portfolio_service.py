"""Portfolio application service.

ADR references:
- ADR-0001: REV11 architecture baseline.
- ADR-0002: Layered modular API scaffold.
- ADR-0005: Persistence strategy.
"""

from control_tower.domain.portfolio import PortfolioProject

from .repositories import PortfolioProjectRepository


class PortfolioService:
    """Coordinates portfolio project registration and lookup."""

    def __init__(self, repository: PortfolioProjectRepository) -> None:
        self._repository = repository

    def register(self, project: PortfolioProject) -> PortfolioProject:
        """Register or replace a project in the tower portfolio."""

        return self._repository.save(project)

    def list_projects(self) -> list[PortfolioProject]:
        """Return all registered portfolio projects."""

        return self._repository.list()

    def exists(self, project_id: str) -> bool:
        """Return whether a project is registered in the portfolio."""

        return self._repository.exists(project_id)
