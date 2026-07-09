from control_tower.application.enterprise_scale_service import EnterpriseScaleSeedRequest, EnterpriseScaleService
from control_tower.application.enterprise_service import CompanyService
from control_tower.application.portfolio_service import CorporatePortfolioDomainService, PortfolioService
from control_tower.domain.portfolio import ProjectStatus
from tests.unit.fakes import (
    FakeAuditEventRepository,
    FakeCompanyRepository,
    FakeCorporateCustomerRepository,
    FakeCorporateGisRepository,
    FakeCorporateProgramRepository,
    FakeInformationAssetRepository,
    FakePortfolioProjectRepository,
    FakeProvisioningRequestRepository,
)


def build_scale_service() -> EnterpriseScaleService:
    portfolio = PortfolioService(FakePortfolioProjectRepository(), FakeAuditEventRepository())
    corporate_portfolio = CorporatePortfolioDomainService(
        FakeCorporateCustomerRepository(),
        FakeCorporateProgramRepository(),
        portfolio,
        FakeProvisioningRequestRepository(),
        FakeInformationAssetRepository(),
        FakeCorporateGisRepository(),
        FakeAuditEventRepository(),
    )
    return EnterpriseScaleService(
        CompanyService(FakeCompanyRepository(), FakeAuditEventRepository()),
        portfolio,
        corporate_portfolio,
    )


def test_enterprise_scale_seed_creates_paginated_dataset() -> None:
    service = build_scale_service()

    result = service.seed(
        EnterpriseScaleSeedRequest(
            company_count=2,
            programs_per_company=2,
            projects_per_program=5,
            prefix="QA",
        )
    )
    page = service.project_page(page=2, page_size=4, company_id="QA-C001")
    summary = service.summary()

    assert result.projects == 20
    assert page.total == 10
    assert page.page == 2
    assert len(page.items) == 4
    assert summary.companies == 2
    assert summary.projects == 20


def test_enterprise_scale_filters_search_and_validates_isolation() -> None:
    service = build_scale_service()
    service.seed(
        EnterpriseScaleSeedRequest(
            company_count=2,
            programs_per_company=1,
            projects_per_program=5,
            prefix="ISO",
        )
    )

    active = service.project_page(company_id="ISO-C001", status=ProjectStatus.ACTIVE)
    search = service.search("ISO-C002-PRG-001")
    isolation = service.validate_isolation()

    assert {project.company_id for project in active.items} == {"ISO-C001"}
    assert active.total == 1
    assert search.programs[0].company_id == "ISO-C002"
    assert search.projects
    assert isolation.status == "ok"
    assert isolation.checked_projects == 10
