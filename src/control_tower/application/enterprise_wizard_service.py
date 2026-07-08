"""Enterprise Wizard application service.

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0025: Corporate Portfolio Domain.
- ADR-0029: Corporate Workflow Engine.
"""

from uuid import uuid4

from control_tower.application.corporate_workflow_service import CorporateWorkflowEngine
from control_tower.application.enterprise_service import CompanyService, UserService
from control_tower.application.portfolio_service import CorporatePortfolioDomainService
from control_tower.application.repositories import AuditEventRepository, EnterpriseWizardRepository
from control_tower.domain.audit import AuditEvent
from control_tower.domain.corporate_workflow import CorporateWorkflowAdvance, CorporateWorkflowStage
from control_tower.domain.enterprise import Company, CompanyMembership, User, UserRole
from control_tower.domain.enterprise_wizard import (
    ENTERPRISE_WIZARD_STEPS,
    EnterpriseWizardActivation,
    EnterpriseWizardSession,
    EnterpriseWizardStatus,
    EnterpriseWizardStep,
    EnterpriseWizardStepDefinition,
    EnterpriseWizardStepState,
    EnterpriseWizardStepStatus,
    EnterpriseWizardStepSubmission,
)
from control_tower.domain.portfolio import CorporateProgram, PortfolioProject


