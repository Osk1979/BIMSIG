from datetime import date

from control_tower.application.dashboard_service import DashboardService
from control_tower.application.enterprise_service import CompanyService, LicensingService, UserService
from control_tower.application.nas_service import NasInformationCenterService
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
    FakeInformationAssetRepository,
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
    assert reporting.printable_html(report.manifest.report_id) == report.html
    assert "corporate_report.issued" in {event.action for event in audit.events}


def test_reporting_service_lists_governed_template_catalog() -> None:
    audit = FakeAuditEventRepository()
    companies = CompanyService(FakeCompanyRepository(), audit)
    users = UserService(FakeUserRepository(), FakeMembershipRepository(), companies, audit)
    licensing = LicensingService(FakeLicensePlanRepository(), FakeCompanyLicenseRepository(), companies, audit)
    portfolio = PortfolioService(FakePortfolioProjectRepository(), audit)
    provisioning = ProvisioningService(portfolio, FakeProvisioningRequestRepository(), audit)
    dashboard = DashboardService(companies, users, licensing, portfolio, provisioning)
    reporting = CorporateReportingService(dashboard, audit)

    templates = reporting.list_templates()

    assert {template.template.value for template in templates} >= {
        "executive_portfolio",
        "company_status",
        "project_governance",
        "gis_corporate",
        "audit_summary",
    }
    assert all(template.data_sources for template in templates)
    assert all(
        "html_print" in {output.value for output in template.output_formats}
        for template in templates
    )


def test_reporting_service_exports_pdf_and_registers_nas_asset(tmp_path) -> None:
    from pypdf import PdfReader

    audit = FakeAuditEventRepository()
    company_repository = FakeCompanyRepository()
    portfolio_repository = FakePortfolioProjectRepository()
    information_repository = FakeInformationAssetRepository()
    companies = CompanyService(company_repository, audit)
    users = UserService(FakeUserRepository(), FakeMembershipRepository(), companies, audit)
    licensing = LicensingService(FakeLicensePlanRepository(), FakeCompanyLicenseRepository(), companies, audit)
    portfolio = PortfolioService(portfolio_repository, audit)
    provisioning = ProvisioningService(portfolio, FakeProvisioningRequestRepository(), audit)
    dashboard = DashboardService(companies, users, licensing, portfolio, provisioning)
    nas = NasInformationCenterService(information_repository, companies, portfolio, audit)
    reporting = CorporateReportingService(dashboard, audit, nas, output_dir=str(tmp_path))

    companies.register(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    portfolio.register(
        PortfolioProject(
            project_id="PSZ-2026",
            company_id="CRTG",
            name="Proyecto Suiza",
            country="PE",
            region="Lima",
            province="Lima",
            district="Miraflores",
        )
    )

    report = reporting.export_pdf(ReportRequest(company_id="CRTG", requested_by="cto"))
    pdf_path = tmp_path / f"{report.manifest.report_id}.pdf"
    reader = PdfReader(str(pdf_path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    assert report.manifest.output_format == "pdf"
    assert report.pdf_path == str(pdf_path)
    assert report.pdf_size_bytes and report.pdf_size_bytes > 1000
    assert len(report.manifest.checksum_sha256) == 64
    assert "BIMSIG Enterprise" in text
    assert "Proyecto Suiza" in text
    assert information_repository.assets[f"NAS-{report.manifest.report_id}"].logical_uri.endswith(".pdf")
    assert "nas.asset_registered" in {event.action for event in audit.events}
