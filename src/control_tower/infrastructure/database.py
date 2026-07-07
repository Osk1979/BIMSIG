"""SQLAlchemy database bootstrap for Corporate Control Tower REV12.

ADR references:
- ADR-0005: Persistence strategy.
- ADR-0013: Database schema and migrations.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from control_tower.domain.portfolio import PortfolioProject, ProjectStatus
from control_tower.domain.provisioning import ProvisioningRequest, ProvisioningStatus


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM mappings."""


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
