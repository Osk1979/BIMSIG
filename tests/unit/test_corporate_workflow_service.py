from control_tower.application.corporate_workflow_service import CorporateWorkflowEngine
from control_tower.application.enterprise_service import CompanyService
from control_tower.application.portfolio_service import PortfolioService
from control_tower.domain.corporate_workflow import CorporateWorkflowAdvance, CorporateWorkflowRollback, CorporateWorkflowStage
from control_tower.domain.enterprise import Company
from control_tower.domain.portfolio import PortfolioProject, ProjectLifecycleStage, ProjectStatus
from tests.unit.fakes import (
    FakeAuditEventRepository,
    FakeCompanyRepository,
    FakeCorporateWorkflowRepository,
    FakePortfolioProjectRepository,
)


def test_corporate_workflow_advances_and_rolls_back_with_audit() -> None:
    audit = FakeAuditEventRepository()
    companies = CompanyService(FakeCompanyRepository(), audit)
    portfolio = PortfolioService(FakePortfolioProjectRepository(), audit)
    workflow_repository = FakeCorporateWorkflowRepository()
    engine = CorporateWorkflowEngine(workflow_repository, companies, portfolio, audit)
    companies.register(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    portfolio.register(PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"))

    started = engine.start_workflow(
        "CRTG",
        workflow_id="CWF-001",
        project_id="PSZ-2026",
        actor="portfolio-manager",
    )
    advanced = engine.advance(
        "CRTG",
        "CWF-001",
        CorporateWorkflowAdvance(to_stage=CorporateWorkflowStage.CREATE_PROGRAM, actor="portfolio-manager"),
    )
    engine.advance(
        "CRTG",
        "CWF-001",
        CorporateWorkflowAdvance(to_stage=CorporateWorkflowStage.CREATE_PROJECT, actor="portfolio-manager"),
    )
    rolled_back = engine.rollback(
        "CRTG",
        "CWF-001",
        CorporateWorkflowRollback(actor="portfolio-manager", reason="Controlled test rollback"),
    )

    assert started.current_stage == CorporateWorkflowStage.CREATE_COMPANY
    assert advanced.current_stage == CorporateWorkflowStage.CREATE_PROGRAM
    assert rolled_back.current_stage == CorporateWorkflowStage.CREATE_PROGRAM
    assert workflow_repository.transitions[-1].rollback is True
    assert {
        event.action
        for event in audit.events
    } >= {
        "corporate_workflow.transitioned",
        "corporate_workflow.rollback",
    }


def test_corporate_workflow_updates_portfolio_lifecycle_on_activation() -> None:
    audit = FakeAuditEventRepository()
    companies = CompanyService(FakeCompanyRepository(), audit)
    project_repository = FakePortfolioProjectRepository()
    portfolio = PortfolioService(project_repository, audit)
    engine = CorporateWorkflowEngine(FakeCorporateWorkflowRepository(), companies, portfolio, audit)
    companies.register(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    portfolio.register(PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"))
    engine.start_workflow("CRTG", workflow_id="CWF-002", project_id="PSZ-2026")

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
        engine.advance("CRTG", "CWF-002", CorporateWorkflowAdvance(to_stage=stage))

    project = project_repository.get("PSZ-2026")

    assert project is not None
    assert project.lifecycle_stage == ProjectLifecycleStage.EXECUTION
    assert project.status == ProjectStatus.ACTIVE
