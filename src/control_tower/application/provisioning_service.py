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
from control_tower.domain.portfolio import ProjectLifecycleStage, ProjectStatus
from control_tower.domain.provisioning import (
    ProvisioningExecutionMode,
    ProvisioningOperation,
    ProvisioningRequest,
    ProvisioningResourceType,
    ProvisioningStatus,
    ProvisioningStep,
    ProvisioningStepStatus,
    WebSigFactoryBlueprint,
)

from .enterprise_service import CompanyService, UserService
from .portfolio_service import PortfolioService
from .provisioning_adapters import ProvisioningAdapter
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
    factory_blueprint: WebSigFactoryBlueprint = Field(default_factory=WebSigFactoryBlueprint)
    approved_by: str | None = Field(default=None, min_length=3)


class ProjectProvisioningContext(BaseModel):
    """Adapter context for one project-stack provisioning execution."""

    company_id: str
    project_id: str
    websig_slug: str
    websig_url: str
    nas_root_uri: str
    postgis_schema_name: str
    geoserver_workspace: str
    dashboard_id: str
    document_structure: list[str]
    catalogs: list[str]
    enabled_modules: list[str]


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
        adapters: list[ProvisioningAdapter] | None = None,
        audit_repository: AuditEventRepository | None = None,
    ) -> None:
        self._companies = companies
        self._users = users
        self._portfolio = portfolio
        self._repository = repository
        self._adapters = adapters or []
        self._audit_repository = audit_repository

    def dry_run_project_stack(self, spec: ProjectProvisioningSpec) -> ProvisioningRequest:
        """Build a project-stack provisioning plan without side effects."""

        self._validate_spec(spec)
        context = self._context(spec)
        return ProvisioningRequest(
            request_id=f"PPE-DRYRUN-{uuid4().hex[:8]}",
            project_id=spec.project.project_id,
            company_id=spec.company.company_id,
            status=ProvisioningStatus.REQUESTED,
            operation=ProvisioningOperation.PROJECT_STACK,
            execution_mode=ProvisioningExecutionMode.DRY_RUN,
            steps=self._build_steps(spec, context, dry_run=True),
        )

    def dry_run_websig_factory(self, spec: ProjectProvisioningSpec) -> ProvisioningRequest:
        """Build a governed WEB SIG Factory plan without side effects."""

        self._validate_spec(spec)
        context = self._context(spec)
        return ProvisioningRequest(
            request_id=f"WSF-DRYRUN-{uuid4().hex[:8]}",
            project_id=spec.project.project_id,
            company_id=spec.company.company_id,
            status=ProvisioningStatus.REQUESTED,
            operation=ProvisioningOperation.WEB_SIG_FACTORY,
            execution_mode=ProvisioningExecutionMode.DRY_RUN,
            steps=self._build_steps(spec, context, dry_run=True, operation=ProvisioningOperation.WEB_SIG_FACTORY),
        )

    def execute_websig_factory(self, spec: ProjectProvisioningSpec) -> ProvisioningRequest:
        """Execute controlled WEB SIG Factory provisioning for one project."""

        return self._provision(spec, operation=ProvisioningOperation.WEB_SIG_FACTORY)

    def provision_project_stack(self, spec: ProjectProvisioningSpec) -> ProvisioningRequest:
        """Provision the enterprise control-plane records for one project stack."""

        return self._provision(spec, operation=ProvisioningOperation.PROJECT_STACK)

    def _provision(
        self,
        spec: ProjectProvisioningSpec,
        operation: ProvisioningOperation,
    ) -> ProvisioningRequest:
        self._validate_spec(spec)
        if spec.approved_by is None:
            raise ValueError("Controlled provisioning requires approved_by")
        context = self._context(spec)

        company = self._companies.register(spec.company)
        project = self._portfolio.register_for_company(company.company_id, spec.project)
        for user in spec.users:
            self._users.register_user(user)
        for membership in spec.memberships:
            if membership.company_id != company.company_id:
                raise ValueError("Membership company_id must match provisioning company_id")
            self._users.add_membership(membership)

        steps = self._build_steps(spec, context, dry_run=False, operation=operation)
        project = self._apply_factory_references(project, context)
        self._portfolio.register_for_company(company.company_id, project)
        request = ProvisioningRequest(
            request_id=f"PPE-{uuid4().hex[:12]}",
            project_id=project.project_id,
            company_id=company.company_id,
            status=ProvisioningStatus.PROVISIONED,
            operation=operation,
            execution_mode=ProvisioningExecutionMode.CONTROLLED,
            approved_by=spec.approved_by,
            steps=steps,
        )
        saved = self._repository.save(request)
        self._portfolio.change_status_for_company(
            company.company_id,
            project.project_id,
            ProjectStatus.ACTIVE,
        )
        self._audit(
            action=f"provisioning.{operation.value}_provisioned",
            entity_id=saved.request_id,
            detail=f"Enterprise project stack provisioned for {company.company_id}/{project.project_id}.",
        )
        return saved

    def _validate_spec(self, spec: ProjectProvisioningSpec) -> None:
        if spec.project.company_id != spec.company.company_id:
            raise ValueError("Project company_id must match provisioning company_id")

    def _context(self, spec: ProjectProvisioningSpec) -> ProjectProvisioningContext:
        company_id = spec.company.company_id
        project_id = spec.project.project_id
        blueprint = spec.factory_blueprint
        websig_slug = spec.websig_slug or blueprint.websig_slug or f"{company_id.lower()}-{project_id.lower()}"
        postgis_schema = blueprint.postgis_schema_name or self._safe_identifier(f"{company_id}_{project_id}")
        geoserver_workspace = blueprint.geoserver_workspace or self._safe_identifier(f"{company_id}_{project_id}").upper()
        return ProjectProvisioningContext(
            company_id=company_id,
            project_id=project_id,
            websig_slug=websig_slug,
            websig_url=blueprint.websig_url or f"websig://{company_id}/{websig_slug}",
            nas_root_uri=blueprint.nas_root_uri or f"nas://{company_id}/{project_id}/websig/root",
            postgis_schema_name=postgis_schema,
            geoserver_workspace=geoserver_workspace,
            dashboard_id=spec.dashboard_id or f"DASH-{company_id}-{project_id}",
            document_structure=spec.document_structure,
            catalogs=spec.catalogs,
            enabled_modules=blueprint.enabled_modules,
        )

    def _build_steps(
        self,
        spec: ProjectProvisioningSpec,
        context: ProjectProvisioningContext,
        dry_run: bool,
        operation: ProvisioningOperation = ProvisioningOperation.PROJECT_STACK,
    ) -> list[ProvisioningStep]:
        company_id = spec.company.company_id
        project_id = spec.project.project_id
        status = ProvisioningStepStatus.PLANNED if dry_run else ProvisioningStepStatus.SUCCEEDED
        steps = [
            self._step(
                "factory-blueprint",
                ProvisioningResourceType.FACTORY_BLUEPRINT,
                "Validar WEB SIG Factory Blueprint",
                spec.factory_blueprint.template_id,
                status,
            ),
            self._step(
                "governance-gate",
                ProvisioningResourceType.GOVERNANCE_GATE,
                f"Verificar aprobacion {operation.value}",
                "dry-run" if dry_run else f"approved-by:{spec.approved_by}",
                status,
            ),
            self._step("company", ProvisioningResourceType.COMPANY, "Create Empresa", company_id, status),
            self._step("project", ProvisioningResourceType.PROJECT, "Create Proyecto", project_id, status),
        ]
        steps.extend(adapter.plan(context) if dry_run else adapter.execute(context) for adapter in self._adapters)
        steps.extend(
            self._step(
                f"user-{user.user_id}",
                ProvisioningResourceType.USER,
                "Crear Usuario",
                user.user_id,
                status,
            )
            for user in spec.users
        )
        steps.extend(
            self._step(
                f"role-{membership.membership_id}",
                ProvisioningResourceType.ROLE,
                "Crear Roles",
                f"{membership.company_id}/{membership.user_id}/{membership.role.value}",
                status,
            )
            for membership in spec.memberships
        )
        return steps

    @staticmethod
    def _apply_factory_references(
        project: PortfolioProject,
        context: ProjectProvisioningContext,
    ) -> PortfolioProject:
        return project.model_copy(
            update={
                "websig_instance_id": f"WEB-{context.company_id}-{context.project_id}",
                "websig_url": context.websig_url,
                "nas_root_uri": context.nas_root_uri,
                "gis_binding_id": f"GBD-{context.company_id}-{context.project_id}",
                "lifecycle_stage": ProjectLifecycleStage.EXECUTION,
            }
        )

    @staticmethod
    def _safe_identifier(value: str) -> str:
        import re

        return re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_")

    @staticmethod
    def _step(
        step_id: str,
        resource_type: ProvisioningResourceType,
        name: str,
        reference: str,
        status: ProvisioningStepStatus,
    ) -> ProvisioningStep:
        return ProvisioningStep(
            step_id=step_id,
            resource_type=resource_type,
            name=name,
            status=status,
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
