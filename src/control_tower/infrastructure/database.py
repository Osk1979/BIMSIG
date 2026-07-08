"""SQLAlchemy database bootstrap for Corporate Control Tower REV12.

ADR references:
- ADR-0005: Persistence strategy.
- ADR-0013: Database schema and migrations.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, create_engine, func, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from control_tower.domain.audit import AuditEvent
from control_tower.domain.enterprise import (
    Company,
    CompanyLicense,
    CompanyMembership,
    CompanyStatus,
    LicensePlan,
    LicenseStatus,
    MembershipStatus,
    User,
    UserRole,
    UserStatus,
)
from control_tower.domain.nas import (
    InformationAsset,
    InformationAssetStatus,
    InformationAssetType,
    InformationBackup,
    InformationPermission,
    InformationSnapshot,
    InformationVersion,
)
from control_tower.domain.portfolio import PortfolioProject, ProjectStatus
from control_tower.domain.provisioning import ProvisioningOperation, ProvisioningRequest, ProvisioningStatus, ProvisioningStep


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM mappings."""


class CompanyRecord(Base):
    """Persistent enterprise company row."""

    __tablename__ = "companies"

    company_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    tax_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, company: Company) -> "CompanyRecord":
        now = datetime.now(UTC)
        return cls(
            company_id=company.company_id,
            legal_name=company.legal_name,
            display_name=company.display_name,
            tax_id=company.tax_id,
            status=company.status.value,
            created_at=now,
            updated_at=now,
        )

    def update_from_domain(self, company: Company) -> None:
        self.legal_name = company.legal_name
        self.display_name = company.display_name
        self.tax_id = company.tax_id
        self.status = company.status.value
        self.updated_at = datetime.now(UTC)

    def to_domain(self) -> Company:
        return Company(
            company_id=self.company_id,
            legal_name=self.legal_name,
            display_name=self.display_name,
            tax_id=self.tax_id,
            status=CompanyStatus(self.status),
        )


class UserRecord(Base):
    """Persistent platform user row."""

    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    identity_provider_subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, user: User) -> "UserRecord":
        now = datetime.now(UTC)
        return cls(
            user_id=user.user_id,
            email=user.email,
            display_name=user.display_name,
            identity_provider_subject=user.identity_provider_subject,
            status=user.status.value,
            created_at=now,
            updated_at=now,
        )

    def update_from_domain(self, user: User) -> None:
        self.email = user.email
        self.display_name = user.display_name
        self.identity_provider_subject = user.identity_provider_subject
        self.status = user.status.value
        self.updated_at = datetime.now(UTC)

    def to_domain(self) -> User:
        return User(
            user_id=self.user_id,
            email=self.email,
            display_name=self.display_name,
            identity_provider_subject=self.identity_provider_subject,
            status=UserStatus(self.status),
        )


class CompanyMembershipRecord(Base):
    """Persistent company membership row."""

    __tablename__ = "company_memberships"

    membership_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(80), ForeignKey("users.user_id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, membership: CompanyMembership) -> "CompanyMembershipRecord":
        now = datetime.now(UTC)
        return cls(
            membership_id=membership.membership_id,
            company_id=membership.company_id,
            user_id=membership.user_id,
            role=membership.role.value,
            status=membership.status.value,
            created_at=now,
            updated_at=now,
        )

    def update_from_domain(self, membership: CompanyMembership) -> None:
        self.company_id = membership.company_id
        self.user_id = membership.user_id
        self.role = membership.role.value
        self.status = membership.status.value
        self.updated_at = datetime.now(UTC)

    def to_domain(self) -> CompanyMembership:
        return CompanyMembership(
            membership_id=self.membership_id,
            company_id=self.company_id,
            user_id=self.user_id,
            role=UserRole(self.role),
            status=MembershipStatus(self.status),
        )


class LicensePlanRecord(Base):
    """Persistent license plan row."""

    __tablename__ = "license_plans"

    plan_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    max_users: Mapped[int] = mapped_column(Integer, nullable=False)
    max_projects: Mapped[int] = mapped_column(Integer, nullable=False)
    max_websig_instances: Mapped[int] = mapped_column(Integer, nullable=False)
    enabled_modules: Mapped[str] = mapped_column(String(1000), nullable=False)
    ai_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reporting_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)

    @classmethod
    def from_domain(cls, plan: LicensePlan) -> "LicensePlanRecord":
        return cls(**plan.model_dump())

    def update_from_domain(self, plan: LicensePlan) -> None:
        self.name = plan.name
        self.max_users = plan.max_users
        self.max_projects = plan.max_projects
        self.max_websig_instances = plan.max_websig_instances
        self.enabled_modules = plan.enabled_modules
        self.ai_enabled = plan.ai_enabled
        self.reporting_enabled = plan.reporting_enabled

    def to_domain(self) -> LicensePlan:
        return LicensePlan(
            plan_id=self.plan_id,
            name=self.name,
            max_users=self.max_users,
            max_projects=self.max_projects,
            max_websig_instances=self.max_websig_instances,
            enabled_modules=self.enabled_modules,
            ai_enabled=self.ai_enabled,
            reporting_enabled=self.reporting_enabled,
        )


