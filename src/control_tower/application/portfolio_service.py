"""Portfolio application service.

ADR references:
- ADR-0001: REV11 architecture baseline.
- ADR-0002: Layered modular API scaffold.
- ADR-0005: Persistence strategy.
- ADR-0009: GeoServer integration.
- ADR-0010: Google Workspace transition integration.
- ADR-0014: Enterprise multitenancy.
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0024: REV13 corporate governance baseline.
"""

from control_tower.domain.audit import AuditEvent
from control_tower.domain.portfolio import (
    CorporateCustomer,
    CorporatePortfolioProjectView,
    CorporateProgram,
    PortfolioLifecycleTransition,
    PortfolioProject,
    ProjectIntegrationSummary,
    ProjectLifecycleStage,
    ProjectStatus,
)

from .repositories import (
    AuditEventRepository,
    CorporateCustomerRepository,
    CorporateGisRepository,
    CorporateProgramRepository,
    InformationAssetRepository,
    PortfolioProjectRepository,
    ProvisioningRequestRepository,
)


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

    def register_for_company(self, company_id: str, project: PortfolioProject) -> PortfolioProject:
        """Register a project inside a company tenant."""

        if project.company_id != company_id:
            raise ValueError("Project company_id must match tenant company_id")
        return self.register(project)

    def list_projects(self) -> list[PortfolioProject]:
        """Return all registered portfolio projects."""

        return self._repository.list()

    def list_projects_for_company(self, company_id: str) -> list[PortfolioProject]:
        """Return projects for one company."""

        return self._repository.list_by_company(company_id)

    def exists(self, project_id: str) -> bool:
        """Return whether a project is registered in the portfolio."""

        return self._repository.exists(project_id)

    def get_project(self, project_id: str) -> PortfolioProject | None:
        """Return a project by identifier when it exists."""

        return self._repository.get(project_id)

    def get_project_for_company(
        self,
        company_id: str,
        project_id: str,
    ) -> PortfolioProject | None:
        """Return a project by identifier inside one company."""

        return self._repository.get_by_company(company_id, project_id)

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

    def transition_lifecycle(
        self,
        project_id: str,
        transition: PortfolioLifecycleTransition,
    ) -> PortfolioProject:
        """Move a project through the corporate lifecycle."""

        project = self._repository.get(project_id)
        if project is None:
            raise ValueError(f"Project is not registered: {project_id}")
        return self._save_lifecycle_transition(project, transition)

    def transition_lifecycle_for_company(
        self,
        company_id: str,
        project_id: str,
        transition: PortfolioLifecycleTransition,
    ) -> PortfolioProject:
        """Move a company-scoped project through the corporate lifecycle."""

        project = self._repository.get_by_company(company_id, project_id)
        if project is None:
            raise ValueError(f"Project is not registered for company {company_id}: {project_id}")
        return self._save_lifecycle_transition(project, transition)

    def change_status_for_company(
        self,
        company_id: str,
        project_id: str,
        status: ProjectStatus,
    ) -> PortfolioProject:
        """Change governance status for a project inside one company."""

        project = self._repository.get_by_company(company_id, project_id)
        if project is None:
            raise ValueError(f"Project is not registered for company {company_id}: {project_id}")
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

    def summary_for_company(self, company_id: str) -> dict[str, int]:
        """Return portfolio counts by governance status for one company."""

        projects = self.list_projects_for_company(company_id)
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

    def _save_lifecycle_transition(
        self,
        project: PortfolioProject,
        transition: PortfolioLifecycleTransition,
    ) -> PortfolioProject:
        status = transition.status or _status_for_lifecycle(transition.lifecycle_stage)
        updated = project.model_copy(
            update={
                "lifecycle_stage": transition.lifecycle_stage,
                "status": status,
            }
        )
        saved = self._repository.save(updated)
        self._audit(
            action="project.lifecycle_transitioned",
            entity_id=saved.project_id,
            detail=(
                "Project lifecycle changed to "
                f"{saved.lifecycle_stage.value} with status {saved.status.value}."
            ),
        )
        return saved


