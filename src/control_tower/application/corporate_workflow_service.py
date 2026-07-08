"""Corporate Workflow Engine application service.

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0017: Project Provisioning Engine.
- ADR-0025: Corporate Portfolio Domain.
- ADR-0027: Corporate Control Tower operational flow.
"""

from uuid import uuid4

from control_tower.application.enterprise_service import CompanyService
from control_tower.application.portfolio_service import PortfolioService
from control_tower.application.repositories import AuditEventRepository, CorporateWorkflowRepository
from control_tower.domain.audit import AuditEvent
from control_tower.domain.corporate_workflow import (
    CorporateWorkflowAdvance,
    CorporateWorkflowInstance,
    CorporateWorkflowRollback,
    CorporateWorkflowStage,
    CorporateWorkflowStatus,
    CorporateWorkflowTransition,
)
from control_tower.domain.corporate_workflow.models import OFFICIAL_WORKFLOW_SEQUENCE
from control_tower.domain.portfolio import PortfolioLifecycleTransition, ProjectLifecycleStage, ProjectStatus


class CorporateWorkflowEngine:
    """Orchestrates official corporate process transitions without operating WEB SIG."""

    def __init__(
        self,
        repository: CorporateWorkflowRepository,
        companies: CompanyService,
        portfolio: PortfolioService,
        audit: AuditEventRepository | None = None,
    ) -> None:
        self._repository = repository
        self._companies = companies
        self._portfolio = portfolio
        self._audit = audit

    def start_workflow(
        self,
        company_id: str,
        *,
        workflow_id: str | None = None,
        project_id: str | None = None,
        program_id: str | None = None,
        actor: str = "system",
        reason: str = "Corporate workflow started",
    ) -> CorporateWorkflowInstance:
        """Start the official corporate workflow for a company/project context."""

        self._require_company(company_id)
        if project_id is not None:
            self._require_company_project(company_id, project_id)
        workflow = CorporateWorkflowInstance(
            workflow_id=workflow_id or f"CWF-{uuid4().hex[:12]}",
            company_id=company_id,
            project_id=project_id,
            program_id=program_id,
            current_stage=CorporateWorkflowStage.CREATE_COMPANY,
            completed_stages=[CorporateWorkflowStage.CREATE_COMPANY],
            created_by=actor,
            updated_by=actor,
        )
        saved = self._repository.save_workflow(workflow)
        self._record_transition(
            workflow=saved,
            from_stage=None,
            to_stage=CorporateWorkflowStage.CREATE_COMPANY,
            actor=actor,
            reason=reason,
        )
        return saved

    def advance(
        self,
        company_id: str,
        workflow_id: str,
        payload: CorporateWorkflowAdvance,
    ) -> CorporateWorkflowInstance:
        """Advance one workflow to the next official stage."""

        workflow = self._get_company_workflow(company_id, workflow_id)
        expected = self._next_stage(workflow.current_stage)
        if payload.to_stage != expected:
            raise ValueError(f"Next allowed workflow stage is {expected.value}")
        completed = list(dict.fromkeys([*workflow.completed_stages, payload.to_stage]))
        status = (
            CorporateWorkflowStatus.COMPLETED
            if payload.to_stage == CorporateWorkflowStage.ARCHIVE
            else CorporateWorkflowStatus.ACTIVE
        )
        updated = workflow.model_copy(
            update={
                "current_stage": payload.to_stage,
                "completed_stages": completed,
                "status": status,
                "updated_by": payload.actor,
            }
        )
        saved = self._repository.save_workflow(updated)
        self._apply_portfolio_transition(saved)
        self._record_transition(
            workflow=saved,
            from_stage=workflow.current_stage,
            to_stage=payload.to_stage,
            actor=payload.actor,
            reason=payload.reason,
        )
        return saved

    def rollback(
        self,
        company_id: str,
        workflow_id: str,
        payload: CorporateWorkflowRollback,
    ) -> CorporateWorkflowInstance:
        """Rollback one workflow to the previous completed stage."""

        workflow = self._get_company_workflow(company_id, workflow_id)
        if not workflow.rollback_available or len(workflow.completed_stages) < 2:
            raise ValueError("Controlled rollback is not available for this workflow")
        previous_stage = workflow.completed_stages[-2]
        completed = workflow.completed_stages[:-1]
        updated = workflow.model_copy(
            update={
                "current_stage": previous_stage,
                "completed_stages": completed,
                "status": CorporateWorkflowStatus.ROLLED_BACK,
                "updated_by": payload.actor,
            }
        )
        saved = self._repository.save_workflow(updated)
        transitions = self._repository.list_transitions(workflow.workflow_id)
        rollback_of = transitions[-1].transition_id if transitions else None
        self._record_transition(
            workflow=saved,
            from_stage=workflow.current_stage,
            to_stage=previous_stage,
            actor=payload.actor,
            reason=payload.reason,
            rollback=True,
            rollback_of=rollback_of,
        )
        return saved

    def list_workflows(self, company_id: str) -> list[CorporateWorkflowInstance]:
        """Return workflows for one company."""

        self._require_company(company_id)
        return self._repository.list_workflows(company_id)

    def get_workflow(self, company_id: str, workflow_id: str) -> CorporateWorkflowInstance:
        """Return one workflow for one company."""

        return self._get_company_workflow(company_id, workflow_id)

    def list_transitions(self, company_id: str, workflow_id: str) -> list[CorporateWorkflowTransition]:
        """Return auditable transitions for one company-scoped workflow."""

        self._get_company_workflow(company_id, workflow_id)
        return self._repository.list_transitions(workflow_id)

    def _get_company_workflow(self, company_id: str, workflow_id: str) -> CorporateWorkflowInstance:
        self._require_company(company_id)
        workflow = self._repository.get_workflow(workflow_id)
        if workflow is None or workflow.company_id != company_id:
            raise ValueError(f"Workflow is not registered for company {company_id}: {workflow_id}")
        return workflow

    def _record_transition(
        self,
        *,
        workflow: CorporateWorkflowInstance,
        from_stage: CorporateWorkflowStage | None,
        to_stage: CorporateWorkflowStage,
        actor: str,
        reason: str,
        rollback: bool = False,
        rollback_of: str | None = None,
    ) -> CorporateWorkflowTransition:
        transition = CorporateWorkflowTransition(
            transition_id=f"CWFT-{uuid4().hex[:12]}",
            workflow_id=workflow.workflow_id,
            company_id=workflow.company_id,
            project_id=workflow.project_id,
            from_stage=from_stage,
            to_stage=to_stage,
            actor=actor,
            reason=reason,
            rollback=rollback,
            rollback_of=rollback_of,
        )
        saved = self._repository.save_transition(transition)
        self._audit_event(saved)
        return saved

    def _apply_portfolio_transition(self, workflow: CorporateWorkflowInstance) -> None:
        if workflow.project_id is None:
            return
        match workflow.current_stage:
            case CorporateWorkflowStage.ACTIVATE_PROJECT | CorporateWorkflowStage.OPERATION:
                self._portfolio.transition_lifecycle_for_company(
                    workflow.company_id,
                    workflow.project_id,
                    PortfolioLifecycleTransition(
                        lifecycle_stage=ProjectLifecycleStage.EXECUTION,
                        status=ProjectStatus.ACTIVE,
                    ),
                )
            case CorporateWorkflowStage.CLOSURE:
                self._portfolio.transition_lifecycle_for_company(
                    workflow.company_id,
                    workflow.project_id,
                    PortfolioLifecycleTransition(
                        lifecycle_stage=ProjectLifecycleStage.CLOSURE,
                        status=ProjectStatus.CLOSED,
                    ),
                )
            case CorporateWorkflowStage.ARCHIVE:
                self._portfolio.transition_lifecycle_for_company(
                    workflow.company_id,
                    workflow.project_id,
                    PortfolioLifecycleTransition(
                        lifecycle_stage=ProjectLifecycleStage.ARCHIVED,
                        status=ProjectStatus.SUSPENDED,
                    ),
                )
            case _:
                return

    @staticmethod
    def _next_stage(stage: CorporateWorkflowStage) -> CorporateWorkflowStage:
        index = OFFICIAL_WORKFLOW_SEQUENCE.index(stage)
        if index + 1 >= len(OFFICIAL_WORKFLOW_SEQUENCE):
            raise ValueError("Workflow is already at final stage")
        return OFFICIAL_WORKFLOW_SEQUENCE[index + 1]

    def _require_company(self, company_id: str) -> None:
        if not self._companies.exists(company_id):
            raise ValueError(f"Company is not registered: {company_id}")

    def _require_company_project(self, company_id: str, project_id: str) -> None:
        if self._portfolio.get_project_for_company(company_id, project_id) is None:
            raise ValueError(f"Project is not registered for company {company_id}: {project_id}")

    def _audit_event(self, transition: CorporateWorkflowTransition) -> None:
        if self._audit is None:
            return
        self._audit.save(
            AuditEvent(
                actor=transition.actor,
                action=(
                    "corporate_workflow.rollback"
                    if transition.rollback
                    else "corporate_workflow.transitioned"
                ),
                entity_type="corporate_workflow",
                entity_id=transition.workflow_id,
                detail=(
                    f"{transition.from_stage.value if transition.from_stage else 'start'} -> "
                    f"{transition.to_stage.value}: {transition.reason}"
                ),
            )
        )