class CompanyLicenseRecord(Base):
    """Persistent company license assignment row."""

    __tablename__ = "company_licenses"

    company_license_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String(80), ForeignKey("license_plans.plan_id"), nullable=False)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(80), nullable=False)

    @classmethod
    def from_domain(cls, license_assignment: CompanyLicense) -> "CompanyLicenseRecord":
        return cls(
            company_license_id=license_assignment.company_license_id,
            company_id=license_assignment.company_id,
            plan_id=license_assignment.plan_id,
            valid_from=license_assignment.valid_from,
            valid_to=license_assignment.valid_to,
            status=license_assignment.status.value,
        )

    def update_from_domain(self, license_assignment: CompanyLicense) -> None:
        self.company_id = license_assignment.company_id
        self.plan_id = license_assignment.plan_id
        self.valid_from = license_assignment.valid_from
        self.valid_to = license_assignment.valid_to
        self.status = license_assignment.status.value

    def to_domain(self) -> CompanyLicense:
        return CompanyLicense(
            company_license_id=self.company_license_id,
            company_id=self.company_id,
            plan_id=self.plan_id,
            valid_from=self.valid_from,
            valid_to=self.valid_to,
            status=LicenseStatus(self.status),
        )


class PortfolioProjectRecord(Base):
    """Persistent portfolio project row."""

    __tablename__ = "portfolio_projects"

    project_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cui: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, project: PortfolioProject) -> "PortfolioProjectRecord":
        """Create a database record from a domain project."""

        now = datetime.now(UTC)
        return cls(
            project_id=project.project_id,
            company_id=project.company_id,
            name=project.name,
            cui=project.cui,
            status=project.status.value,
            created_at=now,
            updated_at=now,
        )

    def update_from_domain(self, project: PortfolioProject) -> None:
        """Apply domain values to an existing database record."""

        self.name = project.name
        self.company_id = project.company_id
        self.cui = project.cui
        self.status = project.status.value
        self.updated_at = datetime.now(UTC)

    def to_domain(self) -> PortfolioProject:
        """Convert the database record to a domain project."""

        return PortfolioProject(
            project_id=self.project_id,
            company_id=self.company_id,
            name=self.name,
            cui=self.cui,
            status=ProjectStatus(self.status),
        )


