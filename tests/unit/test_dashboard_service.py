from datetime import date

from control_tower.application.dashboard_service import DashboardService
from control_tower.application.enterprise_service import CompanyService, LicensingService, UserService
from control_tower.application.portfolio_service import PortfolioService
from control_tower.application.provisioning_service import ProvisioningService
from control_tower.domain.enterprise import Company, CompanyLicense, CompanyMembership, LicensePlan, User
from control_tower.domain.portfolio import PortfolioProject
from tests.unit.fakes import (
    FakeAuditEventRepository,
    FakeCompanyLicenseRepository,
    FakeCompanyRepository,
    FakeLicensePlanRepository,
    FakeMembershipRepository,
    FakePortfolioProjectRepository,
    FakeProvisioningRequestRepository,
    FakeUserRepository,
)


def test_dashboard_service_builds_company_executive_read_model() -> None:
    audit = FakeAuditEventRepository()
    companies = CompanyService(FakeCompanyRepository(), audit)
    users = UserService(FakeUserRepository(), FakeMembershipRepository(), companies, audit)
    licensing = LicensingService(
        FakeLicensePlanRepository(),
        FakeCompanyLicenseRepository(),
        companies,
        audit,
    )
    portfolio = PortfolioService(FakePortfolioProjectRepository(), audit)
    provisioning = ProvisioningService(portfolio, FakeProvisioningRequestRepository(), audit)
    dashboard = DashboardService(companies, users, licensing, portfolio, provisioning)

    companies.register(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    users.register_user(User(user_id="USR-001", email="admin@example.com", display_name="Admin"))
    users.add_membership(
        CompanyMembership(
            membership_id="MEM-001",
            company_id="CRTG",
            user_id="USR-001",
            role="portfolio_manager",
        )
    )
    licensing.create_plan(LicensePlan(plan_id="PLAN-ENTERPRISE", name="Enterprise"))
    licensing.assign_license(
        CompanyLicense(
            company_license_id="LIC-001",
            company_id="CRTG",
            plan_id="PLAN-ENTERPRISE",
            valid_from=date(2026, 7, 8),
        )
    )
    portfolio.register(PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"))
    provisioning.request_websig("PSZ-2026")

    result = dashboard.executive_dashboard("CRTG")

    assert result.company_id == "CRTG"
    assert result.portfolio["total_projects"] == 1
    assert result.map_points[0].project_id == "PSZ-2026"
    assert result.users[0].value == "1"
    assert result.licenses[0].value == "1"
    assert result.comparisons[0].name == "Proyecto Suiza"
    assert result.portfolio_governance[0].project_id == "PSZ-2026"
    assert result.portfolio_governance[0].lifecycle_stage == "intake"
    assert result.portfolio_governance[0].websig == "pendiente"
