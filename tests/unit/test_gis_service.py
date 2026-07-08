from control_tower.application.enterprise_service import CompanyService
from control_tower.application.gis_service import CorporateGisService
from control_tower.application.portfolio_service import PortfolioService
from control_tower.domain.enterprise import Company
from control_tower.domain.gis import (
    GeoServerDatastore,
    GeoServerLayer,
    GeoServerWorkspace,
    GisResourceStatus,
    PostgisSchema,
    ProjectGisBinding,
)
from control_tower.domain.portfolio import PortfolioProject
from tests.unit.fakes import (
    FakeAuditEventRepository,
    FakeCompanyRepository,
    FakeCorporateGisRepository,
    FakePortfolioProjectRepository,
)


def test_corporate_gis_service_registers_and_validates_project_resources() -> None:
    audit = FakeAuditEventRepository()
    companies = CompanyService(FakeCompanyRepository(), audit)
    portfolio = PortfolioService(FakePortfolioProjectRepository(), audit)
    service = CorporateGisService(FakeCorporateGisRepository(), companies, portfolio, audit)
    companies.register(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    portfolio.register_for_company(
        "CRTG",
        PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"),
    )

    schema = service.register_postgis_schema(
        PostgisSchema(
            schema_id="PGS-001",
            company_id="CRTG",
            project_id="PSZ-2026",
            schema_name="crtg_psz_2026",
            database_ref="postgis://CRTG/crtg_psz_2026",
        )
    )
    workspace = service.register_workspace(
        GeoServerWorkspace(
            workspace_id="GWS-001",
            company_id="CRTG",
            project_id="PSZ-2026",
            name="CRTG_PSZ_2026",
            geoserver_url="https://geoserver.example.com",
        )
    )
    datastore = service.register_datastore(
        GeoServerDatastore(
            datastore_id="GDS-001",
            company_id="CRTG",
            project_id="PSZ-2026",
            workspace_id="GWS-001",
            name="postgis_psz",
            postgis_schema_id="PGS-001",
        )
    )
    layer = service.register_layer(
        GeoServerLayer(
            layer_id="GLY-001",
            company_id="CRTG",
            project_id="PSZ-2026",
            workspace_id="GWS-001",
            datastore_id="GDS-001",
            name="frentes_obra",
            title="Frentes de obra",
            wms_url="https://geoserver.example.com/wms?layers=CRTG_PSZ_2026:frentes_obra",
            wfs_url="https://geoserver.example.com/wfs?typeName=CRTG_PSZ_2026:frentes_obra",
        )
    )
    binding = service.bind_project_resources(
        ProjectGisBinding(
            binding_id="GBD-001",
            company_id="CRTG",
            project_id="PSZ-2026",
            postgis_schema_id="PGS-001",
            geoserver_workspace_id="GWS-001",
        )
    )

    validations = service.validate_project_resources("CRTG", "PSZ-2026")
    validated = service.mark_validated("CRTG", "PSZ-2026")

    assert schema.schema_name == "crtg_psz_2026"
    assert workspace.name == "CRTG_PSZ_2026"
    assert datastore.postgis_schema_id == "PGS-001"
    assert layer.wms_url is not None
    assert binding.geoserver_workspace_id == "GWS-001"
    assert validations and all(validation.valid for validation in validations)
    assert validated.postgis_schema is not None
    assert validated.postgis_schema.status == GisResourceStatus.VALIDATED
    assert validated.layers[0].status == GisResourceStatus.VALIDATED
    assert {
        event.action for event in audit.events
    } >= {
        "gis.postgis_schema_registered",
        "gis.workspace_registered",
        "gis.datastore_registered",
        "gis.layer_registered",
        "gis.project_bound",
        "gis.resources_validated",
    }