class ProvisioningRequestRecord(Base):
    """Persistent WEB SIG provisioning request row."""

    __tablename__ = "provisioning_requests"

    request_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str | None] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=True, index=True)
    project_id: Mapped[str] = mapped_column(
        String(80),
        ForeignKey("portfolio_projects.project_id"),
        nullable=False,
        index=True,
    )
    target_revision: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    operation: Mapped[str] = mapped_column(String(80), nullable=False)
    steps_document: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, request: ProvisioningRequest) -> "ProvisioningRequestRecord":
        """Create a database record from a domain provisioning request."""

        now = datetime.now(UTC)
        return cls(
            request_id=request.request_id,
            company_id=request.company_id,
            project_id=request.project_id,
            target_revision=request.target_revision,
            status=request.status.value,
            operation=request.operation.value,
            steps_document=json.dumps([step.model_dump(mode="json") for step in request.steps]),
            created_at=now,
            updated_at=now,
        )

    def to_domain(self) -> ProvisioningRequest:
        """Convert the database record to a domain provisioning request."""

        return ProvisioningRequest(
            request_id=self.request_id,
            company_id=self.company_id,
            project_id=self.project_id,
            target_revision=self.target_revision,
            status=ProvisioningStatus(self.status),
            operation=ProvisioningOperation(self.operation),
            steps=[ProvisioningStep.model_validate(step) for step in json.loads(self.steps_document)],
        )


