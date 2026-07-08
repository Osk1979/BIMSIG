"""FastAPI application factory for Corporate Control Tower REV12.

ADR references:
- ADR-0001: REV11 architecture baseline.
- ADR-0002: Layered modular API scaffold.
- ADR-0003: Project provisioning as a port.
- ADR-0005: Persistence strategy.
"""

import os

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from control_tower import __version__
from control_tower.application.dashboard_service import DashboardService
from control_tower.application.enterprise_service import CompanyService, LicensingService, UserService
from control_tower.application.nas_service import NasInformationCenterService
from control_tower.application.portfolio_service import PortfolioService
from control_tower.application.provisioning_service import (
    ProjectProvisioningEngine,
    ProjectProvisioningSpec,
    ProvisioningService,
)
from control_tower.domain.audit import AuditEvent
from control_tower.domain.dashboard import CorporateDashboard
from control_tower.domain.enterprise import Company, CompanyLicense, CompanyMembership, LicensePlan, User
from control_tower.domain.nas import (
    InformationAsset,
    InformationBackup,
    InformationPermission,
    InformationSnapshot,
    InformationVersion,
)
from control_tower.domain.portfolio import PortfolioProject, ProjectStatus
from control_tower.domain.provisioning import ProvisioningRequest
from control_tower.infrastructure.database import (
    SqlAlchemyAuditEventRepository,
    SqlAlchemyCompanyLicenseRepository,
    SqlAlchemyCompanyMembershipRepository,
    SqlAlchemyCompanyRepository,
    SqlAlchemyInformationAssetRepository,
    SqlAlchemyLicensePlanRepository,
    SqlAlchemyPortfolioProjectRepository,
    SqlAlchemyProvisioningRequestRepository,
    SqlAlchemySessionProvider,
    SqlAlchemyUserRepository,
    check_database,
    create_database_engine,
    initialize_database,
)
from control_tower.infrastructure.adapters.provisioning import default_project_stack_adapters
from control_tower.presentation.dashboard_ui import render_dashboard_html


class ProvisionWebSigPayload(BaseModel):
    """API payload to request a dedicated WEB SIG for a project."""

    project_id: str = Field(min_length=3)


class GovernanceStatusPayload(BaseModel):
    """API payload to change project governance status."""

    status: ProjectStatus


class AssetVersionPayload(BaseModel):
    """API payload to register an information asset version."""

    version: str = Field(min_length=1)
    logical_uri: str = Field(min_length=6)
    checksum_sha256: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class AssetMetadataPayload(BaseModel):
    """API payload to merge information asset metadata."""

    metadata: dict[str, str]


class AssetPermissionPayload(BaseModel):
    """API payload to set one information asset permission."""

    principal: str = Field(min_length=3)
    permission: InformationPermission


class SnapshotPayload(BaseModel):
    """API payload to create an information snapshot."""

    name: str = Field(min_length=3)
    asset_ids: list[str] = Field(default_factory=list)
    project_id: str | None = Field(default=None, min_length=3)
    metadata: dict[str, str] = Field(default_factory=dict)


