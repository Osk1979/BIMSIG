from control_tower.application.enterprise_service import CompanyService
from control_tower.application.operational_flow_service import OperationalFlowService
from control_tower.application.portfolio_service import CorporatePortfolioDomainService, PortfolioService
from control_tower.domain.enterprise import Company
from control_tower.domain.operations import OperationalState
from control_tower.domain.portfolio import PortfolioProject, ProjectLifecycleStage, ProjectStatus
from control_tower.domain.provisioning import ProvisioningRequest, ProvisioningStatus
from tests.unit.fakes import (
    FakeAuditEventRepository,
    FakeCompanyRepository,
    FakeCorporateCustomerRepository,
    FakeCorporateGisRepository,
    FakeCorporateWorkflowRepository,
    FakeEnterpriseWizardRepository,
    FakeCorporateProgramRepository,
    FakeInformationAssetRepository,
    FakePortfolioProjectRepository,
    FakeProvisioningRequestRepository,
)


def test_operational_flow_marks_governed_references_as_observed() -> None:
    audit = FakeAuditEventRepository()
    companies = CompanyService(FakeCompanyRepository(), audit)
    portfolio = PortfolioService(FakePortfolioProjectRepository(), audit)
    provisioning = FakeProvisioningRequestRepository()
    corporate_portfolio = CorporatePortfolioDomainService(
        FakeCorporateCustomerRepository(),
        FakeCorporateProgramRepository(),
        portfolio,
        provisioning,
        FakeInformationAssetRepository(),
        FakeCorporateGisRepository(),
        audit,
    )
    flow = OperationalFlowService(companies, portfolio, corporate_portfolio, provisioning)

    companies.register(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    corporate_portfolio.register_project(
        PortfolioProject(
            project_id="PSZ-2026",
            company_id="CRTG",
            name="Proyecto Suiza",
            status=ProjectStatus.ACTIVE,
            lifecycle_stage=ProjectLifecycleStage.EXECUTION,
            websig_instance_id="WEB-CRTG-PSZ-2026",
            websig_url="https://websig.example.com/crtg/psz-2026",
            nas_root_uri="nas://CRTG/PSZ-2026/websig/root",
            gis_binding_id="GBD-CRTG-PSZ-2026",
        )
    )
    provisioning.save(
        ProvisioningRequest(
            request_id="PPE-001",
            project_id="PSZ-2026",
            company_id="CRTG",
            status=ProvisioningStatus.PROVISIONED,
            approved_by="portfolio-manager",
        )
    )

    result = flow.company_flow("CRTG")

    assert result.summary.total_projects == 1
    assert result.summary.observed == 1
    assert result.summary.average_readiness >= 80
    assert result.items[0].current_state == OperationalState.OBSERVED
    assert result.items[0].approved_by == "portfolio-manager"
    assert result.items[0].websig_registered is True
    assert result.items[0].nas_registered is True
    assert result.items[0].gis_registered is True
    assert result.items[0].next_action == "Mantener monitoreo, release y respaldo USB"


def test_operating_model_connects_existing_domains_without_new_domain() -> None:
    audit = FakeAuditEventRepository()
    companies = CompanyService(FakeCompanyRepository(), audit)
    portfolio = PortfolioService(FakePortfolioProjectRepository(), audit)
    provisioning = FakeProvisioningRequestRepository()
    information = FakeInformationAssetRepository()
    gis = FakeCorporateGisRepository()
    workflows = FakeCorporateWorkflowRepository()
    wizards = FakeEnterpriseWizardRepository()
    corporate_portfolio = CorporatePortfolioDomainService(
        FakeCorporateCustomerRepository(),
        FakeCorporateProgramRepository(),
        portfolio,
        provisioning,
        information,
        gis,
        audit,
    )
    flow = OperationalFlowService(
        companies,
        portfolio,
        corporate_portfolio,
        provisioning,
        workflows,
        wizards,
        information,
        gis,
        audit,
    )

    companies.register(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    corporate_portfolio.register_project(
        PortfolioProject(
            project_id="PSZ-2026",
            company_id="CRTG",
            name="Proyecto Suiza",
            status=ProjectStatus.ACTIVE,
            lifecycle_stage=ProjectLifecycleStage.EXECUTION,
            websig_instance_id="WEB-CRTG-PSZ-2026",
            nas_root_uri="nas://CRTG/PSZ-2026",
            gis_binding_id="GBD-CRTG-PSZ-2026",
        )
    )

    model = flow.company_operating_model("CRTG")

    assert model.phase == "Fase 3 - funcionamiento operativo"
    assert model.flow.summary.total_projects == 1
    assert {capability.capability_id for capability in model.capabilities} >= {
        "enterprise-wizard",
        "workflow-engine",
        "portfolio-governance",
        "websig-factory",
        "corporate-information-center",
        "corporate-gis",
        "audit-continuity",
    }
    assert {lane.lane_id for lane in model.lanes} == {
        "intake",
        "provisioning",
        "governance",
        "intelligence",
        "continuity",
    }
    assert model.priority_actions