class InformationAssetRecord(Base):
    """Persistent Corporate Information Center asset row."""

    __tablename__ = "information_assets"

    asset_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    project_id: Mapped[str | None] = mapped_column(String(80), ForeignKey("portfolio_projects.project_id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    logical_uri: Mapped[str] = mapped_column(String(1000), nullable=False)
    version: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    metadata_document: Mapped[str] = mapped_column(Text, nullable=False)
    permissions_document: Mapped[str] = mapped_column(Text, nullable=False)
    google_drive_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    geoserver_reference: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    postgis_reference: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    docker_reference: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, asset: InformationAsset) -> "InformationAssetRecord":
        now = datetime.now(UTC)
        return cls(
            asset_id=asset.asset_id,
            company_id=asset.company_id,
            project_id=asset.project_id,
            name=asset.name,
            asset_type=asset.asset_type.value,
            logical_uri=asset.logical_uri,
            version=asset.version,
            status=asset.status.value,
            metadata_document=json.dumps(asset.metadata),
            permissions_document=json.dumps({key: value.value for key, value in asset.permissions.items()}),
            google_drive_id=asset.google_drive_id,
            geoserver_reference=asset.geoserver_reference,
            postgis_reference=asset.postgis_reference,
            docker_reference=asset.docker_reference,
            checksum_sha256=asset.checksum_sha256,
            created_at=asset.created_at or now,
            updated_at=asset.updated_at or now,
        )

    def update_from_domain(self, asset: InformationAsset) -> None:
        self.company_id = asset.company_id
        self.project_id = asset.project_id
        self.name = asset.name
        self.asset_type = asset.asset_type.value
        self.logical_uri = asset.logical_uri
        self.version = asset.version
        self.status = asset.status.value
        self.metadata_document = json.dumps(asset.metadata)
        self.permissions_document = json.dumps({key: value.value for key, value in asset.permissions.items()})
        self.google_drive_id = asset.google_drive_id
        self.geoserver_reference = asset.geoserver_reference
        self.postgis_reference = asset.postgis_reference
        self.docker_reference = asset.docker_reference
        self.checksum_sha256 = asset.checksum_sha256
        self.updated_at = asset.updated_at or datetime.now(UTC)

    def to_domain(self) -> InformationAsset:
        return InformationAsset(
            asset_id=self.asset_id,
            company_id=self.company_id,
            project_id=self.project_id,
            name=self.name,
            asset_type=InformationAssetType(self.asset_type),
            logical_uri=self.logical_uri,
            version=self.version,
            status=InformationAssetStatus(self.status),
            metadata=json.loads(self.metadata_document),
            permissions={
                key: InformationPermission(value)
                for key, value in json.loads(self.permissions_document).items()
            },
            google_drive_id=self.google_drive_id,
            geoserver_reference=self.geoserver_reference,
            postgis_reference=self.postgis_reference,
            docker_reference=self.docker_reference,
            checksum_sha256=self.checksum_sha256,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class InformationVersionRecord(Base):
    """Persistent information asset version row."""

    __tablename__ = "information_versions"

    version_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    asset_id: Mapped[str] = mapped_column(String(80), ForeignKey("information_assets.asset_id"), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(80), nullable=False)
    logical_uri: Mapped[str] = mapped_column(String(1000), nullable=False)
    checksum_sha256: Mapped[str | None] = mapped_column(String(128), nullable=True)
    metadata_document: Mapped[str] = mapped_column(Text, nullable=False)

    @classmethod
    def from_domain(cls, version: InformationVersion) -> "InformationVersionRecord":
        return cls(
            version_id=version.version_id,
            asset_id=version.asset_id,
            version=version.version,
            logical_uri=version.logical_uri,
            checksum_sha256=version.checksum_sha256,
            metadata_document=json.dumps(version.metadata),
        )

    def to_domain(self) -> InformationVersion:
        return InformationVersion(
            version_id=self.version_id,
            asset_id=self.asset_id,
            version=self.version,
            logical_uri=self.logical_uri,
            checksum_sha256=self.checksum_sha256,
            metadata=json.loads(self.metadata_document),
        )


class InformationSnapshotRecord(Base):
    """Persistent information snapshot row."""

    __tablename__ = "information_snapshots"

    snapshot_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    project_id: Mapped[str | None] = mapped_column(String(80), ForeignKey("portfolio_projects.project_id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_ids_document: Mapped[str] = mapped_column(Text, nullable=False)
    logical_uri: Mapped[str] = mapped_column(String(1000), nullable=False)
    metadata_document: Mapped[str] = mapped_column(Text, nullable=False)

    @classmethod
    def from_domain(cls, snapshot: InformationSnapshot) -> "InformationSnapshotRecord":
        return cls(
            snapshot_id=snapshot.snapshot_id,
            company_id=snapshot.company_id,
            project_id=snapshot.project_id,
            name=snapshot.name,
            asset_ids_document=json.dumps(snapshot.asset_ids),
            logical_uri=snapshot.logical_uri,
            metadata_document=json.dumps(snapshot.metadata),
        )

    def to_domain(self) -> InformationSnapshot:
        return InformationSnapshot(
            snapshot_id=self.snapshot_id,
            company_id=self.company_id,
            project_id=self.project_id,
            name=self.name,
            asset_ids=json.loads(self.asset_ids_document),
            logical_uri=self.logical_uri,
            metadata=json.loads(self.metadata_document),
        )


class InformationBackupRecord(Base):
    """Persistent information backup row."""

    __tablename__ = "information_backups"

    backup_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    project_id: Mapped[str | None] = mapped_column(String(80), ForeignKey("portfolio_projects.project_id"), nullable=True, index=True)
    snapshot_id: Mapped[str | None] = mapped_column(String(80), ForeignKey("information_snapshots.snapshot_id"), nullable=True)
    logical_uri: Mapped[str] = mapped_column(String(1000), nullable=False)
    checksum_sha256: Mapped[str | None] = mapped_column(String(128), nullable=True)
    metadata_document: Mapped[str] = mapped_column(Text, nullable=False)

    @classmethod
    def from_domain(cls, backup: InformationBackup) -> "InformationBackupRecord":
        return cls(
            backup_id=backup.backup_id,
            company_id=backup.company_id,
            project_id=backup.project_id,
            snapshot_id=backup.snapshot_id,
            logical_uri=backup.logical_uri,
            checksum_sha256=backup.checksum_sha256,
            metadata_document=json.dumps(backup.metadata),
        )

    def to_domain(self) -> InformationBackup:
        return InformationBackup(
            backup_id=self.backup_id,
            company_id=self.company_id,
            project_id=self.project_id,
            snapshot_id=self.snapshot_id,
            logical_uri=self.logical_uri,
            checksum_sha256=self.checksum_sha256,
            metadata=json.loads(self.metadata_document),
        )


class AuditEventRecord(Base):
    """Persistent audit event row."""

    __tablename__ = "audit_events"

    event_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor: Mapped[str] = mapped_column(String(120), nullable=False)
    action: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    detail: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, event: AuditEvent) -> "AuditEventRecord":
        """Create a database record from a domain audit event."""

        return cls(
            actor=event.actor,
            action=event.action,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            detail=event.detail,
            created_at=event.created_at or datetime.now(UTC),
        )

    def to_domain(self) -> AuditEvent:
        """Convert the database record to a domain audit event."""

        return AuditEvent(
            event_id=self.event_id,
            actor=self.actor,
            action=self.action,
            entity_type=self.entity_type,
            entity_id=self.entity_id,
            detail=self.detail,
            created_at=self.created_at,
        )


def create_database_engine(database_url: str) -> Engine:
    """Create a SQLAlchemy engine for the configured database URL."""

    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args, future=True)


def initialize_database(engine: Engine) -> None:
    """Create scaffold tables for local development and CI fallback.

    Production and staging schema changes are owned by Alembic migrations.
    See ADR-0013.
    """

    Base.metadata.create_all(engine)


def check_database(engine: Engine) -> bool:
    """Return whether the configured database responds to a simple query."""

    with engine.connect() as connection:
        connection.execute(text("select 1"))
    return True


class SqlAlchemySessionProvider:
    """Small session factory wrapper used by repository adapters."""

    def __init__(self, engine: Engine) -> None:
        self._session_factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)

    @contextmanager
    def session(self) -> Iterator[Session]:
        """Yield a SQLAlchemy session and commit successful work."""

        db = self._session_factory()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


class SqlAlchemyPortfolioProjectRepository:
    """SQLAlchemy implementation of the portfolio project repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save(self, project: PortfolioProject) -> PortfolioProject:
        """Persist a portfolio project."""

        with self._sessions.session() as db:
            record = db.get(PortfolioProjectRecord, project.project_id)
            if record is None:
                record = PortfolioProjectRecord.from_domain(project)
                db.add(record)
            else:
                record.update_from_domain(project)
            db.flush()
            return record.to_domain()

    def list(self) -> list[PortfolioProject]:
        """Return all persisted portfolio projects."""

        with self._sessions.session() as db:
            records = db.scalars(select(PortfolioProjectRecord).order_by(PortfolioProjectRecord.project_id))
            return [record.to_domain() for record in records]

    def list_by_company(self, company_id: str) -> list[PortfolioProject]:
        """Return projects for one company."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(PortfolioProjectRecord)
                .where(PortfolioProjectRecord.company_id == company_id)
                .order_by(PortfolioProjectRecord.project_id)
            )
            return [record.to_domain() for record in records]

    def get(self, project_id: str) -> PortfolioProject | None:
        """Return one persisted project when it exists."""

        with self._sessions.session() as db:
            record = db.get(PortfolioProjectRecord, project_id)
            return record.to_domain() if record is not None else None

    def get_by_company(self, company_id: str, project_id: str) -> PortfolioProject | None:
        """Return one project inside one company when it exists."""

        with self._sessions.session() as db:
            record = db.get(PortfolioProjectRecord, project_id)
            if record is None or record.company_id != company_id:
                return None
            return record.to_domain()

    def exists(self, project_id: str) -> bool:
        """Return whether a project exists."""

        with self._sessions.session() as db:
            return db.get(PortfolioProjectRecord, project_id) is not None