class EnterpriseWizardService:
    """Coordinates a resumable Enterprise Wizard without operating WEB SIG."""

    def __init__(
        self,
        repository: EnterpriseWizardRepository,
        companies: CompanyService,
        users: UserService,
        portfolio: CorporatePortfolioDomainService,
        workflow: CorporateWorkflowEngine,
        audit: AuditEventRepository | None = None,
    ) -> None:
        self._repository = repository
        self._companies = companies
        self._users = users
        self._portfolio = portfolio
        self._workflow = workflow
        self._audit = audit
        self._definitions = {definition.step: definition for definition in ENTERPRISE_WIZARD_STEPS}

    def start(self, *, wizard_id: str | None = None, actor: str = "system") -> EnterpriseWizardSession:
        """Start a resumable wizard session."""

        session = EnterpriseWizardSession(
            wizard_id=wizard_id or f"WIZ-{uuid4().hex[:12]}",
            steps=[
                EnterpriseWizardStepState(step=definition.step)
                for definition in ENTERPRISE_WIZARD_STEPS
            ],
            created_by=actor,
            updated_by=actor,
        )
        saved = self._repository.save(session)
        self._audit_event(actor, "enterprise_wizard.started", saved.wizard_id)
        return saved

    def list_sessions(self) -> list[EnterpriseWizardSession]:
        """Return wizard sessions."""

        return self._repository.list()

    def get(self, wizard_id: str) -> EnterpriseWizardSession:
        """Return one wizard session for resume."""

        session = self._repository.get(wizard_id)
        if session is None:
            raise ValueError(f"Enterprise Wizard session is not registered: {wizard_id}")
        return session

    def save_step(
        self,
        wizard_id: str,
        step: EnterpriseWizardStep,
        submission: EnterpriseWizardStepSubmission,
    ) -> EnterpriseWizardSession:
        """Save and validate one wizard step independently."""

        session = self.get(wizard_id)
        step_state = self.validate_step(step, submission.data)
        updated_steps = [
            step_state if existing.step == step else existing
            for existing in session.steps
        ]
        status = self._session_status(updated_steps)
        updated = session.model_copy(
            update={
                "company_id": self._company_id(updated_steps),
                "project_id": self._project_id(updated_steps),
                "status": status,
                "current_step": self._current_step(updated_steps),
                "steps": updated_steps,
                "updated_by": submission.actor,
            }
        )
        saved = self._repository.save(updated)
        self._audit_event(submission.actor, "enterprise_wizard.step_saved", saved.wizard_id, step.value)
        return saved

    def validate_step(
        self,
        step: EnterpriseWizardStep,
        data: dict[str, object],
    ) -> EnterpriseWizardStepState:
        """Validate one step without requiring other steps to be complete."""

        definition = self._definitions[step]
        errors = self._validate_required_fields(definition, data)
        status = (
            EnterpriseWizardStepStatus.VALID
            if not errors
            else EnterpriseWizardStepStatus.INVALID
        )
        if data == {}:
            status = EnterpriseWizardStepStatus.DRAFT
        return EnterpriseWizardStepState(
            step=step,
            status=status,
            data=data,
            validation_errors=errors,
        )

    def activate(
        self,
        wizard_id: str,
        payload: EnterpriseWizardActivation,
    ) -> EnterpriseWizardSession:
        """Activate a ready wizard by creating governed corporate records."""

        session = self.get(wizard_id)
        if session.status != EnterpriseWizardStatus.READY:
            raise ValueError("Enterprise Wizard must be ready before activation")
        data = {state.step: state.data for state in session.steps}
        company_data = data[EnterpriseWizardStep.COMPANY]
        program_data = data[EnterpriseWizardStep.PROGRAM]
        project_data = data[EnterpriseWizardStep.PROJECT]
        websig_data = data[EnterpriseWizardStep.WEB_SIG]
        gis_data = data[EnterpriseWizardStep.GIS]
        nas_data = data[EnterpriseWizardStep.NAS]
        location_data = data[EnterpriseWizardStep.LOCATION]

        company = self._companies.register(
            Company(
                company_id=str(company_data["company_id"]),
                legal_name=str(company_data["legal_name"]),
                display_name=str(company_data["display_name"]),
            )
        )
        program = self._portfolio.register_program(
            CorporateProgram(
                program_id=str(program_data["program_id"]),
                company_id=company.company_id,
                name=str(program_data["name"]),
                customer_id=program_data.get("customer_id"),
            )
        )
        project = self._portfolio.register_project(
            PortfolioProject(
                project_id=str(project_data["project_id"]),
                company_id=company.company_id,
                program_id=program.program_id,
                name=str(project_data["name"]),
                cui=project_data.get("cui"),
                websig_instance_id=websig_data.get("websig_instance_id"),
                websig_url=websig_data.get("websig_url"),
                nas_root_uri=str(nas_data["nas_root_uri"]),
                gis_binding_id=gis_data.get("gis_binding_id"),
                google_drive_folder_id=nas_data.get("google_drive_folder_id"),
            )
        )
        self._register_users_and_memberships(data[EnterpriseWizardStep.USERS], company.company_id)
        workflow = self._workflow.start_workflow(
            company.company_id,
            workflow_id=f"CWF-{wizard_id}",
            project_id=project.project_id,
            program_id=program.program_id,
            actor=payload.actor,
            reason=payload.reason,
        )
        workflow = self._advance_workflow_to_activation(company.company_id, workflow.workflow_id, payload)
        updated = session.model_copy(
            update={
                "company_id": company.company_id,
                "project_id": project.project_id,
                "workflow_id": workflow.workflow_id,
                "status": EnterpriseWizardStatus.ACTIVATED,
                "updated_by": payload.actor,
            }
        )
        saved = self._repository.save(updated)
        self._audit_event(
            payload.actor,
            "enterprise_wizard.activated",
            saved.wizard_id,
            f"{company.company_id}:{project.project_id}:{location_data.get('region')}",
        )
        return saved

    def _register_users_and_memberships(self, users_data: dict[str, object], company_id: str) -> None:
        users = users_data.get("users", [])
        if not isinstance(users, list):
            return
        for index, user_data in enumerate(users, start=1):
            if not isinstance(user_data, dict):
                continue
            user_id = str(user_data.get("user_id") or f"USR-WIZ-{index:03d}")
            self._users.register_user(
                User(
                    user_id=user_id,
                    email=str(user_data["email"]),
                    display_name=str(user_data.get("display_name") or user_data["email"]),
                )
            )
            role_value = str(user_data.get("role") or UserRole.PROJECT_OPERATOR.value)
            self._users.add_membership(
                CompanyMembership(
                    membership_id=str(user_data.get("membership_id") or f"MEM-{company_id}-{user_id}"),
                    company_id=company_id,
                    user_id=user_id,
                    role=UserRole(role_value),
                )
            )

    def _advance_workflow_to_activation(
        self,
        company_id: str,
        workflow_id: str,
        payload: EnterpriseWizardActivation,
    ) -> object:
        workflow = None
        for stage in [
            CorporateWorkflowStage.CREATE_PROGRAM,
            CorporateWorkflowStage.CREATE_PROJECT,
            CorporateWorkflowStage.PROVISION_WEB_SIG,
            CorporateWorkflowStage.CREATE_NAS,
            CorporateWorkflowStage.CREATE_POSTGIS,
            CorporateWorkflowStage.REGISTER_GEOSERVER,
            CorporateWorkflowStage.CREATE_DASHBOARD,
            CorporateWorkflowStage.ASSIGN_USERS,
            CorporateWorkflowStage.ASSIGN_SPECIALTIES,
            CorporateWorkflowStage.ACTIVATE_PROJECT,
        ]:
            workflow = self._workflow.advance(
                company_id,
                workflow_id,
                CorporateWorkflowAdvance(
                    to_stage=stage,
                    actor=payload.actor,
                    reason=f"Enterprise Wizard activation: {stage.value}",
                ),
            )
        return workflow

    @staticmethod
    def _validate_required_fields(
        definition: EnterpriseWizardStepDefinition,
        data: dict[str, object],
    ) -> list[str]:
        errors: list[str] = []
        for field_name in definition.required_fields:
            value = data.get(field_name)
            if value is None or value == "" or value == []:
                errors.append(f"{field_name} is required")
        if "users" in definition.required_fields and isinstance(data.get("users"), list):
            for index, user in enumerate(data["users"], start=1):
                if not isinstance(user, dict) or not user.get("email"):
                    errors.append(f"users[{index}].email is required")
        return errors

    @staticmethod
    def _session_status(steps: list[EnterpriseWizardStepState]) -> EnterpriseWizardStatus:
        if all(step.status == EnterpriseWizardStepStatus.VALID for step in steps):
            return EnterpriseWizardStatus.READY
        return EnterpriseWizardStatus.DRAFT

    @staticmethod
    def _current_step(steps: list[EnterpriseWizardStepState]) -> EnterpriseWizardStep:
        for step in steps:
            if step.status != EnterpriseWizardStepStatus.VALID:
                return step.step
        return EnterpriseWizardStep.ACTIVATION

    @staticmethod
    def _company_id(steps: list[EnterpriseWizardStepState]) -> str | None:
        for step in steps:
            if step.step == EnterpriseWizardStep.COMPANY:
                value = step.data.get("company_id")
                return str(value) if value else None
        return None

    @staticmethod
    def _project_id(steps: list[EnterpriseWizardStepState]) -> str | None:
        for step in steps:
            if step.step == EnterpriseWizardStep.PROJECT:
                value = step.data.get("project_id")
                return str(value) if value else None
        return None

    def _audit_event(self, actor: str, action: str, entity_id: str, detail: str | None = None) -> None:
        if self._audit is None:
            return
        self._audit.save(
            AuditEvent(
                actor=actor,
                action=action,
                entity_type="enterprise_wizard",
                entity_id=entity_id,
                detail=detail,
            )
        )
