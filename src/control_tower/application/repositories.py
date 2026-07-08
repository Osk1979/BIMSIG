"""Repository ports for durable Corporate Control Tower state.

ADR references:
- ADR-0002: Layered modular API scaffold.
- ADR-0005: Persistence strategy.
- ADR-0013: Database schema and migrations.
"""

from __future__ import annotations

from typing import Protocol

from control_tower.domain.audit import AuditEvent
from control_tower.domain.enterprise import (
    Company,
    CompanyLicense,
    CompanyMembership,
    LicensePlan,
    User,
)
from control_tower.domain.nas import InformationAsset, InformationBackup, InformationSnapshot, InformationVersion
from control_tower.domain.portfolio import PortfolioProject
from control_tower.domain.provisioning import ProvisioningRequest


class PortfolioProjectRepository(Protocol):
    """Persistence port for portfolio projects."""

    def save(self, project: PortfolioProject) -> PortfolioProject:
        """Persist a portfolio project."""

    def list(self) -> list[PortfolioProject]:
        """Return all persisted portfolio projects."""

    def list_by_company(self, company_id: str) -> list[PortfolioProject]:
        """Return projects for one company."""

    def get(self, project_id: str) -> PortfolioProject | None:
        """Return one persisted project when it exists."""

    def get_by_company(self, company_id: str, project_id: str) -> PortfolioProject | None:
        """Return one project inside one company when it exists."""

    def exists(self, project_id: str) -> bool:
        """Return whether a project exists."""


class ProvisioningRequestRepository(Protocol):
    """Persistence port for WEB SIG provisioning requests."""

    def save(self, request: ProvisioningRequest) -> ProvisioningRequest:
        """Persist a provisioning request."""

    def list(self) -> list[ProvisioningRequest]:
        """Return all persisted provisioning requests."""

    def list_by_company(self, company_id: str) -> list[ProvisioningRequest]:
        """Return persisted provisioning requests for one company."""


class AuditEventRepository(Protocol):
    """Persistence port for audit events."""

    def save(self, event: AuditEvent) -> AuditEvent:
        """Persist an audit event."""

    def list(self, limit: int = 100) -> list[AuditEvent]:
        """Return recent audit events."""


class CompanyRepository(Protocol):
    """Persistence port for enterprise companies."""

    def save(self, company: Company) -> Company:
        """Persist a company."""

    def list(self) -> list[Company]:
        """Return all companies."""

    def get(self, company_id: str) -> Company | None:
        """Return one company when it exists."""


class UserRepository(Protocol):
    """Persistence port for platform users."""

    def save(self, user: User) -> User:
        """Persist a user."""

    def list(self) -> list[User]:
        """Return all users."""

    def get(self, user_id: str) -> User | None:
        """Return one user when it exists."""


class CompanyMembershipRepository(Protocol):
    """Persistence port for company memberships."""

    def save(self, membership: CompanyMembership) -> CompanyMembership:
        """Persist a company membership."""

    def list_by_company(self, company_id: str) -> list[CompanyMembership]:
        """Return memberships for a company."""


class LicensePlanRepository(Protocol):
    """Persistence port for license plans."""

    def save(self, plan: LicensePlan) -> LicensePlan:
        """Persist a license plan."""

    def list(self) -> list[LicensePlan]:
        """Return license plans."""

    def get(self, plan_id: str) -> LicensePlan | None:
        """Return one license plan when it exists."""


class CompanyLicenseRepository(Protocol):
    """Persistence port for company license assignments."""

    def save(self, license_assignment: CompanyLicense) -> CompanyLicense:
        """Persist a company license assignment."""

    def list_by_company(self, company_id: str) -> list[CompanyLicense]:
        """Return license assignments for a company."""


class InformationAssetRepository(Protocol):
    """Persistence port for Corporate Information Center assets."""

    def save_asset(self, asset: InformationAsset) -> InformationAsset:
        """Persist an information asset."""

    def list_assets_by_company(self, company_id: str) -> list[InformationAsset]:
        """Return information assets for one company."""

    def get_asset(self, asset_id: str) -> InformationAsset | None:
        """Return one information asset when it exists."""

    def save_version(self, version: InformationVersion) -> InformationVersion:
        """Persist an information asset version."""

    def list_versions(self, asset_id: str) -> list[InformationVersion]:
        """Return versions for one asset."""

    def save_snapshot(self, snapshot: InformationSnapshot) -> InformationSnapshot:
        """Persist an information snapshot."""

    def list_snapshots_by_company(self, company_id: str) -> list[InformationSnapshot]:
        """Return snapshots for one company."""

    def save_backup(self, backup: InformationBackup) -> InformationBackup:
        """Persist an information backup manifest."""

    def list_backups_by_company(self, company_id: str) -> list[InformationBackup]:
        """Return backup manifests for one company."""
