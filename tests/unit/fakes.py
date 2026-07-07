from __future__ import annotations

from control_tower.domain.audit import AuditEvent
from control_tower.domain.enterprise import Company, CompanyMembership, User
from control_tower.domain.portfolio import PortfolioProject
from control_tower.domain.provisioning import ProvisioningRequest


class FakeCompanyRepository:
    def __init__(self) -> None:
        self.companies: dict[str, Company] = {}

    def save(self, company: Company) -> Company:
        self.companies[company.company_id] = company
        return company

    def list(self) -> list[Company]:
        return list(self.companies.values())

    def get(self, company_id: str) -> Company | None:
        return self.companies.get(company_id)


class FakeUserRepository:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}

    def save(self, user: User) -> User:
        self.users[user.user_id] = user
        return user

    def list(self) -> list[User]:
        return list(self.users.values())

    def get(self, user_id: str) -> User | None:
        return self.users.get(user_id)


class FakeMembershipRepository:
    def __init__(self) -> None:
        self.memberships: dict[str, CompanyMembership] = {}

    def save(self, membership: CompanyMembership) -> CompanyMembership:
        self.memberships[membership.membership_id] = membership
        return membership

    def list_by_company(self, company_id: str) -> list[CompanyMembership]:
        return [
            membership
            for membership in self.memberships.values()
            if membership.company_id == company_id
        ]


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

    def list_by_company(self, company_id: str) -> list[ProvisioningRequest]:
        return [request for request in self.requests.values() if request.company_id == company_id]


class FakeAuditEventRepository:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def save(self, event: AuditEvent) -> AuditEvent:
        self.events.append(event)
        return event

    def list(self, limit: int = 100) -> list[AuditEvent]:
        return self.events[-limit:]
