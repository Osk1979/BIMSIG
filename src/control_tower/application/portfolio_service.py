"""Portfolio application service.

ADR references:
- ADR-0001: REV11 architecture baseline.
- ADR-0002: Layered modular API scaffold.
"""

from control_tower.domain.portfolio import PortfolioProject


class PortfolioService:
    """Coordinates portfolio project registration and lookup."""

    def __init__(self) -> None:
        self._projects: dict[str, PortfolioProject] = {}

    def register(self, project: PortfolioProject) -> PortfolioProject:
        """Register or replace a project in the tower portfolio."""

        self._projects[project.project_id] = project
        return project

    def list_projects(self) -> list[PortfolioProject]:
        """Return all registered portfolio projects."""

        return list(self._projects.values())

    def exists(self, project_id: str) -> bool:
        """Return whether a project is registered in the portfolio."""

        return project_id in self._projects
