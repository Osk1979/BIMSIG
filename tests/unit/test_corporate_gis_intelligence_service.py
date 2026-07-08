from datetime import date

from control_tower.application.corporate_gis_intelligence_service import CorporateGisIntelligenceService
from control_tower.application.enterprise_service import CompanyService
from control_tower.application.portfolio_service import PortfolioService
from control_tower.domain.corporate_gis_intelligence import (
    CorporateGisSource,
    CorporateLayer,
    CorporateLayerStatus,
    CorporateLayerType,
    GisDiscipline,
    GisServiceKind,
)
from control_tower.domain.enterprise import Company
from control_tower.domain.portfolio import PortfolioProject, ProjectLifecycleStage, ProjectStatus
from tests.unit.fakes import (
    FakeAuditEventRepository,
    FakeCompanyRepository,
    FakeCorporateGisIntelligenceRepository,
    FakePortfolioProjectRepository,
)


def test_corporate_gis_intelligence_builds_spatial_summary() -> None:
    audit = FakeAuditEventRepository()
    companies = CompanyService(FakeCompanyRepository(), audit)
    portfolio = PortfolioService(FakePortfolioProjectRepository(), audit)
    repository = FakeCorporateGisIntelligenceRepository()
    service = CorporateGisIntelligenceService(repository, companies, portfolio, audit)
    companies.register(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    portfolio.register(
        PortfolioProject(
            project_id="PSZ-2026",
            company_id="CRTG",
            name="Proyecto Suiza",
            status=ProjectStatus.ACTIVE,
            lifecycle_stage=ProjectLifecycleStage.EXECUTION,
            websig_instance_id="WEB-CRTG-PSZ-2026",
        )
    )
    source = service.register_source(
        CorporateGisSource(
            source_id="CGIS-SRC-001",
            company_id="CRTG",
            project_id="PSZ-2026",
            websig_instance_id="WEB-CRTG-PSZ-2026",
            service_kind=GisServiceKind.WMS,
            service_url="https://websig.example.com/crtg/psz-2026/wms",
            discipline=GisDiscipline.PRODUCTION,
            layer_type=CorporateLayerType.PHYSICAL_PROGRESS,
            updated_on=date(2026, 7, 8),
        )
    )
    layer = service.register_layer(
        CorporateLayer(
            layer_id="CGIS-LYR-001",
            source_id=source.source_id,
            company_id="CRTG",
            project_id="PSZ-2026",
            name="Avance fisico",
            layer_type=CorporateLayerType.PHYSICAL_PROGRESS,
            discipline=GisDiscipline.PRODUCTION,
            status=CorporateLayerStatus.AVAILABLE,
            spatial_indicator="physical_progress",
            indicator_value=78,
            updated_on=date(2026, 7, 8),
            region="Lima",
        )
    )

    summary = service.summary("CRTG")
    filtered = service.filter_projects_by_indicator("CRTG", "physical_progress", 70)

    assert layer.layer_id == "CGIS-LYR-001"
    assert summary.total_projects_georeferenced == 1
    assert summary.projects_with_active_layers == 1
    assert summary.aggregated_spatial_progress == 78
    assert summary.regions["Lima"] == 1
    assert filtered[0].project_name == "Proyecto Suiza"
    assert {"gis_intelligence.source_registered", "gis_intelligence.layer_registered"} <= {
        event.action for event in audit.events
    }