class SqlAlchemyProvisioningRequestRepository:
    """SQLAlchemy implementation of the provisioning request repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save(self, request: ProvisioningRequest) -> ProvisioningRequest:
        """Persist a WEB SIG provisioning request."""

        with self._sessions.session() as db:
            record = db.get(ProvisioningRequestRecord, request.request_id)
            if record is None:
                record = ProvisioningRequestRecord.from_domain(request)
                db.add(record)
            else:
                record.company_id = request.company_id
                record.project_id = request.project_id
                record.target_revision = request.target_revision
                record.status = request.status.value
                record.operation = request.operation.value
                record.steps_document = json.dumps([step.model_dump(mode="json") for step in request.steps])
                record.updated_at = datetime.now(UTC)
            db.flush()
            return record.to_domain()

    def list(self) -> list[ProvisioningRequest]:
        """Return all persisted WEB SIG provisioning requests."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(ProvisioningRequestRecord).order_by(ProvisioningRequestRecord.created_at)
            )
            return [record.to_domain() for record in records]

    def list_by_company(self, company_id: str) -> list[ProvisioningRequest]:
        """Return persisted WEB SIG provisioning requests for one company."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(ProvisioningRequestRecord)
                .where(ProvisioningRequestRecord.company_id == company_id)
                .order_by(ProvisioningRequestRecord.created_at)
            )
            return [record.to_domain() for record in records]


class SqlAlchemyAuditEventRepository:
    """SQLAlchemy implementation of the audit event repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save(self, event: AuditEvent) -> AuditEvent:
        """Persist an audit event."""

        with self._sessions.session() as db:
            record = AuditEventRecord.from_domain(event)
            db.add(record)
            db.flush()
            return record.to_domain()

    def list(self, limit: int = 100) -> list[AuditEvent]:
        """Return recent audit events."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(AuditEventRecord)
                .order_by(AuditEventRecord.created_at.desc(), AuditEventRecord.event_id.desc())
                .limit(limit)
            )
            return [record.to_domain() for record in records]

    def count(self) -> int:
        """Return total audit events."""

        with self._sessions.session() as db:
            return db.scalar(select(func.count()).select_from(AuditEventRecord)) or 0


class SqlAlchemyCompanyRepository:
    """SQLAlchemy implementation of the company repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save(self, company: Company) -> Company:
        """Persist a company."""

        with self._sessions.session() as db:
            record = db.get(CompanyRecord, company.company_id)
            if record is None:
                record = CompanyRecord.from_domain(company)
                db.add(record)
            else:
                record.update_from_domain(company)
            db.flush()
            return record.to_domain()

    def list(self) -> list[Company]:
        """Return all companies."""

        with self._sessions.session() as db:
            records = db.scalars(select(CompanyRecord).order_by(CompanyRecord.company_id))
            return [record.to_domain() for record in records]

    def get(self, company_id: str) -> Company | None:
        """Return one company when it exists."""

        with self._sessions.session() as db:
            record = db.get(CompanyRecord, company_id)
            return record.to_domain() if record is not None else None