class CorporatePortfolioDomainService:
    """Coordinates the complete corporate portfolio governance domain."""

    def __init__(
        self,
        customer_repository: CorporateCustomerRepository,
        program_repository: CorporateProgramRepository,
        portfolio: PortfolioService,
        provisioning_repository: ProvisioningRequestRepository,
        information_repository: InformationAssetRepository,
        gis_repository: CorporateGisRepository,
        audit_repository: AuditEventRepository | None = None,
    ) -> None:
        self._customers = customer_repository
        self._programs = program_repository
        self._portfolio = portfolio
        self._provisioning = provisioning_repository
        self._information = information_repository
        self._gis = gis_repository
        self._audit = audit_repository

    def register_customer(self, customer: CorporateCustomer) -> CorporateCustomer:
        """Register a customer under a company portfolio."""

        saved = self._customers.save(customer)
        self._audit_event("portfolio.customer_registered", "customer", saved.customer_id)
        return saved

    def list_customers(self, company_id: str) -> list[CorporateCustomer]:
        """List customers for one company."""

        return self._customers.list_by_company(company_id)

    def register_program(self, program: CorporateProgram) -> CorporateProgram:
        """Register a program and validate its customer relationship."""

        if program.customer_id is not None:
            customer = self._customers.get(program.customer_id)
            if customer is None or customer.company_id != program.company_id:
                raise ValueError(f"Customer is not registered for company {program.company_id}")
        saved = self._programs.save(program)
        self._audit_event("portfolio.program_registered", "program", saved.program_id)
        return saved

    def list_programs(self, company_id: str) -> list[CorporateProgram]:
        """List programs for one company."""

        return self._programs.list_by_company(company_id)

    def register_project(self, project: PortfolioProject) -> PortfolioProject:
        """Register a project with validated customer and program links."""

        self._validate_project_relationships(project)
        saved = self._portfolio.register(project)
        self._audit_event("portfolio.project_governed", "project", saved.project_id)
        return saved

    def register_project_for_company(
        self,
        company_id: str,
        project: PortfolioProject,
    ) -> PortfolioProject:
        """Register a project under one company with corporate relationships."""

        if project.company_id != company_id:
            raise ValueError("Project company_id must match tenant company_id")
        return self.register_project(project)

    def project_view(self, company_id: str, project_id: str) -> CorporatePortfolioProjectView:
        """Return the integrated corporate governance view for one project."""

        project = self._portfolio.get_project_for_company(company_id, project_id)
        if project is None:
            raise ValueError(f"Project is not registered for company {company_id}: {project_id}")
        customer = self._customers.get(project.customer_id) if project.customer_id is not None else None
        program = self._programs.get(project.program_id) if project.program_id is not None else None
        assets = [
            asset
            for asset in self._information.list_assets_by_company(company_id)
            if asset.project_id == project_id
        ]
        provisioning_requests = [
            request
            for request in self._provisioning.list_by_company(company_id)
            if request.project_id == project_id
        ]
        gis_binding = self._gis.get_binding(company_id, project_id)
        layers = self._gis.list_layers(company_id, project_id)
        return CorporatePortfolioProjectView(
            project=project,
            customer=customer,
            program=program,
            integrations=ProjectIntegrationSummary(
                websig_instance_id=project.websig_instance_id,
                websig_url=project.websig_url,
                nas_root_uri=project.nas_root_uri,
                gis_binding_id=gis_binding.binding_id if gis_binding is not None else project.gis_binding_id,
                google_drive_folder_id=project.google_drive_folder_id,
                provisioning_requests=len(provisioning_requests),
                nas_assets=len(assets),
                gis_layers=len(layers),
            ),
        )

    def _validate_project_relationships(self, project: PortfolioProject) -> None:
        if project.customer_id is not None:
            customer = self._customers.get(project.customer_id)
            if customer is None or customer.company_id != project.company_id:
                raise ValueError(f"Customer is not registered for company {project.company_id}")
        if project.program_id is not None:
            program = self._programs.get(project.program_id)
            if program is None or program.company_id != project.company_id:
                raise ValueError(f"Program is not registered for company {project.company_id}")
            if project.customer_id is not None and program.customer_id not in (None, project.customer_id):
                raise ValueError("Project customer_id must match the program customer_id")

    def _audit_event(self, action: str, entity_type: str, entity_id: str) -> None:
        if self._audit is None:
            return
        self._audit.save(
            AuditEvent(
                actor="system",
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                detail=f"{entity_type} {entity_id} governed by Corporate Portfolio Domain.",
            )
        )


def _status_for_lifecycle(stage: ProjectLifecycleStage) -> ProjectStatus:
    match stage:
        case ProjectLifecycleStage.INTAKE | ProjectLifecycleStage.PLANNING:
            return ProjectStatus.REGISTERED
        case ProjectLifecycleStage.PROVISIONING:
            return ProjectStatus.PROVISIONING_REQUESTED
        case ProjectLifecycleStage.EXECUTION:
            return ProjectStatus.ACTIVE
        case ProjectLifecycleStage.CLOSURE:
            return ProjectStatus.CLOSED
        case ProjectLifecycleStage.ARCHIVED:
            return ProjectStatus.SUSPENDED
