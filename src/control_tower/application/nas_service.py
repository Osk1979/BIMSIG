"""Corporate Information Center NAS application service.

ADR references:
- ADR-0007: NAS integration.
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0010: Google Workspace transition integration.
- ADR-0019: NAS Corporate Information Center.
"""

from datetime import UTC, datetime
from uuid import uuid4

from control_tower.domain.audit import AuditEvent
from control_tower.domain.nas import (
    InformationAsset,
    InformationAssetStatus,
    InformationBackup,
    InformationPermission,
    InformationSnapshot,
    InformationVersion,
)

from .enterprise_service import CompanyService
from .portfolio_service import PortfolioService
from .repositories import AuditEventRepository, InformationAssetRepository


class NasInformationCenterService:
    """Coordinates corporate NAS information governance."""

    def __init__(
        self,
        repository: InformationAssetRepository,
        companies: CompanyService,
        portfolio: PortfolioService,
        audit: AuditEventRepository | None = None,
    ) -> None:
        self._repository = repository
        self._companies = companies
        self._portfolio = portfolio
        self._audit = audit

    def register_asset(self, asset: InformationAsset) -> InformationAsset:
        """Register or update a corporate information asset."""

        self._validate_scope(asset.company_id, asset.project_id)
        now = datetime.now(UTC)
        saved = self._repository.save_asset(
            asset.model_copy(update={"created_at": asset.created_at or now, "updated_at": now})
        )
        self._audit_event("nas.asset_registered", "information_asset", saved.asset_id)
        return saved

    def list_assets(self, company_id: str) -> list[InformationAsset]:
        """Return all assets registered for one company."""

        self._validate_scope(company_id, None)
        return self._repository.list_assets_by_company(company_id)

    def get_asset(self, asset_id: str) -> InformationAsset | None:
        """Return one asset when it exists."""

        return self._repository.get_asset(asset_id)

    def register_version(
        self,
        asset_id: str,
        version: str,
        logical_uri: str,
        checksum_sha256: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> InformationVersion:
        """Register a new immutable version for an asset."""

        asset = self._require_asset(asset_id)
        version_record = InformationVersion(
            version_id=f"VER-{uuid4().hex[:12]}",
            asset_id=asset_id,
            version=version,
            logical_uri=logical_uri,
            checksum_sha256=checksum_sha256,
            metadata=metadata or {},
        )
        saved = self._repository.save_version(version_record)
        self._repository.save_asset(
            asset.model_copy(
                update={
                    "version": version,
                    "logical_uri": logical_uri,
                    "checksum_sha256": checksum_sha256 or asset.checksum_sha256,
                    "status": InformationAssetStatus.REVIEW,
                    "updated_at": datetime.now(UTC),
                }
            )
        )
        self._audit_event("nas.asset_versioned", "information_asset", asset_id)
        return saved

    def list_versions(self, asset_id: str) -> list[InformationVersion]:
        """Return versions for one information asset."""

        self._require_asset(asset_id)
        return self._repository.list_versions(asset_id)

    def create_snapshot(
        self,
        company_id: str,
        name: str,
        asset_ids: list[str],
        project_id: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> InformationSnapshot:
        """Create a snapshot manifest for selected assets."""

        self._validate_scope(company_id, project_id)
        for asset_id in asset_ids:
            asset = self._require_asset(asset_id)
            if asset.company_id != company_id:
                raise ValueError(f"Asset does not belong to company {company_id}: {asset_id}")
        snapshot = InformationSnapshot(
            snapshot_id=f"SNP-{uuid4().hex[:12]}",
            company_id=company_id,
            project_id=project_id,
            name=name,
            asset_ids=asset_ids,
            logical_uri=self._snapshot_uri(company_id, project_id, name),
            metadata=metadata or {},
        )
        saved = self._repository.save_snapshot(snapshot)
        for asset_id in asset_ids:
            asset = self._require_asset(asset_id)
            self._repository.save_asset(
                asset.model_copy(
                    update={
                        "status": InformationAssetStatus.APPROVED,
                        "updated_at": datetime.now(UTC),
                    }
                )
            )
        self._audit_event("nas.snapshot_created", "information_snapshot", saved.snapshot_id)
        return saved

    def list_snapshots(self, company_id: str) -> list[InformationSnapshot]:
        """Return snapshot manifests for one company."""

        self._validate_scope(company_id, None)
        return self._repository.list_snapshots_by_company(company_id)

    def register_backup(
        self,
        company_id: str,
        logical_uri: str,
        project_id: str | None = None,
        snapshot_id: str | None = None,
        checksum_sha256: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> InformationBackup:
        """Register a backup manifest for NAS information."""

        self._validate_scope(company_id, project_id)
        backup = InformationBackup(
            backup_id=f"BKP-{uuid4().hex[:12]}",
            company_id=company_id,
            project_id=project_id,
            snapshot_id=snapshot_id,
            logical_uri=logical_uri,
            checksum_sha256=checksum_sha256,
            metadata=metadata or {},
        )
        saved = self._repository.save_backup(backup)
        self._audit_event("nas.backup_registered", "information_backup", saved.backup_id)
        return saved

    def list_backups(self, company_id: str) -> list[InformationBackup]:
        """Return backup manifests for one company."""

        self._validate_scope(company_id, None)
        return self._repository.list_backups_by_company(company_id)

    def set_permission(
        self,
        asset_id: str,
        principal: str,
        permission: InformationPermission,
    ) -> InformationAsset:
        """Assign a permission to a user, role, or service principal."""

        asset = self._require_asset(asset_id)
        permissions = dict(asset.permissions)
        permissions[principal] = InformationPermission(permission)
        saved = self._repository.save_asset(
            asset.model_copy(update={"permissions": permissions, "updated_at": datetime.now(UTC)})
        )
        self._audit_event("nas.permission_set", "information_asset", asset_id)
        return saved

    def update_metadata(self, asset_id: str, metadata: dict[str, str]) -> InformationAsset:
        """Merge metadata into an information asset."""

        asset = self._require_asset(asset_id)
        merged = {**asset.metadata, **metadata}
        saved = self._repository.save_asset(
            asset.model_copy(update={"metadata": merged, "updated_at": datetime.now(UTC)})
        )
        self._audit_event("nas.metadata_updated", "information_asset", asset_id)
        return saved

    def archive_asset(self, asset_id: str) -> InformationAsset:
        """Archive an information asset without deleting its registry."""

        asset = self._require_asset(asset_id)
        saved = self._repository.save_asset(
            asset.model_copy(
                update={
                    "status": InformationAssetStatus.ARCHIVED,
                    "updated_at": datetime.now(UTC),
                }
            )
        )
        self._audit_event("nas.asset_archived", "information_asset", asset_id)
        return saved

    def _validate_scope(self, company_id: str, project_id: str | None) -> None:
        if not self._companies.exists(company_id):
            raise ValueError(f"Company is not registered: {company_id}")
        if project_id is not None and self._portfolio.get_project_for_company(company_id, project_id) is None:
            raise ValueError(f"Project is not registered for company {company_id}: {project_id}")

    def _require_asset(self, asset_id: str) -> InformationAsset:
        asset = self._repository.get_asset(asset_id)
        if asset is None:
            raise ValueError(f"Information asset is not registered: {asset_id}")
        return asset

    @staticmethod
    def _snapshot_uri(company_id: str, project_id: str | None, name: str) -> str:
        normalized = name.lower().replace(" ", "-")
        scope = project_id or "corporate"
        return f"nas://{company_id}/{scope}/snapshots/{normalized}"

    def _audit_event(self, action: str, entity_type: str, entity_id: str) -> None:
        if self._audit is None:
            return
        self._audit.save(
            AuditEvent(
                actor="system",
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                detail=f"{entity_type} {entity_id} changed.",
            )
        )