class SqlAlchemyUserRepository:
    """SQLAlchemy implementation of the user repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save(self, user: User) -> User:
        """Persist a user."""

        with self._sessions.session() as db:
            record = db.get(UserRecord, user.user_id)
            if record is None:
                record = UserRecord.from_domain(user)
                db.add(record)
            else:
                record.update_from_domain(user)
            db.flush()
            return record.to_domain()

    def list(self) -> list[User]:
        """Return all users."""

        with self._sessions.session() as db:
            records = db.scalars(select(UserRecord).order_by(UserRecord.user_id))
            return [record.to_domain() for record in records]

    def get(self, user_id: str) -> User | None:
        """Return one user when it exists."""

        with self._sessions.session() as db:
            record = db.get(UserRecord, user_id)
            return record.to_domain() if record is not None else None


class SqlAlchemyCompanyMembershipRepository:
    """SQLAlchemy implementation of the membership repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save(self, membership: CompanyMembership) -> CompanyMembership:
        """Persist a company membership."""

        with self._sessions.session() as db:
            record = db.get(CompanyMembershipRecord, membership.membership_id)
            if record is None:
                record = CompanyMembershipRecord.from_domain(membership)
                db.add(record)
            else:
                record.update_from_domain(membership)
            db.flush()
            return record.to_domain()

    def list_by_company(self, company_id: str) -> list[CompanyMembership]:
        """Return memberships for one company."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(CompanyMembershipRecord)
                .where(CompanyMembershipRecord.company_id == company_id)
                .order_by(CompanyMembershipRecord.membership_id)
            )
            return [record.to_domain() for record in records]


class SqlAlchemyLicensePlanRepository:
    """SQLAlchemy implementation of the license plan repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save(self, plan: LicensePlan) -> LicensePlan:
        """Persist a license plan."""

        with self._sessions.session() as db:
            record = db.get(LicensePlanRecord, plan.plan_id)
            if record is None:
                record = LicensePlanRecord.from_domain(plan)
                db.add(record)
            else:
                record.update_from_domain(plan)
            db.flush()
            return record.to_domain()

    def list(self) -> list[LicensePlan]:
        """Return license plans."""

        with self._sessions.session() as db:
            records = db.scalars(select(LicensePlanRecord).order_by(LicensePlanRecord.plan_id))
            return [record.to_domain() for record in records]

    def get(self, plan_id: str) -> LicensePlan | None:
        """Return one license plan when it exists."""

        with self._sessions.session() as db:
            record = db.get(LicensePlanRecord, plan_id)
            return record.to_domain() if record is not None else None


