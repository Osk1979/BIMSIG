from control_tower.application.corporate_workflow_service import CorporateWorkflowEngine
from control_tower.application.enterprise_service import CompanyService, UserService
from control_tower.application.enterprise_wizard_service import EnterpriseWizardService
from control_tower.application.portfolio_service import CorporatePortfolioDomainService, PortfolioService
from control_tower.domain.enterprise_wizard import (
    EnterpriseWizardActivation,
    EnterpriseWizardStep,
    EnterpriseWizardStepStatus,
    EnterpriseWizardStepSubmission,
)
from tests.unit.fakes import (
    FakeAuditEventRepository,
    FakeCompanyRepository,
    FakeCorporateCustomerRepository,
    FakeCorporateGisRepository,
    FakeCorporateProgramRepository,
    FakeCorporateWorkflowRepository,
    FakeEnterpriseWizardRepository,
    FakeInformationAssetRepository,
    FakeMembershipRepository,
    FakePortfolioProjectRepository,
    FakeProvisioningRequestRepository,
    FakeUserRepository,
)


def build_wizard_service() -> tuple[
    EnterpriseWizardService,
    FakePortfolioProjectRepository,
    FakeCorporateWorkflowRepository,
    FakeAuditEventRepository,
]:
    audit = FakeAuditEventRepository()
    company_repository = FakeCompanyRepository()
    project_repository = FakePortfolioProjectRepository()
    workflow_repository = FakeCorporateWorkflowRepository()
    companies = CompanyService(company_repository, audit)
    users = UserService(FakeUserRepository(), FakeMembershipRepository(), companies, audit)
    portfolio = PortfolioService(project_repository, audit)
    corporate_portfolio = CorporatePortfolioDomainService(
        FakeCorporateCustomerRepository(),
        FakeCorporateProgramRepository(),
        portfolio,
        FakeProvisioningRequestRepository(),
        FakeInformationAssetRepository(),
        FakeCorporateGisRepository(),
        audit,
    )
    workflow = CorporateWorkflowEngine(workflow_repository, companies, portfolio, audit)
    service = EnterpriseWizardService(
        FakeEnterpriseWizardRepository(),
        companies,
        users,
        corporate_portfolio,
        workflow,
        audit,
    )
    return service, project_repository, workflow_repository, audit


def complete_wizard(service: EnterpriseWizardService, wizard_id: str) -> None:
    payloads = {
        EnterpriseWizardStep.COMPANY: {
            "company_id": "CRTG-WIZ",
            "legal_name": "CRTG Wizard S.A.C.",
            "display_name": "CRTG Wizard",
        },
        EnterpriseWizardStep.PROGRAM: {"program_id": "PRG-WIZ", "name": "Programa Wizard"},
        EnterpriseWizardStep.PROJECT: {"project_id": "PSZ-WIZ", "name": "Proyecto Wizard"},
        EnterpriseWizardStep.LOCATION: {"country": "PE", "region": "Lima"},
        EnterpriseWizardStep.SPECIALTIES: {"specialties": ["bim", "gis"]},
        EnterpriseWizardStep.WEB_SIG: {
            "template_id": "WEB-SIG-ENTERPRISE-REV13",
            "websig_slug": "crtg-wiz-psz",
            "websig_instance_id": "WEB-CRTG-WIZ-PSZ",
            "websig_url": "https://websig.example.com/crtg-wiz/psz",
        },
        EnterpriseWizardStep.GIS: {
            "postgis_schema": "crtg_wiz_psz",
            "geoserver_workspace": "CRTG_WIZ_PSZ",
            "gis_binding_id": "GBD-CRTG-WIZ-PSZ",
        },
        EnterpriseWizardStep.NAS: {
            "nas_root_uri": "nas://CRTG-WIZ/PSZ-WIZ",
            "google_drive_folder_id": "DRIVE-WIZ",
        },
        EnterpriseWizardStep.USERS: {
            "users": [
                {
                    "user_id": "USR-WIZ-001",
                    "email": "wizard@example.com",
                    "display_name": "Wizard User",
                    "role": "portfolio_manager",
                }
            ]
        },
        EnterpriseWizardStep.ACTIVATION: {"approved_by": "portfolio-manager"},
    }
    for step, data in payloads.items():
        service.save_step(wizard_id, step, EnterpriseWizardStepSubmission(data=data, actor="tester"))


def test_enterprise_wizard_saves_partial_progress_and_validates_independently() -> None:
    service, _, _, audit = build_wizard_service()

    started = service.start(wizard_id="WIZ-001", actor="tester")
    invalid = service.validate_step(EnterpriseWizardStep.PROJECT, {"project_id": "PSZ-WIZ"})
    saved = service.save_step(
        "WIZ-001",
        EnterpriseWizardStep.COMPANY,
        EnterpriseWizardStepSubmission(
            data={
                "company_id": "CRTG-WIZ",
                "legal_name": "CRTG Wizard S.A.C.",
                "display_name": "CRTG Wizard",
            },
            actor="tester",
        ),
    )

    assert started.current_step == EnterpriseWizardStep.COMPANY
    assert invalid.status == EnterpriseWizardStepStatus.INVALID
    assert "name is required" in invalid.validation_errors
    assert saved.company_id == "CRTG-WIZ"
    assert saved.current_step == EnterpriseWizardStep.PROGRAM
    assert service.get("WIZ-001").steps[0].status == EnterpriseWizardStepStatus.VALID
    assert {event.action for event in audit.events} >= {
        "enterprise_wizard.started",
        "enterprise_wizard.step_saved",
    }


def test_enterprise_wizard_activation_creates_governed_project_and_workflow() -> None:
    service, project_repository, workflow_repository, audit = build_wizard_service()
    service.start(wizard_id="WIZ-002", actor="tester")
    complete_wizard(service, "WIZ-002")

    activated = service.activate(
        "WIZ-002",
        EnterpriseWizardActivation(actor="portfolio-manager", reason="Activacion controlada"),
    )
    project = project_repository.get("PSZ-WIZ")
    workflow = workflow_repository.get_workflow("CWF-WIZ-002")

    assert activated.status == "activated"
    assert activated.company_id == "CRTG-WIZ"
    assert activated.project_id == "PSZ-WIZ"
    assert activated.workflow_id == "CWF-WIZ-002"
    assert project is not None
    assert project.status == "active"
    assert project.websig_instance_id == "WEB-CRTG-WIZ-PSZ"
    assert project.nas_root_uri == "nas://CRTG-WIZ/PSZ-WIZ"
    assert workflow is not None
    assert workflow.current_stage == "activate_project"
    assert "enterprise_wizard.activated" in {event.action for event in audit.events}
