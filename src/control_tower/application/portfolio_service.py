"""Portfolio application service.

ADR references:
- ADR-0001: REV11 architecture baseline.
- ADR-0002: Layered modular API scaffold.
- ADR-0005: Persistence strategy.
"""

from control_tower.domain.audit import AuditEvent
from control_tower.domain.portfolio import PortfolioProject, ProjectStatus

from .repositories import AuditEventRepository, PortfolioProjectRepository


class PortfolioService:
    """Coordinates portfolio project registration and lookup."""

    def __init__(
        self,
        repository: PortfolioProjectRepository,
        audit_repository: AuditEventRepository | None = None,
    ) -> None:
        self._repository = repository
        self._audit_repository = audit_repository

    def register(self, project: PortfolioProject) -> PortfolioProject:
        """Register or replace a project in the tower portfolio."""

        saved = self._repository.save(project)
        self._audit(
            action="project.registered",
            entity_id=saved.project_id,
            detail=f"Project registered with status {saved.status.value}.",
        )
        return saved

    def list_projects(self) -> list[PortfolioProject]:
        """Return all registered portfolio projects."""

        return self._repository.list()

    def exists(self, project_id: str) -> bool:
        """Return whether a project is registered in the portfolio."""

        return self._repository.exists(project_id)

    def get_project(self, project_id: str) -> PortfolioProject | None:
        """Return a project by identifier when it exists."""

        return self._repository.get(project_id)

    def change_status(self, project_id: str, status: ProjectStatus) -> PortfolioProject:
        """Change the governance status of a registered project."""

        project = self._repository.get(project_id)
        if project is None:
            raise ValueError(f"Project is not registered: {project_id}")
        updated = project.model_copy(update={"status": status})
        saved = self._repository.save(updated)
        self._audit(
            action="project.status_changed",
            entity_id=saved.project_id,
            detail=f"Project status changed to {saved.status.value}.",
        )
        return saved

    def summary(self) -> dict[str, int]:
        """Return portfolio counts by governance status."""

        projects = self.list_projects()
        summary = {"total_projects": len(projects)}
        for project_status in ProjectStatus:
            summary[project_status.value] = sum(
                1 for project in projects if project.status == project_status
            )
        return summary

    def _audit(self, action: str, entity_id: str, detail: str) -> None:
        if self._audit_repository is None:
            return
        self._audit_repository.save(
            AuditEvent(
                actor="system",
                action=action,
                entity_type="project",
                entity_id=entity_id,
                detail=detail,
            )
        )
