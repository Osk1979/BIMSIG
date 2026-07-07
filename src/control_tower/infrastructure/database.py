"""SQLAlchemy database bootstrap for Corporate Control Tower REV12.

ADR references:
- ADR-0005: Persistence strategy.
- ADR-0013: Database schema and migrations.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, create_engine, func, select, text
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
from control_tower.domain.portfolio import PortfolioProject, ProjectStatus
from control_tower.domain.provisioning import ProvisioningRequest, ProvisioningStatus


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
            name=project.name,
            cui=project.cui,
            status=project.status.value,
            created_at=now,
            updated_at=now,
        )

    def update_from_domain(self, project: PortfolioProject) -> None:
        """Apply domain values to an existing database record."""

        self.name = project.name
        self.cui = project.cui
        self.status = project.status.value
        self.updated_at = datetime.now(UTC)

    def to_domain(self) -> PortfolioProject:
        """Convert the database record to a domain project."""

        return PortfolioProject(
            project_id=self.project_id,
            name=self.name,
            cui=self.cui,
            status=ProjectStatus(self.status),
        )


class ProvisioningRequestRecord(Base):
    """Persistent WEB SIG provisioning request row."""

    __tablename__ = "provisioning_requests"

    request_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(80),
        ForeignKey("portfolio_projects.project_id"),
        nullable=False,
        index=True,
    )
    target_revision: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, request: ProvisioningRequest) -> "ProvisioningRequestRecord":
        """Create a database record from a domain provisioning request."""

        now = datetime.now(UTC)
        return cls(
            request_id=request.request_id,
            project_id=request.project_id,
            target_revision=request.target_revision,
            status=request.status.value,
            created_at=now,
            updated_at=now,
        )

    def to_domain(self) -> ProvisioningRequest:
        """Convert the database record to a domain provisioning request."""

        return ProvisioningRequest(
            request_id=self.request_id,
            project_id=self.project_id,
            target_revision=self.target_revision,
            status=ProvisioningStatus(self.status),
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

    def get(self, project_id: str) -> PortfolioProject | None:
        """Return one persisted project when it exists."""

        with self._sessions.session() as db:
            record = db.get(PortfolioProjectRecord, project_id)
            return record.to_domain() if record is not None else None

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
            record = ProvisioningRequestRecord.from_domain(request)
            db.add(record)
            db.flush()
            return record.to_domain()

    def list(self) -> list[ProvisioningRequest]:
        """Return all persisted WEB SIG provisioning requests."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(ProvisioningRequestRecord).order_by(ProvisioningRequestRecord.created_at)
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
