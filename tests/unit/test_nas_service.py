from control_tower.application.enterprise_service import CompanyService
from control_tower.application.nas_service import NasInformationCenterService
from control_tower.application.portfolio_service import PortfolioService
from control_tower.domain.enterprise import Company
from control_tower.domain.nas import (
    InformationAsset,
    InformationAssetStatus,
    InformationAssetType,
    InformationCategory,
)
from control_tower.domain.portfolio import PortfolioProject
from tests.unit.fakes import (
    FakeAuditEventRepository,
    FakeCompanyRepository,
    FakeInformationAssetRepository,
    FakePortfolioProjectRepository,
)


def test_nas_information_center_registers_versions_snapshots_backups_and_permissions() -> None:
    audit = FakeAuditEventRepository()
    companies = CompanyService(FakeCompanyRepository(), audit)
    portfolio = PortfolioService(FakePortfolioProjectRepository(), audit)
    repository = FakeInformationAssetRepository()
    service = NasInformationCenterService(repository, companies, portfolio, audit)
    companies.register(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    portfolio.register(PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"))

    asset = service.register_asset(
        InformationAsset(
            asset_id="NAS-001",
            company_id="CRTG",
            project_id="PSZ-2026",
            name="Modelo federado IFC",
            asset_type=InformationAssetType.IFC,
            category=InformationCategory.BIM,
            logical_uri="nas://CRTG/PSZ-2026/bim/ifc/model.ifc",
            metadata={"discipline": "bim"},
            google_drive_id="drive-folder-1",
            geoserver_reference="geoserver://workspace/CRTG_PSZ",
            postgis_reference="postgis://CRTG/psz_2026",
            docker_reference="docker://websig/psz-2026",
        )
    )
    version = service.register_version(
        asset.asset_id,
        version="v2",
        logical_uri="nas://CRTG/PSZ-2026/bim/ifc/model-v2.ifc",
    )
    updated = service.set_permission(asset.asset_id, "role:portfolio_manager", "admin")
    enriched = service.update_metadata(asset.asset_id, {"format": "IFC4"})
    snapshot = service.create_snapshot("CRTG", "Cierre Semanal", [asset.asset_id], project_id="PSZ-2026")
    backup = service.register_backup(
        "CRTG",
        "nas://CRTG/PSZ-2026/backups/cierre-semanal.zip",
        project_id="PSZ-2026",
        snapshot_id=snapshot.snapshot_id,
    )
    archived = service.archive_asset(asset.asset_id)

    assert asset.status == InformationAssetStatus.DRAFT
    assert version.version == "v2"
    assert updated.permissions["role:portfolio_manager"] == "admin"
    assert enriched.metadata["format"] == "IFC4"
    assert snapshot.asset_ids == ["NAS-001"]
    assert backup.snapshot_id == snapshot.snapshot_id
    assert archived.status == InformationAssetStatus.ARCHIVED
    assert {
        event.action for event in audit.events
    } >= {
        "nas.asset_registered",
        "nas.asset_versioned",
        "nas.permission_set",
        "nas.metadata_updated",
        "nas.snapshot_created",
        "nas.backup_registered",
        "nas.asset_archived",
    }
