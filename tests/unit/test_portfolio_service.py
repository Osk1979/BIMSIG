from control_tower.application.portfolio_service import CorporatePortfolioDomainService, PortfolioService
from control_tower.domain.gis import GeoServerLayer, ProjectGisBinding
from control_tower.domain.nas import InformationAsset, InformationAssetType
from control_tower.domain.portfolio import (
    CorporateCustomer,
    CorporateProgram,
    PortfolioLifecycleTransition,
    PortfolioProject,
    ProjectLifecycleStage,
    ProjectStatus,
)
from control_tower.domain.provisioning import ProvisioningRequest
from tests.unit.fakes import (
    FakeAuditEventRepository,
    FakeCorporateCustomerRepository,
    FakeCorporateGisRepository,
    FakeCorporateProgramRepository,
    FakeInformationAssetRepository,
    FakePortfolioProjectRepository,
    FakeProvisioningRequestRepository,
)


def test_register_project_keeps_portfolio_identity() -> None:
    audit = FakeAuditEventRepository()
    service = PortfolioService(FakePortfolioProjectRepository(), audit)
    project = PortfolioProject(
        project_id="PSZ-2026",
        company_id="CRTG",
        name="Proyecto Suiza",
        cui="CUI 2661613",
    )

    registered = service.register(project)

    assert registered.project_id == "PSZ-2026"
    assert registered.status == ProjectStatus.REGISTERED
    assert service.exists("PSZ-2026")
    assert audit.events[0].action == "project.registered"


def test_change_project_status() -> None:
    service = PortfolioService(FakePortfolioProjectRepository(), FakeAuditEventRepository())
    service.register(PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"))

    updated = service.change_status("PSZ-2026", ProjectStatus.ACTIVE)

    assert updated.status == ProjectStatus.ACTIVE


def test_list_projects_for_company_only_returns_tenant_projects() -> None:
    service = PortfolioService(FakePortfolioProjectRepository())
    service.register(PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"))
    service.register(PortfolioProject(project_id="OTHER-2026", company_id="OTHER", name="Other Project"))

    projects = service.list_projects_for_company("CRTG")

    assert [project.project_id for project in projects] == ["PSZ-2026"]


def test_transition_lifecycle_maps_to_governance_status() -> None:
    service = PortfolioService(FakePortfolioProjectRepository(), FakeAuditEventRepository())
    service.register(PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"))

    updated = service.transition_lifecycle(
        "PSZ-2026",
        PortfolioLifecycleTransition(lifecycle_stage=ProjectLifecycleStage.EXECUTION),
    )

    assert updated.lifecycle_stage == ProjectLifecycleStage.EXECUTION
    assert updated.status == ProjectStatus.ACTIVE


def test_corporate_portfolio_domain_validates_customer_program_and_project_links() -> None:
    customer_repository = FakeCorporateCustomerRepository()
    program_repository = FakeCorporateProgramRepository()
    service = CorporatePortfolioDomainService(
        customer_repository,
        program_repository,
        PortfolioService(FakePortfolioProjectRepository(), FakeAuditEventRepository()),
        FakeProvisioningRequestRepository(),
        FakeInformationAssetRepository(),
        FakeCorporateGisRepository(),
        FakeAuditEventRepository(),
    )
    service.register_customer(
        CorporateCustomer(
            customer_id="CLI-MTC",
            company_id="CRTG",
            legal_name="Ministerio de Transportes",
            display_name="MTC",
        )
    )
    service.register_program(
        CorporateProgram(
            program_id="PRG-TRANSPORTE",
            company_id="CRTG",
            customer_id="CLI-MTC",
            name="Programa Transporte",
        )
    )

    project = service.register_project(
        PortfolioProject(
            project_id="PSZ-2026",
            company_id="CRTG",
            customer_id="CLI-MTC",
            program_id="PRG-TRANSPORTE",
            name="Proyecto Suiza",
            websig_instance_id="WEB-PSZ-2026",
            nas_root_uri="nas://CRTG/PSZ-2026",
        )
    )

    assert project.customer_id == "CLI-MTC"
    assert project.program_id == "PRG-TRANSPORTE"


def test_corporate_project_view_summarizes_provisioning_nas_and_gis_references() -> None:
    customer_repository = FakeCorporateCustomerRepository()
    program_repository = FakeCorporateProgramRepository()
    project_repository = FakePortfolioProjectRepository()
    provisioning_repository = FakeProvisioningRequestRepository()
    information_repository = FakeInformationAssetRepository()
    gis_repository = FakeCorporateGisRepository()
    portfolio = PortfolioService(project_repository, FakeAuditEventRepository())
    service = CorporatePortfolioDomainService(
        customer_repository,
        program_repository,
        portfolio,
        provisioning_repository,
        information_repository,
        gis_repository,
        FakeAuditEventRepository(),
    )
    customer_repository.save(
        CorporateCustomer(
            customer_id="CLI-MTC",
            company_id="CRTG",
            legal_name="Ministerio de Transportes",
            display_name="MTC",
        )
    )
    program_repository.save(
        CorporateProgram(
            program_id="PRG-TRANSPORTE",
            company_id="CRTG",
            customer_id="CLI-MTC",
            name="Programa Transporte",
        )
    )
    portfolio.register(
        PortfolioProject(
            project_id="PSZ-2026",
            company_id="CRTG",
            customer_id="CLI-MTC",
            program_id="PRG-TRANSPORTE",
            name="Proyecto Suiza",
            websig_instance_id="WEB-PSZ-2026",
            websig_url="https://websig.example.com/psz",
            nas_root_uri="nas://CRTG/PSZ-2026",
            google_drive_folder_id="DRIVE-PSZ",
        )
    )
    provisioning_repository.save(
        ProvisioningRequest(
            request_id="PRV-001",
            company_id="CRTG",
            project_id="PSZ-2026",
        )
    )
    information_repository.save_asset(
        InformationAsset(
            asset_id="NAS-001",
            company_id="CRTG",
            project_id="PSZ-2026",
            name="Expediente tecnico",
            asset_type=InformationAssetType.DOCUMENTATION,
            logical_uri="nas://CRTG/PSZ-2026/cde/expediente.pdf",
        )
    )
    gis_repository.save_binding(
        ProjectGisBinding(
            binding_id="GBD-001",
            company_id="CRTG",
            project_id="PSZ-2026",
            postgis_schema_id="PGS-001",
            geoserver_workspace_id="GWS-001",
        )
    )
    gis_repository.save_layer(
        GeoServerLayer(
            layer_id="GLY-001",
            company_id="CRTG",
            project_id="PSZ-2026",
            workspace_id="GWS-001",
            datastore_id="GDS-001",
            name="avance_obra",
            title="Avance de obra",
            wms_url="https://geoserver.example.com/wms",
        )
    )

    view = service.project_view("CRTG", "PSZ-2026")

    assert view.customer is not None
    assert view.program is not None
    assert view.integrations.websig_instance_id == "WEB-PSZ-2026"
    assert view.integrations.provisioning_requests == 1
    assert view.integrations.nas_assets == 1
    assert view.integrations.gis_binding_id == "GBD-001"
    assert view.integrations.gis_layers == 1
