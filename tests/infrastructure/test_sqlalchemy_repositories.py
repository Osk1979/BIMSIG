from datetime import date

from control_tower.domain.corporate_gis_intelligence import (
    CorporateGisSource,
    CorporateLayer,
    CorporateLayerType,
    GisDiscipline,
    GisServiceKind,
)
from control_tower.domain.corporate_workflow import (
    CorporateWorkflowInstance,
    CorporateWorkflowStage,
    CorporateWorkflowTransition,
)
from control_tower.domain.portfolio import CorporateCustomer, CorporateProgram, PortfolioProject
from control_tower.domain.nas import InformationAsset, InformationAssetType, InformationCategory
from control_tower.domain.provisioning import ProvisioningRequest, ProvisioningResourceType, ProvisioningStep
from control_tower.infrastructure.database import (
    SqlAlchemyCompanyRepository,
    SqlAlchemyCorporateCustomerRepository,
    SqlAlchemyCorporateGisIntelligenceRepository,
    SqlAlchemyCorporateProgramRepository,
    SqlAlchemyCorporateWorkflowRepository,
    SqlAlchemyInformationAssetRepository,
    SqlAlchemyPortfolioProjectRepository,
    SqlAlchemyProvisioningRequestRepository,
    SqlAlchemySessionProvider,
    create_database_engine,
    initialize_database,
)
from control_tower.domain.enterprise import Company