class BackupPayload(BaseModel):
    """API payload to register an information backup."""

    logical_uri: str = Field(min_length=6)
    project_id: str | None = Field(default=None, min_length=3)
    snapshot_id: str | None = Field(default=None, min_length=3)
    checksum_sha256: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


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
    company_repository = SqlAlchemyCompanyRepository(sessions)
    user_repository = SqlAlchemyUserRepository(sessions)
    membership_repository = SqlAlchemyCompanyMembershipRepository(sessions)
    license_plan_repository = SqlAlchemyLicensePlanRepository(sessions)
    company_license_repository = SqlAlchemyCompanyLicenseRepository(sessions)
    information_repository = SqlAlchemyInformationAssetRepository(sessions)
    portfolio_repository = SqlAlchemyPortfolioProjectRepository(sessions)
    provisioning_repository = SqlAlchemyProvisioningRequestRepository(sessions)
    companies = CompanyService(company_repository, audit_repository)
    users = UserService(user_repository, membership_repository, companies, audit_repository)
    licensing = LicensingService(
        license_plan_repository,
        company_license_repository,
        companies,
        audit_repository,
    )
    portfolio = PortfolioService(portfolio_repository, audit_repository)
    provisioning = ProvisioningService(portfolio, provisioning_repository, audit_repository)
    project_stack_adapters = default_project_stack_adapters(
        nas_root=os.getenv("CONTROL_TOWER_NAS_ROOT"),
        postgis_database_url=os.getenv("CONTROL_TOWER_POSTGIS_DATABASE_URL"),
        geoserver_url=os.getenv("CONTROL_TOWER_GEOSERVER_URL"),
        geoserver_user=os.getenv("CONTROL_TOWER_GEOSERVER_USER"),
        geoserver_password=os.getenv("CONTROL_TOWER_GEOSERVER_PASSWORD"),
    )
    provisioning_engine = ProjectProvisioningEngine(
        companies,
        users,
        portfolio,
        provisioning_repository,
        project_stack_adapters,
        audit_repository,
    )
    dashboard = DashboardService(companies, users, licensing, portfolio, provisioning)
    nas = NasInformationCenterService(information_repository, companies, portfolio, audit_repository)

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

    @app.get("/api/v1/companies/{company_id}/portfolio/summary")
    def company_portfolio_summary(company_id: str) -> dict[str, int]:
        """Return portfolio status counts for one company."""

        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return portfolio.summary_for_company(company_id)

    @app.get("/dashboard", response_class=HTMLResponse)
    def dashboard_ui() -> HTMLResponse:
        """Return the integrated corporate executive dashboard UI."""

        return HTMLResponse(render_dashboard_html())

    @app.get("/api/v1/companies/{company_id}/dashboard/executive", response_model=CorporateDashboard)
    def executive_dashboard(company_id: str) -> CorporateDashboard:
        """Return the company-scoped executive dashboard read model."""

        try:
            return dashboard.executive_dashboard(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get("/api/v1/companies", response_model=list[Company])
    def list_companies() -> list[Company]:
        """List enterprise companies."""

        return companies.list_companies()

    @app.post("/api/v1/companies", response_model=Company, status_code=status.HTTP_201_CREATED)
    def register_company(company: Company) -> Company:
        """Register an enterprise company."""

        return companies.register(company)

    @app.get("/api/v1/companies/{company_id}", response_model=Company)
    def get_company(company_id: str) -> Company:
        """Return one enterprise company."""

        company = companies.get_company(company_id)
        if company is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return company

    @app.get("/api/v1/users", response_model=list[User])
    def list_users() -> list[User]:
        """List platform users."""

        return users.list_users()

    @app.post("/api/v1/users", response_model=User, status_code=status.HTTP_201_CREATED)
    def register_user(user: User) -> User:
        """Register a platform user."""

        return users.register_user(user)

    @app.get("/api/v1/companies/{company_id}/memberships", response_model=list[CompanyMembership])
    def list_company_memberships(company_id: str) -> list[CompanyMembership]:
        """List memberships for a company."""

        try:
            return users.list_memberships(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/memberships",
        response_model=CompanyMembership,
        status_code=status.HTTP_201_CREATED,
    )
    def add_company_membership(
        company_id: str,
        membership: CompanyMembership,
    ) -> CompanyMembership:
        """Assign a user role inside a company."""

        if membership.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Membership company_id must match path company_id",
            )
        try:
            return users.add_membership(membership)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get("/api/v1/license-plans", response_model=list[LicensePlan])
    def list_license_plans() -> list[LicensePlan]:
        """List enterprise license plans."""

        return licensing.list_plans()

    @app.post("/api/v1/license-plans", response_model=LicensePlan, status_code=status.HTTP_201_CREATED)
    def create_license_plan(plan: LicensePlan) -> LicensePlan:
        """Create an enterprise license plan."""

        return licensing.create_plan(plan)

    @app.get("/api/v1/companies/{company_id}/licenses", response_model=list[CompanyLicense])
    def list_company_licenses(company_id: str) -> list[CompanyLicense]:
        """List licenses assigned to a company."""

        try:
            return licensing.list_company_licenses(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get("/api/v1/companies/{company_id}/nas/assets", response_model=list[InformationAsset])
    def list_information_assets(company_id: str) -> list[InformationAsset]:
        """List Corporate Information Center assets for one company."""

        try:
            return nas.list_assets(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/nas/assets",
        response_model=InformationAsset,
        status_code=status.HTTP_201_CREATED,
    )
    def register_information_asset(company_id: str, asset: InformationAsset) -> InformationAsset:
        """Register a Corporate Information Center asset."""

        if asset.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Asset company_id must match path company_id",
            )
        try:
            return nas.register_asset(asset)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get("/api/v1/nas/assets/{asset_id}", response_model=InformationAsset)
    def get_information_asset(asset_id: str) -> InformationAsset:
        """Return one Corporate Information Center asset."""

        asset = nas.get_asset(asset_id)
        if asset is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Information asset not found")
        return asset

    @app.post("/api/v1/nas/assets/{asset_id}/versions", response_model=InformationVersion)
    def register_information_version(asset_id: str, payload: AssetVersionPayload) -> InformationVersion:
        """Register an immutable version for an information asset."""

        try:
            return nas.register_version(
                asset_id=asset_id,
                version=payload.version,
                logical_uri=payload.logical_uri,
                checksum_sha256=payload.checksum_sha256,
                metadata=payload.metadata,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get("/api/v1/nas/assets/{asset_id}/versions", response_model=list[InformationVersion])
    def list_information_versions(asset_id: str) -> list[InformationVersion]:
        """List versions for an information asset."""

        try:
            return nas.list_versions(asset_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.patch("/api/v1/nas/assets/{asset_id}/metadata", response_model=InformationAsset)
    def update_information_metadata(asset_id: str, payload: AssetMetadataPayload) -> InformationAsset:
        """Merge metadata into an information asset."""

        try:
            return nas.update_metadata(asset_id, payload.metadata)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.patch("/api/v1/nas/assets/{asset_id}/permissions", response_model=InformationAsset)
    def set_information_permission(asset_id: str, payload: AssetPermissionPayload) -> InformationAsset:
        """Set a permission on an information asset."""

        try:
            return nas.set_permission(asset_id, payload.principal, payload.permission)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.patch("/api/v1/nas/assets/{asset_id}/archive", response_model=InformationAsset)
    def archive_information_asset(asset_id: str) -> InformationAsset:
        """Archive an information asset registry entry."""

        try:
            return nas.archive_asset(asset_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get("/api/v1/companies/{company_id}/nas/snapshots", response_model=list[InformationSnapshot])
    def list_information_snapshots(company_id: str) -> list[InformationSnapshot]:
        """List information snapshots for one company."""

        try:
            return nas.list_snapshots(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post("/api/v1/companies/{company_id}/nas/snapshots", response_model=InformationSnapshot)
    def create_information_snapshot(company_id: str, payload: SnapshotPayload) -> InformationSnapshot:
        """Create an information snapshot manifest."""

        try:
            return nas.create_snapshot(
                company_id=company_id,
                name=payload.name,
                asset_ids=payload.asset_ids,
                project_id=payload.project_id,
                metadata=payload.metadata,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get("/api/v1/companies/{company_id}/nas/backups", response_model=list[InformationBackup])
    def list_information_backups(company_id: str) -> list[InformationBackup]:
        """List information backup manifests for one company."""

        try:
            return nas.list_backups(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post("/api/v1/companies/{company_id}/nas/backups", response_model=InformationBackup)
    def register_information_backup(company_id: str, payload: BackupPayload) -> InformationBackup:
        """Register an information backup manifest."""

        try:
            return nas.register_backup(
                company_id=company_id,
                logical_uri=payload.logical_uri,
                project_id=payload.project_id,
                snapshot_id=payload.snapshot_id,
                checksum_sha256=payload.checksum_sha256,
                metadata=payload.metadata,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/licenses",
        response_model=CompanyLicense,
        status_code=status.HTTP_201_CREATED,
    )
    def assign_company_license(
        company_id: str,
        license_assignment: CompanyLicense,
    ) -> CompanyLicense:
        """Assign a license plan to a company."""

        if license_assignment.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="License company_id must match path company_id",
            )
        try:
            return licensing.assign_license(license_assignment)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get("/api/v1/projects", response_model=list[PortfolioProject])
    def list_projects() -> list[PortfolioProject]:
        """List projects registered in the Corporate Control Tower portfolio."""

        return portfolio.list_projects()

    @app.get("/api/v1/companies/{company_id}/projects", response_model=list[PortfolioProject])
    def list_company_projects(company_id: str) -> list[PortfolioProject]:
        """List projects registered for one company."""

        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return portfolio.list_projects_for_company(company_id)

    @app.get("/api/v1/projects/{project_id}", response_model=PortfolioProject)
    def get_project(project_id: str) -> PortfolioProject:
        """Return one portfolio project."""

        project = portfolio.get_project(project_id)
        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return project

    @app.get("/api/v1/companies/{company_id}/projects/{project_id}", response_model=PortfolioProject)
    def get_company_project(company_id: str, project_id: str) -> PortfolioProject:
        """Return one project inside one company."""

        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        project = portfolio.get_project_for_company(company_id, project_id)
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

    @app.post(
        "/api/v1/companies/{company_id}/projects",
        response_model=PortfolioProject,
        status_code=status.HTTP_201_CREATED,
    )
    def register_company_project(company_id: str, project: PortfolioProject) -> PortfolioProject:
        """Register a project inside one company."""

        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        try:
            return portfolio.register_for_company(company_id, project)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

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

    @app.patch(
        "/api/v1/companies/{company_id}/projects/{project_id}/governance-status",
        response_model=PortfolioProject,
    )
    def change_company_governance_status(
        company_id: str,
        project_id: str,
        payload: GovernanceStatusPayload,
    ) -> PortfolioProject:
        """Change project governance status inside one company."""

        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        try:
            return portfolio.change_status_for_company(company_id, project_id, payload.status)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/provisioning/websig",
        response_model=ProvisioningRequest,
        status_code=status.HTTP_202_ACCEPTED,
    )
    def provision_websig(payload: ProvisionWebSigPayload) -> ProvisioningRequest:
        """Request creation of a dedicated WEB SIG for a registered project."""

        try:
            request = provisioning.request_websig(payload.project_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return request

    @app.post(
        "/api/v1/companies/{company_id}/provisioning/project-stack",
        response_model=ProvisioningRequest,
        status_code=status.HTTP_202_ACCEPTED,
    )
    def provision_project_stack(company_id: str, payload: ProjectProvisioningSpec) -> ProvisioningRequest:
        """Provision a complete BIMSIG Enterprise project stack."""

        if payload.company.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provisioning company_id must match path company_id",
            )
        try:
            return provisioning_engine.provision_project_stack(payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/provisioning/project-stack/dry-run",
        response_model=ProvisioningRequest,
        status_code=status.HTTP_200_OK,
    )
    def dry_run_project_stack(company_id: str, payload: ProjectProvisioningSpec) -> ProvisioningRequest:
        """Return a project-stack provisioning plan without side effects."""

        if payload.company.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provisioning company_id must match path company_id",
            )
        try:
            return provisioning_engine.dry_run_project_stack(payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/provisioning/project-stack/execute",
        response_model=ProvisioningRequest,
        status_code=status.HTTP_202_ACCEPTED,
    )
    def execute_project_stack(company_id: str, payload: ProjectProvisioningSpec) -> ProvisioningRequest:
        """Execute project-stack provisioning through configured adapters."""

        return provision_project_stack(company_id, payload)

    @app.get("/api/v1/provisioning/websig", response_model=list[ProvisioningRequest])
    def list_websig_provisioning_requests() -> list[ProvisioningRequest]:
        """List WEB SIG provisioning requests."""

        return provisioning.list_requests()

    @app.get("/api/v1/companies/{company_id}/provisioning/websig", response_model=list[ProvisioningRequest])
    def list_company_websig_provisioning_requests(company_id: str) -> list[ProvisioningRequest]:
        """List provisioning requests for one company."""

        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return provisioning.list_requests_for_company(company_id)

    @app.get("/api/v1/audit/events", response_model=list[AuditEvent])
    def list_audit_events(limit: int = 100) -> list[AuditEvent]:
        """List recent audit events."""

        return audit_repository.list(limit=limit)

    return app
