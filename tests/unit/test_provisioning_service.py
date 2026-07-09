import pytest
import json

from control_tower.application.portfolio_service import PortfolioService
from control_tower.application.provisioning_service import (
    ProjectProvisioningEngine,
    ProjectProvisioningSpec,
    ProvisioningService,
)
from control_tower.application.enterprise_service import CompanyService, UserService
from control_tower.domain.enterprise import Company, CompanyMembership, User
from control_tower.domain.portfolio import PortfolioProject, ProjectStatus
from control_tower.domain.provisioning import (
    ProvisioningExecutionMode,
    ProvisioningOperation,
    ProvisioningResourceType,
    ProvisioningStatus,
)
from control_tower.infrastructure.adapters.provisioning import (
    DocumentStructureProvisioningAdapter,
    NasProvisioningAdapter,
    WebSigFactoryTemplateProvisioningAdapter,
    default_project_stack_adapters,
)
from tests.unit.fakes import (
    FakeAuditEventRepository,
    FakeCompanyRepository,
    FakeMembershipRepository,
    FakePortfolioProjectRepository,
    FakeProvisioningRequestRepository,
    FakeUserRepository,
)


def test_request_websig_requires_registered_project() -> None:
    portfolio = PortfolioService(FakePortfolioProjectRepository())
    provisioning = ProvisioningService(portfolio, FakeProvisioningRequestRepository())

    with pytest.raises(ValueError):
        provisioning.request_websig("MISSING")