def test_sqlalchemy_project_repository_persists_records(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'repository.db'}"
    engine = create_database_engine(database_url)
    initialize_database(engine)
    sessions = SqlAlchemySessionProvider(engine)
    repository = SqlAlchemyPortfolioProjectRepository(sessions)

    repository.save(PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"))
    reloaded_repository = SqlAlchemyPortfolioProjectRepository(SqlAlchemySessionProvider(engine))

    assert reloaded_repository.exists("PSZ-2026")
    assert reloaded_repository.list()[0].name == "Proyecto Suiza"
    assert reloaded_repository.list_by_company("CRTG")[0].project_id == "PSZ-2026"


def test_sqlalchemy_corporate_portfolio_domain_persists_customer_program_links(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'corporate_portfolio.db'}"
    engine = create_database_engine(database_url)
    initialize_database(engine)
    sessions = SqlAlchemySessionProvider(engine)
    companies = SqlAlchemyCompanyRepository(sessions)
    customers = SqlAlchemyCorporateCustomerRepository(sessions)
    programs = SqlAlchemyCorporateProgramRepository(sessions)
    projects = SqlAlchemyPortfolioProjectRepository(sessions)
    companies.save(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    customers.save(
        CorporateCustomer(
            customer_id="CLI-MTC",
            company_id="CRTG",
            legal_name="Ministerio de Transportes",
            display_name="MTC",
        )
    )
    programs.save(
        CorporateProgram(
            program_id="PRG-TRANSPORTE",
            company_id="CRTG",
            customer_id="CLI-MTC",
            name="Programa Transporte",
        )
    )

    saved = projects.save(
        PortfolioProject(
            project_id="PSZ-2026",
            company_id="CRTG",
            customer_id="CLI-MTC",
            program_id="PRG-TRANSPORTE",
            name="Proyecto Suiza",
            websig_instance_id="WEB-PSZ-2026",
            nas_root_uri="nas://CRTG/PSZ-2026",
            google_drive_folder_id="DRIVE-PSZ",
        )
    )

    assert customers.list_by_company("CRTG")[0].customer_id == "CLI-MTC"
    assert programs.list_by_company("CRTG")[0].program_id == "PRG-TRANSPORTE"
    assert saved.websig_instance_id == "WEB-PSZ-2026"
    assert projects.get_by_company("CRTG", "PSZ-2026").program_id == "PRG-TRANSPORTE"


def test_sqlalchemy_provisioning_repository_persists_requests(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'provisioning.db'}"
    engine = create_database_engine(database_url)
    initialize_database(engine)
    sessions = SqlAlchemySessionProvider(engine)
    projects = SqlAlchemyPortfolioProjectRepository(sessions)
    requests = SqlAlchemyProvisioningRequestRepository(sessions)
    projects.save(PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"))

    saved = requests.save(
        ProvisioningRequest(
            request_id="PPE-001",
            project_id="PSZ-2026",
            company_id="CRTG",
            approved_by="portfolio-manager",
            steps=[
                ProvisioningStep(
                    step_id="websig",
                    resource_type=ProvisioningResourceType.WEB_SIG,
                    name="Create WEB SIG",
                    reference="websig://CRTG/PSZ-2026",
                )
            ],
        )
    )
    reloaded = requests.list_by_company("CRTG")[0]

    assert saved.request_id == "PPE-001"
    assert saved.project_id == "PSZ-2026"
    assert reloaded.approved_by == "portfolio-manager"
    assert reloaded.execution_mode == "controlled"
    assert reloaded.company_id == "CRTG"
    assert reloaded.steps[0].resource_type == ProvisioningResourceType.WEB_SIG


def test_sqlalchemy_information_asset_repository_persists_registry(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'nas.db'}"
    engine = create_database_engine(database_url)
    initialize_database(engine)
    sessions = SqlAlchemySessionProvider(engine)
    companies = SqlAlchemyCompanyRepository(sessions)
    projects = SqlAlchemyPortfolioProjectRepository(sessions)
    repository = SqlAlchemyInformationAssetRepository(sessions)
    companies.save(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    projects.save(PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"))

    asset = repository.save_asset(
        InformationAsset(
            asset_id="NAS-001",
            company_id="CRTG",
            project_id="PSZ-2026",
            name="Modelo IFC",
            asset_type=InformationAssetType.IFC,
            category=InformationCategory.BIM,
            logical_uri="nas://CRTG/PSZ-2026/bim/ifc/model.ifc",
            metadata={"discipline": "bim"},
            permissions={"role:portfolio_manager": "admin"},
        )
    )

    assert asset.asset_id == "NAS-001"
    assert asset.category == InformationCategory.BIM
    assert repository.list_assets_by_company("CRTG")[0].metadata["discipline"] == "bim"
    assert repository.get_asset("NAS-001").permissions["role:portfolio_manager"] == "admin"


def test_sqlalchemy_corporate_gis_intelligence_repository_persists_sources_layers(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'gis_intelligence.db'}"
    engine = create_database_engine(database_url)
    initialize_database(engine)
    sessions = SqlAlchemySessionProvider(engine)
    companies = SqlAlchemyCompanyRepository(sessions)
    projects = SqlAlchemyPortfolioProjectRepository(sessions)
    repository = SqlAlchemyCorporateGisIntelligenceRepository(sessions)
    companies.save(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    projects.save(PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"))

    repository.save_source(
        CorporateGisSource(
            source_id="CGIS-SRC-001",
            company_id="CRTG",
            project_id="PSZ-2026",
            service_kind=GisServiceKind.WMS,
            service_url="https://websig.example.com/wms",
            discipline=GisDiscipline.PRODUCTION,
            layer_type=CorporateLayerType.PHYSICAL_PROGRESS,
            updated_on=date(2026, 7, 8),
            metadata={"source": "websig"},
        )
    )
    repository.save_layer(
        CorporateLayer(
            layer_id="CGIS-LYR-001",
            source_id="CGIS-SRC-001",
            company_id="CRTG",
            project_id="PSZ-2026",
            name="Avance fisico",
            layer_type=CorporateLayerType.PHYSICAL_PROGRESS,
            discipline=GisDiscipline.PRODUCTION,
            spatial_indicator="physical_progress",
            indicator_value=78,
            updated_on=date(2026, 7, 8),
            metadata={"unit": "percent"},
        )
    )

    assert repository.get_source("CGIS-SRC-001").metadata["source"] == "websig"
    assert repository.list_sources("CRTG")[0].service_kind == GisServiceKind.WMS
    assert repository.list_layers("CRTG")[0].indicator_value == 78
    assert repository.list_layers("CRTG", "PSZ-2026")[0].metadata["unit"] == "percent"


def test_sqlalchemy_corporate_workflow_repository_persists_transitions(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'corporate_workflow.db'}"
    engine = create_database_engine(database_url)
    initialize_database(engine)
    sessions = SqlAlchemySessionProvider(engine)
    companies = SqlAlchemyCompanyRepository(sessions)
    projects = SqlAlchemyPortfolioProjectRepository(sessions)
    repository = SqlAlchemyCorporateWorkflowRepository(sessions)
    companies.save(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    projects.save(PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"))

    repository.save_workflow(
        CorporateWorkflowInstance(
            workflow_id="CWF-001",
            company_id="CRTG",
            project_id="PSZ-2026",
            current_stage=CorporateWorkflowStage.CREATE_COMPANY,
            completed_stages=[CorporateWorkflowStage.CREATE_COMPANY],
            created_by="portfolio-manager",
            updated_by="portfolio-manager",
        )
    )
    repository.save_transition(
        CorporateWorkflowTransition(
            transition_id="CWFT-001",
            workflow_id="CWF-001",
            company_id="CRTG",
            project_id="PSZ-2026",
            to_stage=CorporateWorkflowStage.CREATE_COMPANY,
            actor="portfolio-manager",
            reason="Workflow started",
        )
    )

    workflow = repository.get_workflow("CWF-001")
    transitions = repository.list_transitions("CWF-001")

    assert workflow is not None
    assert workflow.current_stage == CorporateWorkflowStage.CREATE_COMPANY
    assert repository.list_workflows("CRTG")[0].workflow_id == "CWF-001"
    assert transitions[0].to_stage == CorporateWorkflowStage.CREATE_COMPANY
