"""Provisioning application service.

ADR references:
- ADR-0001: REV11 architecture baseline.
- ADR-0003: Project provisioning as a port.
- ADR-0005: Persistence strategy.
- ADR-0007: NAS integration.
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0014: Enterprise multitenancy.
- ADR-0015: Tower vs WEB SIG operational boundary.
"""

from uuid import uuid4

from pydantic import BaseModel, Field

from control_tower.domain.audit import AuditEvent
from control_tower.domain.enterprise import Company, CompanyMembership, User
from control_tower.domain.portfolio import PortfolioProject
from control_tower.domain.portfolio import ProjectStatus
from control_tower.domain.provisioning import (
    ProvisioningOperation,
    ProvisioningRequest,
    ProvisioningResourceType,
    ProvisioningStatus,
    ProvisioningStep,
)

from .enterprise_service import CompanyService, UserService
from .portfolio_service import PortfolioService
from .repositories import AuditEventRepository, ProvisioningRequestRepository


class ProjectProvisioningSpec(BaseModel):
    """Complete input for provisioning a BIMSIG Enterprise project stack."""

    company: Company
    project: PortfolioProject
    users: list[User] = Field(default_factory=list)
    memberships: list[CompanyMembership] = Field(default_factory=list)
    catalogs: list[str] = Field(default_factory=list)
    document_structure: list[str] = Field(
        default_factory=lambda: [
            "00_gobierno",
            "01_contratos",
            "02_bim",
            "03_gis",
            "04_reportes",
            "05_auditoria",
        ]
    )
    websig_slug: str | None = None
    dashboard_id: str | None = None


class ProvisioningService:
    """Coordinates WEB SIG provisioning requests for registered projects."""

    def __init__(
        self,
        portfolio: PortfolioService,
        repository: ProvisioningRequestRepository,
        audit_repository: AuditEventRepository | None = None,
    ) -> None:
        self._portfolio = portfolio
        self._repository = repository
        self._audit_repository = audit_repository

    def request_websig(self, project_id: str) -> ProvisioningRequest:
        """Create a WEB SIG provisioning request for a registered project."""

        project = self._portfolio.get_project(project_id)
        if project is None:
            raise ValueError(f"Project is not registered: {project_id}")
        request = ProvisioningRequest(
            request_id=f"PPE-{uuid4().hex[:12]}",
            project_id=project_id,
            company_id=project.company_id,
            operation=ProvisioningOperation.WEB_SIG,
            steps=[
                ProvisioningStep(
                    step_id="websig-request",
                    resource_type=ProvisioningResourceType.WEB_SIG,
                    name="Register WEB SIG provisioning intent",
                    reference=f"websig://{project.company_id}/{project.project_id}",
                )
            ],
        )
        saved = self._repository.save(request)
        self._portfolio.change_status(project_id, ProjectStatus.PROVISIONING_REQUESTED)
        self._audit(
            action="provisioning.websig_requested",
            entity_id=saved.request_id,
            detail=f"WEB SIG provisioning requested for project {saved.project_id}.",
        )
        return saved

    def list_requests(self) -> list[ProvisioningRequest]:
        """Return all WEB SIG provisioning requests."""

        return self._repository.list()

    def list_requests_for_company(self, company_id: str) -> list[ProvisioningRequest]:
        """Return provisioning requests for one company."""

        return self._repository.list_by_company(company_id)

    def _audit(self, action: str, entity_id: str, detail: str) -> None:
        if self._audit_repository is None:
            return
        self._audit_repository.save(
            AuditEvent(
                actor="system",
                action=action,
                entity_type="provisioning_request",
                entity_id=entity_id,
                detail=detail,
            )
        )


