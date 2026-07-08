from __future__ import annotations

from control_tower.domain.audit import AuditEvent
from control_tower.domain.enterprise import Company, CompanyLicense, CompanyMembership, LicensePlan, User
from control_tower.domain.nas import InformationAsset, InformationBackup, InformationSnapshot, InformationVersion
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


class FakeLicensePlanRepository:
    def __init__(self) -> None:
        self.plans: dict[str, LicensePlan] = {}

    def save(self, plan: LicensePlan) -> LicensePlan:
        self.plans[plan.plan_id] = plan
        return plan

    def list(self) -> list[LicensePlan]:
        return list(self.plans.values())

    def get(self, plan_id: str) -> LicensePlan | None:
        return self.plans.get(plan_id)


class FakeCompanyLicenseRepository:
    def __init__(self) -> None:
        self.licenses: dict[str, CompanyLicense] = {}

    def save(self, license_assignment: CompanyLicense) -> CompanyLicense:
        self.licenses[license_assignment.company_license_id] = license_assignment
        return license_assignment

    def list_by_company(self, company_id: str) -> list[CompanyLicense]:
        return [
            license_assignment
            for license_assignment in self.licenses.values()
            if license_assignment.company_id == company_id
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


class FakeInformationAssetRepository:
    def __init__(self) -> None:
        self.assets: dict[str, InformationAsset] = {}
        self.versions: dict[str, InformationVersion] = {}
        self.snapshots: dict[str, InformationSnapshot] = {}
        self.backups: dict[str, InformationBackup] = {}

    def save_asset(self, asset: InformationAsset) -> InformationAsset:
        self.assets[asset.asset_id] = asset
        return asset

    def list_assets_by_company(self, company_id: str) -> list[InformationAsset]:
        return [asset for asset in self.assets.values() if asset.company_id == company_id]

    def get_asset(self, asset_id: str) -> InformationAsset | None:
        return self.assets.get(asset_id)

    def save_version(self, version: InformationVersion) -> InformationVersion:
        self.versions[version.version_id] = version
        return version

    def list_versions(self, asset_id: str) -> list[InformationVersion]:
        return [version for version in self.versions.values() if version.asset_id == asset_id]

    def save_snapshot(self, snapshot: InformationSnapshot) -> InformationSnapshot:
        self.snapshots[snapshot.snapshot_id] = snapshot
        return snapshot

    def list_snapshots_by_company(self, company_id: str) -> list[InformationSnapshot]:
        return [snapshot for snapshot in self.snapshots.values() if snapshot.company_id == company_id]

    def save_backup(self, backup: InformationBackup) -> InformationBackup:
        self.backups[backup.backup_id] = backup
        return backup

    def list_backups_by_company(self, company_id: str) -> list[InformationBackup]:
        return [backup for backup in self.backups.values() if backup.company_id == company_id]


class FakeAuditEventRepository:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def save(self, event: AuditEvent) -> AuditEvent:
        self.events.append(event)
        return event

    def list(self, limit: int = 100) -> list[AuditEvent]:
        return self.events[-limit:]
