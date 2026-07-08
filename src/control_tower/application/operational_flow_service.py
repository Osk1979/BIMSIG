"""Corporate Control Tower operational flow service.

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0025: Corporate Portfolio Domain.
- ADR-0026: WEB SIG Factory controlled provisioning.
- ADR-0027: Corporate Control Tower operational flow.
"""

from control_tower.domain.operations import (
    CompanyOperationalFlow,
    CorporateOperatingModel,
    OperatingCapability,
    OperatingLane,
    OperationalFlowItem,
    OperationalFlowSummary,
    OperationalPhase,
    OperationalState,
)
from control_tower.domain.portfolio import ProjectLifecycleStage

from .enterprise_service import CompanyService
from .portfolio_service import CorporatePortfolioDomainService, PortfolioService
from .repositories import (
    AuditEventRepository,
    CorporateGisRepository,
    CorporateWorkflowRepository,
    EnterpriseWizardRepository,
    InformationAssetRepository,
    ProvisioningRequestRepository,
)


class OperationalFlowService:
    """Builds governed operational flow read models for one company."""

    def __init__(
        self,
        companies: CompanyService,
        portfolio: PortfolioService,
        corporate_portfolio: CorporatePortfolioDomainService,
        provisioning_repository: ProvisioningRequestRepository,
        workflow_repository: CorporateWorkflowRepository | None = None,
        wizard_repository: EnterpriseWizardRepository | None = None,
        information_repository: InformationAssetRepository | None = None,
        gis_repository: CorporateGisRepository | None = None,
        audit_repository: AuditEventRepository | None = None,
    ) -> None:
        self._companies = companies
        self._portfolio = portfolio
        self._corporate_portfolio = corporate_portfolio
        self._provisioning = provisioning_repository
        self._workflows = workflow_repository
        self._wizards = wizard_repository
        self._information = information_repository
        self._gis = gis_repository
        self._audit = audit_repository

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

    def company_operating_model(self, company_id: str) -> CorporateOperatingModel:
        """Return the Fase 3 operating model backed by existing domains."""

        flow = self.company_flow(company_id)
        workflows = self._workflows.list_workflows(company_id) if self._workflows else []
        wizards = self._company_wizards(company_id)
        assets = self._information.list_assets_by_company(company_id) if self._information else []
        gis_layers = self._gis.list_layers(company_id) if self._gis else []
        audits = self._audit.list(limit=100) if self._audit else []
        requests = self._provisioning.list_by_company(company_id)

        capabilities = [
            self._capability(
                "enterprise-wizard",
                "Enterprise Wizard",
                len(wizards),
                "sesiones registradas",
                "Continuar sesiones draft o activar sesiones ready",
            ),
            self._capability(
                "workflow-engine",
                "Corporate Workflow Engine",
                len(workflows),
                "workflows corporativos",
                "Avanzar transiciones pendientes con rollback disponible",
            ),
            self._capability(
                "portfolio-governance",
                "Gobierno de Portafolio",
                flow.summary.total_projects,
                "proyectos gobernados",
                "Completar lifecycle, cliente, programa e integraciones",
            ),
            self._capability(
                "websig-factory",
                "WEB SIG Factory",
                len(requests),
                "solicitudes de provisioning",
                "Ejecutar dry-run, aprobar y registrar referencias WEB SIG",
            ),
            self._capability(
                "corporate-information-center",
                "NAS Corporate Information Center",
                len(assets),
                "activos documentales",
                "Registrar metadatos y logical NAS URI por proyecto",
            ),
            self._capability(
                "corporate-gis",
                "GIS Corporativo",
                len(gis_layers),
                "capas GeoServer registradas",
                "Vincular PostGIS schema, workspace y layers",
            ),
            self._capability(
                "audit-continuity",
                "Auditoria y Continuidad",
                len(audits),
                "eventos recientes",
                "Mantener cierre GitHub y respaldo fisico diario",
            ),
        ]
        lanes = self._lanes(flow, workflows=len(workflows), wizards=len(wizards), audits=len(audits))
        return CorporateOperatingModel(
            company_id=company_id,
            flow=flow,
            lanes=lanes,
            capabilities=capabilities,
            priority_actions=self._priority_actions(flow, lanes),
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

    def _company_wizards(self, company_id: str):
        if self._wizards is None:
            return []
        sessions = self._wizards.list()
        return [
            session
            for session in sessions
            if session.company_id == company_id
            or any(
                step.data.get("company_id") == company_id
                for step in session.steps
                if isinstance(step.data, dict)
            )
        ]

    @staticmethod
    def _capability(
        capability_id: str,
        name: str,
        count: int,
        evidence_label: str,
        next_action: str,
    ) -> OperatingCapability:
        status = "operational" if count > 0 else "watch"
        return OperatingCapability(
            capability_id=capability_id,
            name=name,
            status=status,
            evidence=f"{count} {evidence_label}",
            next_action=next_action,
        )

    @staticmethod
    def _lanes(
        flow: CompanyOperationalFlow,
        *,
        workflows: int,
        wizards: int,
        audits: int,
    ) -> list[OperatingLane]:
        total = max(flow.summary.total_projects, 1)
        blocked = sum(1 for item in flow.items if item.pending_controls)
        return [
            OperatingLane(
                lane_id="intake",
                name="Intake corporativo",
                owner="PMO corporativa",
                readiness_score=100 if wizards else 40,
                capabilities=["enterprise-wizard", "portfolio-governance"],
                active_items=wizards,
                blocked_items=0 if wizards else 1,
                next_action="Completar Wizard para nuevos proyectos",
            ),
            OperatingLane(
                lane_id="provisioning",
                name="Provisioning controlado",
                owner="WEB SIG Factory",
                readiness_score=round((flow.summary.observed / total) * 100),
                capabilities=["websig-factory", "workflow-engine"],
                active_items=workflows,
                blocked_items=blocked,
                next_action="Cerrar referencias WEB SIG, NAS y GIS pendientes",
            ),
            OperatingLane(
                lane_id="governance",
                name="Gobierno ejecutivo",
                owner="Control Tower",
                readiness_score=flow.summary.average_readiness,
                capabilities=["portfolio-governance", "audit-continuity"],
                active_items=flow.summary.total_projects,
                blocked_items=blocked,
                next_action="Resolver controles pendientes de mayor impacto",
            ),
            OperatingLane(
                lane_id="intelligence",
                name="Inteligencia corporativa",
                owner="GIS Intelligence",
                readiness_score=flow.summary.average_readiness,
                capabilities=["corporate-gis", "corporate-information-center"],
                active_items=flow.summary.observed,
                blocked_items=max(0, flow.summary.total_projects - flow.summary.observed),
                next_action="Publicar capas, metadatos y KPIs espaciales",
            ),
            OperatingLane(
                lane_id="continuity",
                name="Continuidad y auditoria",
                owner="DevSecOps",
                readiness_score=100 if audits else 50,
                capabilities=["audit-continuity"],
                active_items=audits,
                blocked_items=0 if audits else 1,
                next_action="Confirmar push remoto y respaldo fisico",
            ),
        ]

    @staticmethod
    def _priority_actions(flow: CompanyOperationalFlow, lanes: list[OperatingLane]) -> list[str]:
        actions = []
        for item in flow.items:
            if item.pending_controls:
                actions.append(f"{item.project_id}: {item.pending_controls[0]}")
        for lane in lanes:
            if lane.blocked_items:
                actions.append(f"{lane.name}: {lane.next_action}")
        return actions[:6] or ["Mantener monitoreo operativo, auditoria y respaldo fisico"]
