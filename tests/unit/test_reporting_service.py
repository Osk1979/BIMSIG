from datetime import date

from control_tower.application.dashboard_service import DashboardService
from control_tower.application.enterprise_service import CompanyService, LicensingService, UserService
from control_tower.application.portfolio_service import PortfolioService
from control_tower.application.provisioning_service import ProvisioningService
from control_tower.application.reporting_service import CorporateReportingService
from control_tower.domain.enterprise import Company, CompanyLicense, LicensePlan
from control_tower.domain.portfolio import PortfolioProject
from control_tower.domain.reports import ReportRequest
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


def test_reporting_service_issues_print_manifest_and_audit_event() -> None:
    audit = FakeAuditEventRepository()
    companies = CompanyService(FakeCompanyRepository(), audit)
    users = UserService(FakeUserRepository(), FakeMembershipRepository(), companies, audit)
    licensing = LicensingService(FakeLicensePlanRepository(), FakeCompanyLicenseRepository(), companies, audit)
    portfolio = PortfolioService(FakePortfolioProjectRepository(), audit)
    provisioning = ProvisioningService(portfolio, FakeProvisioningRequestRepository(), audit)
    dashboard = DashboardService(companies, users, licensing, portfolio, provisioning)
    reporting = CorporateReportingService(dashboard, audit)

    companies.register(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    licensing.create_plan(LicensePlan(plan_id="PLAN-ENTERPRISE", name="Enterprise"))
    licensing.assign_license(
        CompanyLicense(
            company_license_id="LIC-001",
            company_id="CRTG",
            plan_id="PLAN-ENTERPRISE",
            valid_from=date(2026, 7, 8),
        )
    )
    portfolio.register(
        PortfolioProject(
            project_id="PSZ-2026",
            company_id="CRTG",
            name="Proyecto Suiza",
            country="PE",
            region="Lima",
            province="Lima",
            district="Miraflores",
            latitude=-12.1211,
            longitude=-77.0305,
            location_source="portfolio_domain",
            location_validation_status="validated",
        )
    )

    report = reporting.issue(ReportRequest(company_id="CRTG", requested_by="cto"))

    assert report.manifest.report_id.startswith("RPT-CRTG-EXECUTIVE_PORTFOLIO")
    assert report.manifest.nas_logical_uri.startswith("nas://CRTG/reports/")
    assert len(report.manifest.checksum_sha256) == 64
    assert "Proyecto Suiza" in report.html
    assert "Miraflores" in report.html
    assert "corporate_report.issued" in {event.action for event in audit.events}
