from __future__ import annotations

from control_tower.domain.audit import AuditEvent
from control_tower.domain.portfolio import PortfolioProject
from control_tower.domain.provisioning import ProvisioningRequest


class FakePortfolioProjectRepository:
    def __init__(self) -> None:
        self.projects: dict[str, PortfolioProject] = {}

    def save(self, project: PortfolioProject) -> PortfolioProject:
        self.projects[project.project_id] = project
        return project

    def list(self) -> list[PortfolioProject]:
        return list(self.projects.values())

    def list_by_company(self, company_id: str) -> list[PortfolioProject]:
        return [project for project in self.projects.values() if project.company_id == company_id]

    def get(self, project_id: str) -> PortfolioProject | None:
        return self.projects.get(project_id)

    def get_by_company(self, company_id: str, project_id: str) -> PortfolioProject | None:
        project = self.projects.get(project_id)
        if project is None or project.company_id != company_id:
            return None
        return project

    def exists(self, project_id: str) -> bool:
        return project_id in self.projects


class FakeProvisioningRequestRepository:
    def __init__(self) -> None:
        self.requests: dict[str, ProvisioningRequest] = {}

    def save(self, request: ProvisioningRequest) -> ProvisioningRequest:
        self.requests[request.request_id] = request
        return request

    def list(self) -> list[ProvisioningRequest]:
        return list(self.requests.values())


class FakeAuditEventRepository:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def save(self, event: AuditEvent) -> AuditEvent:
        self.events.append(event)
        return event

    def list(self, limit: int = 100) -> list[AuditEvent]:
        return self.events[-limit:]
