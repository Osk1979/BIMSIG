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

    def exists(self, project_id: str) -> bool:
        return project_id in self.projects


class FakeProvisioningRequestRepository:
    def __init__(self) -> None:
        self.requests: dict[str, ProvisioningRequest] = {}

    def save(self, request: ProvisioningRequest) -> ProvisioningRequest:
        self.requests[request.request_id] = request
        return request