class SqlAlchemyCompanyLicenseRepository:
    """SQLAlchemy implementation of the company license repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save(self, license_assignment: CompanyLicense) -> CompanyLicense:
        """Persist a company license assignment."""

        with self._sessions.session() as db:
            record = db.get(CompanyLicenseRecord, license_assignment.company_license_id)
            if record is None:
                record = CompanyLicenseRecord.from_domain(license_assignment)
                db.add(record)
            else:
                record.update_from_domain(license_assignment)
            db.flush()
            return record.to_domain()

    def list_by_company(self, company_id: str) -> list[CompanyLicense]:
        """Return company license assignments."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(CompanyLicenseRecord)
                .where(CompanyLicenseRecord.company_id == company_id)
                .order_by(CompanyLicenseRecord.company_license_id)
            )
            return [record.to_domain() for record in records]


class SqlAlchemyInformationAssetRepository:
    """SQLAlchemy implementation of the Corporate Information Center repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save_asset(self, asset: InformationAsset) -> InformationAsset:
        """Persist an information asset."""

        with self._sessions.session() as db:
            record = db.get(InformationAssetRecord, asset.asset_id)
            if record is None:
                record = InformationAssetRecord.from_domain(asset)
                db.add(record)
            else:
                record.update_from_domain(asset)
            db.flush()
            return record.to_domain()

    def list_assets_by_company(self, company_id: str) -> list[InformationAsset]:
        """Return assets for one company."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(InformationAssetRecord)
                .where(InformationAssetRecord.company_id == company_id)
                .order_by(InformationAssetRecord.asset_id)
            )
            return [record.to_domain() for record in records]

    def get_asset(self, asset_id: str) -> InformationAsset | None:
        """Return one asset when it exists."""

        with self._sessions.session() as db:
            record = db.get(InformationAssetRecord, asset_id)
            return record.to_domain() if record is not None else None

    def save_version(self, version: InformationVersion) -> InformationVersion:
        """Persist an information version."""

        with self._sessions.session() as db:
            record = InformationVersionRecord.from_domain(version)
            db.add(record)
            db.flush()
            return record.to_domain()

    def list_versions(self, asset_id: str) -> list[InformationVersion]:
        """Return versions for one asset."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(InformationVersionRecord)
                .where(InformationVersionRecord.asset_id == asset_id)
                .order_by(InformationVersionRecord.version_id)
            )
            return [record.to_domain() for record in records]

    def save_snapshot(self, snapshot: InformationSnapshot) -> InformationSnapshot:
        """Persist an information snapshot."""

        with self._sessions.session() as db:
            record = InformationSnapshotRecord.from_domain(snapshot)
            db.add(record)
            db.flush()
            return record.to_domain()

    def list_snapshots_by_company(self, company_id: str) -> list[InformationSnapshot]:
        """Return snapshots for one company."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(InformationSnapshotRecord)
                .where(InformationSnapshotRecord.company_id == company_id)
                .order_by(InformationSnapshotRecord.snapshot_id)
            )
            return [record.to_domain() for record in records]

    def save_backup(self, backup: InformationBackup) -> InformationBackup:
        """Persist an information backup manifest."""

        with self._sessions.session() as db:
            record = InformationBackupRecord.from_domain(backup)
            db.add(record)
            db.flush()
            return record.to_domain()

    def list_backups_by_company(self, company_id: str) -> list[InformationBackup]:
        """Return backup manifests for one company."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(InformationBackupRecord)
                .where(InformationBackupRecord.company_id == company_id)
                .order_by(InformationBackupRecord.backup_id)
            )
            return [record.to_domain() for record in records]