def test_request_websig_for_registered_project() -> None:
    portfolio = PortfolioService(FakePortfolioProjectRepository())
    portfolio.register(PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"))
    provisioning = ProvisioningService(portfolio, FakeProvisioningRequestRepository(), FakeAuditEventRepository())

    request = provisioning.request_websig("PSZ-2026")

    assert request.project_id == "PSZ-2026"
    assert request.target_revision == "REV12"
    assert request.status == ProvisioningStatus.REQUESTED
    assert request.company_id == "CRTG"
    assert portfolio.get_project("PSZ-2026").status == ProjectStatus.PROVISIONING_REQUESTED


def test_project_provisioning_engine_creates_enterprise_project_stack() -> None:
    audit = FakeAuditEventRepository()
    companies = CompanyService(FakeCompanyRepository(), audit)
    users = UserService(FakeUserRepository(), FakeMembershipRepository(), companies, audit)
    portfolio = PortfolioService(FakePortfolioProjectRepository(), audit)
    provisioning_repository = FakeProvisioningRequestRepository()
    engine = ProjectProvisioningEngine(
        companies,
        users,
        portfolio,
        provisioning_repository,
        adapters=default_project_stack_adapters(),
        audit_repository=audit,
    )

    request = engine.provision_project_stack(
        ProjectProvisioningSpec(
            company=Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"),
            project=PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"),
            users=[User(user_id="USR-001", email="admin@example.com", display_name="Admin")],
            memberships=[
                CompanyMembership(
                    membership_id="MEM-001",
                    company_id="CRTG",
                    user_id="USR-001",
                    role="portfolio_manager",
                )
            ],
            catalogs=["disciplinas", "estados_gobierno"],
            approved_by="portfolio-manager",
        )
    )

    assert request.operation == ProvisioningOperation.PROJECT_STACK
    assert request.status == ProvisioningStatus.PROVISIONED
    assert request.execution_mode == ProvisioningExecutionMode.CONTROLLED
    assert request.approved_by == "portfolio-manager"
    assert request.company_id == "CRTG"
    assert portfolio.get_project_for_company("CRTG", "PSZ-2026").status == ProjectStatus.ACTIVE
    assert {
        step.resource_type for step in request.steps
    } >= {
        ProvisioningResourceType.COMPANY,
        ProvisioningResourceType.PROJECT,
        ProvisioningResourceType.WEB_SIG,
        ProvisioningResourceType.POSTGIS,
        ProvisioningResourceType.NAS,
        ProvisioningResourceType.DOCUMENT_STRUCTURE,
        ProvisioningResourceType.GEOSERVER,
        ProvisioningResourceType.DASHBOARD,
        ProvisioningResourceType.USER,
        ProvisioningResourceType.ROLE,
        ProvisioningResourceType.CATALOG,
    }
    assert "provisioning.project_stack_provisioned" in {event.action for event in audit.events}


def test_project_provisioning_engine_requires_approval_for_controlled_execution() -> None:
    companies = CompanyService(FakeCompanyRepository())
    users = UserService(FakeUserRepository(), FakeMembershipRepository(), companies)
    portfolio = PortfolioService(FakePortfolioProjectRepository())
    engine = ProjectProvisioningEngine(companies, users, portfolio, FakeProvisioningRequestRepository())

    with pytest.raises(ValueError, match="approved_by"):
        engine.provision_project_stack(
            ProjectProvisioningSpec(
                company=Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"),
                project=PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"),
            )
        )


def test_project_provisioning_engine_dry_run_has_no_side_effects() -> None:
    companies = CompanyService(FakeCompanyRepository())
    users = UserService(FakeUserRepository(), FakeMembershipRepository(), companies)
    portfolio = PortfolioService(FakePortfolioProjectRepository())
    engine = ProjectProvisioningEngine(companies, users, portfolio, FakeProvisioningRequestRepository())

    request = engine.dry_run_project_stack(
        ProjectProvisioningSpec(
            company=Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"),
            project=PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"),
        )
    )

    assert request.operation == ProvisioningOperation.PROJECT_STACK
    assert request.status == ProvisioningStatus.REQUESTED
    assert request.execution_mode == ProvisioningExecutionMode.DRY_RUN
    assert {step.status for step in request.steps} == {"planned"}
    assert companies.exists("CRTG") is False
    assert portfolio.get_project("PSZ-2026") is None


def test_project_provisioning_engine_executes_filesystem_adapters(tmp_path) -> None:
    companies = CompanyService(FakeCompanyRepository())
    users = UserService(FakeUserRepository(), FakeMembershipRepository(), companies)
    portfolio = PortfolioService(FakePortfolioProjectRepository())
    engine = ProjectProvisioningEngine(
        companies,
        users,
        portfolio,
        FakeProvisioningRequestRepository(),
        adapters=[
            NasProvisioningAdapter(str(tmp_path)),
            DocumentStructureProvisioningAdapter(str(tmp_path)),
        ],
    )

    engine.provision_project_stack(
        ProjectProvisioningSpec(
            company=Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"),
            project=PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"),
            document_structure=["00_gobierno", "03_gis"],
            approved_by="portfolio-manager",
        )
    )

    assert (tmp_path / "CRTG" / "PSZ-2026" / "websig").is_dir()
    assert (tmp_path / "CRTG" / "PSZ-2026" / "documents" / "00_gobierno").is_dir()
    assert (tmp_path / "CRTG" / "PSZ-2026" / "documents" / "03_gis").is_dir()


def test_websig_factory_execute_updates_project_references() -> None:
    companies = CompanyService(FakeCompanyRepository())
    users = UserService(FakeUserRepository(), FakeMembershipRepository(), companies)
    portfolio = PortfolioService(FakePortfolioProjectRepository())
    engine = ProjectProvisioningEngine(
        companies,
        users,
        portfolio,
        FakeProvisioningRequestRepository(),
        adapters=default_project_stack_adapters(),
    )

    request = engine.execute_websig_factory(
        ProjectProvisioningSpec(
            company=Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"),
            project=PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"),
            approved_by="portfolio-manager",
        )
    )
    project = portfolio.get_project_for_company("CRTG", "PSZ-2026")

    assert request.operation == ProvisioningOperation.WEB_SIG_FACTORY
    assert request.status == ProvisioningStatus.PROVISIONED
    assert {step.resource_type for step in request.steps} >= {
        ProvisioningResourceType.FACTORY_BLUEPRINT,
        ProvisioningResourceType.GOVERNANCE_GATE,
        ProvisioningResourceType.WEB_SIG,
    }
    assert project.websig_instance_id == "WEB-CRTG-PSZ-2026"
    assert project.websig_url == "websig://CRTG/crtg-psz-2026"
    assert project.nas_root_uri == "nas://CRTG/PSZ-2026/websig/root"
    assert project.gis_binding_id == "GBD-CRTG-PSZ-2026"


def test_websig_factory_template_adapter_creates_instance_config(tmp_path) -> None:
    template = tmp_path / "WEB_SIG_ENTERPRISE_REPOSITORY_REV02_FACTORY_TEMPLATE_WEB-SIG-001"
    output = tmp_path / "instances"
    template.mkdir()
    (template / "index.html").write_text("<html>WEB SIG Factory Template</html>", encoding="utf-8")

    companies = CompanyService(FakeCompanyRepository())
    users = UserService(FakeUserRepository(), FakeMembershipRepository(), companies)
    portfolio = PortfolioService(FakePortfolioProjectRepository())
    engine = ProjectProvisioningEngine(
        companies,
        users,
        portfolio,
        FakeProvisioningRequestRepository(),
        adapters=[WebSigFactoryTemplateProvisioningAdapter(str(template), str(output))],
    )

    request = engine.execute_websig_factory(
        ProjectProvisioningSpec(
            company=Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"),
            project=PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"),
            approved_by="portfolio-manager",
        )
    )

    target = output / "CRTG" / "crtg-psz-2026"
    config = json.loads((target / "websig.config.json").read_text(encoding="utf-8"))

    assert request.operation == ProvisioningOperation.WEB_SIG_FACTORY
    assert target.is_dir()
    assert (target / "index.html").is_file()
    assert config["company_id"] == "CRTG"
    assert config["project_id"] == "PSZ-2026"
    assert config["websig_id"] == "WEB-CRTG-PSZ-2026"
    assert config["postgis_schema"] == "CRTG_PSZ_2026"
    assert config["geoserver_workspace"] == "CRTG_PSZ_2026"
    assert config["tower_boundary"]["geometry_editing_by_tower"] is False