class ProjectProvisioningEngine:
    """Orchestrates enterprise project stack provisioning inside BIMSIG."""

    def __init__(
        self,
        companies: CompanyService,
        users: UserService,
        portfolio: PortfolioService,
        repository: ProvisioningRequestRepository,
        audit_repository: AuditEventRepository | None = None,
    ) -> None:
        self._companies = companies
        self._users = users
        self._portfolio = portfolio
        self._repository = repository
        self._audit_repository = audit_repository

    def provision_project_stack(self, spec: ProjectProvisioningSpec) -> ProvisioningRequest:
        """Provision the enterprise control-plane records for one project stack."""

        if spec.project.company_id != spec.company.company_id:
            raise ValueError("Project company_id must match provisioning company_id")

        company = self._companies.register(spec.company)
        project = self._portfolio.register_for_company(company.company_id, spec.project)
        for user in spec.users:
            self._users.register_user(user)
        for membership in spec.memberships:
            if membership.company_id != company.company_id:
                raise ValueError("Membership company_id must match provisioning company_id")
            self._users.add_membership(membership)

        steps = self._build_steps(spec)
        request = ProvisioningRequest(
            request_id=f"PPE-{uuid4().hex[:12]}",
            project_id=project.project_id,
            company_id=company.company_id,
            status=ProvisioningStatus.PROVISIONED,
            operation=ProvisioningOperation.PROJECT_STACK,
            steps=steps,
        )
        saved = self._repository.save(request)
        self._portfolio.change_status_for_company(
            company.company_id,
            project.project_id,
            ProjectStatus.ACTIVE,
        )
        self._audit(
            action="provisioning.project_stack_provisioned",
            entity_id=saved.request_id,
            detail=f"Enterprise project stack provisioned for {company.company_id}/{project.project_id}.",
        )
        return saved

    def _build_steps(self, spec: ProjectProvisioningSpec) -> list[ProvisioningStep]:
        company_id = spec.company.company_id
        project_id = spec.project.project_id
        websig_slug = spec.websig_slug or f"{company_id.lower()}-{project_id.lower()}"
        dashboard_id = spec.dashboard_id or f"DASH-{company_id}-{project_id}"
        steps = [
            self._step("company", ProvisioningResourceType.COMPANY, "Create Empresa", company_id),
            self._step("project", ProvisioningResourceType.PROJECT, "Create Proyecto", project_id),
            self._step(
                "websig",
                ProvisioningResourceType.WEB_SIG,
                "Create WEB SIG",
                f"websig://{company_id}/{websig_slug}",
            ),
            self._step(
                "postgis",
                ProvisioningResourceType.POSTGIS,
                "Create Base PostGIS",
                f"postgis://{company_id}/{project_id}",
            ),
            self._step(
                "nas",
                ProvisioningResourceType.NAS,
                "Create Espacio NAS",
                f"nas://{company_id}/{project_id}/websig/root",
            ),
            self._step(
                "documents",
                ProvisioningResourceType.DOCUMENT_STRUCTURE,
                "Create estructura documental",
                ",".join(spec.document_structure),
            ),
            self._step(
                "geoserver",
                ProvisioningResourceType.GEOSERVER,
                "Registrar GeoServer",
                f"geoserver://workspace/{company_id}_{project_id}",
            ),
            self._step(
                "dashboard",
                ProvisioningResourceType.DASHBOARD,
                "Crear Dashboard",
                f"dashboard://{dashboard_id}",
            ),
        ]
        steps.extend(
            self._step(
                f"user-{user.user_id}",
                ProvisioningResourceType.USER,
                "Crear Usuario",
                user.user_id,
            )
            for user in spec.users
        )
        steps.extend(
            self._step(
                f"role-{membership.membership_id}",
                ProvisioningResourceType.ROLE,
                "Crear Roles",
                f"{membership.company_id}/{membership.user_id}/{membership.role.value}",
            )
            for membership in spec.memberships
        )
        steps.extend(
            self._step(
                f"catalog-{index}",
                ProvisioningResourceType.CATALOG,
                "Crear Catalogos",
                catalog,
            )
            for index, catalog in enumerate(spec.catalogs, start=1)
        )
        return steps

    @staticmethod
    def _step(
        step_id: str,
        resource_type: ProvisioningResourceType,
        name: str,
        reference: str,
    ) -> ProvisioningStep:
        return ProvisioningStep(
            step_id=step_id,
            resource_type=resource_type,
            name=name,
            reference=reference,
        )

    def _audit(self, action: str, entity_id: str, detail: str) -> None:
        if self._audit_repository is None:
            return
        self._audit_repository.save(
            AuditEvent(
                actor="system",
                action=action,
                entity_type="provisioning_request",
                entity_id=entity_id,
                detail=detail,
            )
        )
