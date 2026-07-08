"""Corporate Control Tower operational flow service.

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0025: Corporate Portfolio Domain.
- ADR-0026: WEB SIG Factory controlled provisioning.
- ADR-0027: Corporate Control Tower operational flow.
"""

from control_tower.domain.operations import (
    CompanyOperationalFlow,
    OperationalFlowItem,
    OperationalFlowSummary,
    OperationalPhase,
    OperationalState,
)
from control_tower.domain.portfolio import ProjectLifecycleStage

from .enterprise_service import CompanyService
from .portfolio_service import CorporatePortfolioDomainService, PortfolioService
from .repositories import ProvisioningRequestRepository


class OperationalFlowService:
    """Builds governed operational flow read models for one company."""

    def __init__(
        self,
        companies: CompanyService,
        portfolio: PortfolioService,
        corporate_portfolio: CorporatePortfolioDomainService,
        provisioning_repository: ProvisioningRequestRepository,
    ) -> None:
        self._companies = companies
        self._portfolio = portfolio
        self._corporate_portfolio = corporate_portfolio
        self._provisioning = provisioning_repository

    def company_flow(self, company_id: str) -> CompanyOperationalFlow:
        """Return operational flow status for all projects in one company."""

        if not self._companies.exists(company_id):
            raise ValueError(f"Company is not registered: {company_id}")

        requests = self._provisioning.list_by_company(company_id)
        items: list[OperationalFlowItem] = []
        for project in self._portfolio.list_projects_for_company(company_id):
            project_requests = [
                request for request in requests if request.project_id == project.project_id
            ]
            view = self._corporate_portfolio.project_view(company_id, project.project_id)
            latest_approver = next(
                (
                    request.approved_by
                    for request in reversed(project_requests)
                    if request.approved_by is not None
                ),
                None,
            )
            items.append(
                self._project_item(
                    company_id=company_id,
                    project_id=project.project_id,
                    project_name=project.name,
                    lifecycle_stage=project.lifecycle_stage,
                    websig_registered=bool(
                        view.integrations.websig_instance_id or view.integrations.websig_url
                    ),
                    nas_registered=bool(view.integrations.nas_root_uri)
                    or view.integrations.nas_assets > 0,
                    gis_registered=bool(view.integrations.gis_binding_id)
                    or view.integrations.gis_layers > 0,
                    provisioning_requests=len(project_requests),
                    approved_by=latest_approver,
                )
            )

        return CompanyOperationalFlow(
            company_id=company_id,
            summary=self._summary(items),
            items=items,
        )

    def _project_item(
        self,
        company_id: str,
        project_id: str,
        project_name: str,
        lifecycle_stage: ProjectLifecycleStage,
        websig_registered: bool,
        nas_registered: bool,
        gis_registered: bool,
        provisioning_requests: int,
        approved_by: str | None,
    ) -> OperationalFlowItem:
        completed = [OperationalPhase.INTAKE]
        pending: list[str] = []

        if lifecycle_stage != ProjectLifecycleStage.INTAKE:
            completed.append(OperationalPhase.GOVERNANCE_QUALIFICATION)
            completed.append(OperationalPhase.PORTFOLIO_LIFECYCLE)
        else:
            pending.append("Definir lifecycle corporativo")

        if provisioning_requests > 0:
            completed.append(OperationalPhase.FACTORY_DRY_RUN)
        else:
            pending.append("Ejecutar dry-run WEB SIG Factory")

        if approved_by is not None:
            completed.append(OperationalPhase.APPROVAL_GATE)
        else:
            pending.append("Registrar approved_by")

        if websig_registered and nas_registered and gis_registered:
            completed.append(OperationalPhase.CONTROLLED_EXECUTION)
            completed.append(OperationalPhase.REFERENCE_REGISTRATION)
            completed.append(OperationalPhase.DASHBOARD_PUBLICATION)
        else:
            self._append_missing_references(
                pending,
                websig_registered=websig_registered,
                nas_registered=nas_registered,
                gis_registered=gis_registered,
            )

        if provisioning_requests > 0 and websig_registered:
            completed.append(OperationalPhase.AUDIT_MONITORING)

        state = self._state_for(
            lifecycle_stage=lifecycle_stage,
            provisioning_requests=provisioning_requests,
            approved_by=approved_by,
            websig_registered=websig_registered,
            nas_registered=nas_registered,
            gis_registered=gis_registered,
        )
        active_phase = self._active_phase(completed)
        readiness = round((len(completed) / len(OperationalPhase)) * 100)

        return OperationalFlowItem(
            project_id=project_id,
            project_name=project_name,
            company_id=company_id,
            current_state=state,
            active_phase=active_phase,
            completed_phases=completed,
            pending_controls=pending,
            next_action=self._next_action(state, pending),
            readiness_score=readiness,
            websig_registered=websig_registered,
            nas_registered=nas_registered,
            gis_registered=gis_registered,
            provisioning_requests=provisioning_requests,
            approved_by=approved_by,
        )

    @staticmethod
    def _append_missing_references(
        pending: list[str],
        *,
        websig_registered: bool,
        nas_registered: bool,
        gis_registered: bool,
    ) -> None:
        if not websig_registered:
            pending.append("Registrar referencia WEB SIG")
        if not nas_registered:
            pending.append("Registrar logical NAS URI")
        if not gis_registered:
            pending.append("Registrar binding GIS/PostGIS/GeoServer")

    @staticmethod
    def _state_for(
        *,
        lifecycle_stage: ProjectLifecycleStage,
        provisioning_requests: int,
        approved_by: str | None,
        websig_registered: bool,
        nas_registered: bool,
        gis_registered: bool,
    ) -> OperationalState:
        if lifecycle_stage in {ProjectLifecycleStage.CLOSURE, ProjectLifecycleStage.ARCHIVED}:
            return OperationalState.ARCHIVED
        if websig_registered and nas_registered and gis_registered:
            return OperationalState.OBSERVED
        if approved_by is not None:
            return OperationalState.APPROVED
        if provisioning_requests > 0:
            return OperationalState.PLANNED
        if lifecycle_stage != ProjectLifecycleStage.INTAKE:
            return OperationalState.QUALIFIED
        return OperationalState.INTAKE

    @staticmethod
    def _active_phase(completed: list[OperationalPhase]) -> OperationalPhase:
        for phase in OperationalPhase:
            if phase not in completed:
                return phase
        return OperationalPhase.CONTINUITY_BACKUP

    @staticmethod
    def _next_action(state: OperationalState, pending: list[str]) -> str:
        if state == OperationalState.OBSERVED:
            return "Mantener monitoreo, release y respaldo USB"
        if state == OperationalState.ARCHIVED:
            return "Preservar auditoria y metadatos historicos"
        if pending:
            return pending[0]
        return "Continuar siguiente puerta de gobierno"

    @staticmethod
    def _summary(items: list[OperationalFlowItem]) -> OperationalFlowSummary:
        total = len(items)
        average = 0 if total == 0 else round(sum(item.readiness_score for item in items) / total)
        return OperationalFlowSummary(
            total_projects=total,
            intake=sum(1 for item in items if item.current_state == OperationalState.INTAKE),
            qualified=sum(1 for item in items if item.current_state == OperationalState.QUALIFIED),
            planned=sum(1 for item in items if item.current_state == OperationalState.PLANNED),
            approved=sum(1 for item in items if item.current_state == OperationalState.APPROVED),
            provisioned=sum(1 for item in items if item.current_state == OperationalState.PROVISIONED),
            observed=sum(1 for item in items if item.current_state == OperationalState.OBSERVED),
            archived=sum(1 for item in items if item.current_state == OperationalState.ARCHIVED),
            average_readiness=average,
        )
