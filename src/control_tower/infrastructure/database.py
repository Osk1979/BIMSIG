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
from control_tower.domain.corporate_gis_intelligence import (
    CorporateGisSource,
    CorporateGisSourceStatus,
    CorporateLayer,
    CorporateLayerStatus,
    CorporateLayerType,
    GisDiscipline,
    GisServiceKind,
)
from control_tower.domain.corporate_workflow import (
    CorporateWorkflowInstance,
    CorporateWorkflowStage,
    CorporateWorkflowStatus,
    CorporateWorkflowTransition,
)
from control_tower.domain.enterprise import (
    AuthIdentity,
    AuthProvider,
    Company,
    CompanyLicense,
    CompanyMembership,
    CompanyStatus,
    LicensePlan,
    LicenseStatus,
    MembershipStatus,
    PermissionAction,
    PermissionScope,
    ProjectMembership,
    RolePermission,
    Specialty,
    User,
    UserHistoryEvent,
    UserRole,
    UserSpecialty,
    UserStatus,
)
from control_tower.domain.enterprise_wizard import (
    EnterpriseWizardSession,
    EnterpriseWizardStatus,
    EnterpriseWizardStep,
    EnterpriseWizardStepState,
)
from control_tower.domain.gis import (
    GeoServerDatastore,
    GeoServerLayer,
    GeoServerWorkspace,
    GisResourceStatus,
    PostgisSchema,
    ProjectGisBinding,
)
from control_tower.domain.nas import (
    InformationAsset,
    InformationAssetStatus,
    InformationAssetType,
    InformationBackup,
    InformationCategory,
    InformationPermission,
    InformationSnapshot,
    InformationVersion,
)
from control_tower.domain.portfolio import (
    CorporateCustomer,
    CorporateProgram,
    CustomerStatus,
    PortfolioProject,
    ProgramStatus,
    ProjectLifecycleStage,
    ProjectStatus,
)
from control_tower.domain.provisioning import (
    ProvisioningExecutionMode,
    ProvisioningOperation,
    ProvisioningRequest,
    ProvisioningStatus,
    ProvisioningStep,
)


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


class CorporateCustomerRecord(Base):
    """Persistent corporate portfolio customer row."""

    __tablename__ = "portfolio_customers"

    customer_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    tax_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(80), nullable=False)

    @classmethod
    def from_domain(cls, customer: CorporateCustomer) -> "CorporateCustomerRecord":
        return cls(**customer.model_dump(mode="json"))

    def update_from_domain(self, customer: CorporateCustomer) -> None:
        self.company_id = customer.company_id
        self.legal_name = customer.legal_name
        self.display_name = customer.display_name
        self.tax_id = customer.tax_id
        self.status = customer.status.value

    def to_domain(self) -> CorporateCustomer:
        return CorporateCustomer(
            customer_id=self.customer_id,
            company_id=self.company_id,
            legal_name=self.legal_name,
            display_name=self.display_name,
            tax_id=self.tax_id,
            status=CustomerStatus(self.status),
        )


class CorporateProgramRecord(Base):
    """Persistent corporate portfolio program row."""

    __tablename__ = "portfolio_programs"

    program_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    customer_id: Mapped[str | None] = mapped_column(
        String(80),
        ForeignKey("portfolio_customers.customer_id"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)

    @classmethod
    def from_domain(cls, program: CorporateProgram) -> "CorporateProgramRecord":
        return cls(**program.model_dump(mode="json"))

    def update_from_domain(self, program: CorporateProgram) -> None:
        self.company_id = program.company_id
        self.customer_id = program.customer_id
        self.name = program.name
        self.status = program.status.value

    def to_domain(self) -> CorporateProgram:
        return CorporateProgram(
            program_id=self.program_id,
            company_id=self.company_id,
            customer_id=self.customer_id,
            name=self.name,
            status=ProgramStatus(self.status),
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


class SpecialtyRecord(Base):
    """Persistent corporate specialty row."""

    __tablename__ = "specialties"

    specialty_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    @classmethod
    def from_domain(cls, specialty: Specialty) -> "SpecialtyRecord":
        return cls(**specialty.model_dump())

    def update_from_domain(self, specialty: Specialty) -> None:
        self.name = specialty.name
        self.description = specialty.description

    def to_domain(self) -> Specialty:
        return Specialty(
            specialty_id=self.specialty_id,
            name=self.name,
            description=self.description,
        )


class UserSpecialtyRecord(Base):
    """Persistent user specialty assignment row."""

    __tablename__ = "user_specialties"

    user_specialty_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(80), ForeignKey("users.user_id"), nullable=False, index=True)
    specialty_id: Mapped[str] = mapped_column(String(80), ForeignKey("specialties.specialty_id"), nullable=False, index=True)

    @classmethod
    def from_domain(cls, assignment: UserSpecialty) -> "UserSpecialtyRecord":
        return cls(**assignment.model_dump())

    def to_domain(self) -> UserSpecialty:
        return UserSpecialty(
            user_specialty_id=self.user_specialty_id,
            user_id=self.user_id,
            specialty_id=self.specialty_id,
        )


class ProjectMembershipRecord(Base):
    """Persistent project membership row."""

    __tablename__ = "project_memberships"

    project_membership_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(80), ForeignKey("portfolio_projects.project_id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(80), ForeignKey("users.user_id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)

    @classmethod
    def from_domain(cls, membership: ProjectMembership) -> "ProjectMembershipRecord":
        return cls(
            project_membership_id=membership.project_membership_id,
            company_id=membership.company_id,
            project_id=membership.project_id,
            user_id=membership.user_id,
            role=membership.role.value,
            status=membership.status.value,
        )

    def update_from_domain(self, membership: ProjectMembership) -> None:
        self.company_id = membership.company_id
        self.project_id = membership.project_id
        self.user_id = membership.user_id
        self.role = membership.role.value
        self.status = membership.status.value

    def to_domain(self) -> ProjectMembership:
        return ProjectMembership(
            project_membership_id=self.project_membership_id,
            company_id=self.company_id,
            project_id=self.project_id,
            user_id=self.user_id,
            role=UserRole(self.role),
            status=MembershipStatus(self.status),
        )


class RolePermissionRecord(Base):
    """Persistent role permission row."""

    __tablename__ = "role_permissions"

    role_permission_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    role: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(80), nullable=False)
    action: Mapped[str] = mapped_column(String(80), nullable=False)

    @classmethod
    def from_domain(cls, permission: RolePermission) -> "RolePermissionRecord":
        return cls(
            role_permission_id=permission.role_permission_id,
            role=permission.role.value,
            scope=permission.scope.value,
            action=permission.action.value,
        )

    def to_domain(self) -> RolePermission:
        return RolePermission(
            role_permission_id=self.role_permission_id,
            role=UserRole(self.role),
            scope=PermissionScope(self.scope),
            action=PermissionAction(self.action),
        )


class AuthIdentityRecord(Base):
    """Persistent authentication identity row."""

    __tablename__ = "auth_identities"

    identity_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(80), ForeignKey("users.user_id"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)

    @classmethod
    def from_domain(cls, identity: AuthIdentity) -> "AuthIdentityRecord":
        return cls(
            identity_id=identity.identity_id,
            user_id=identity.user_id,
            provider=identity.provider.value,
            subject=identity.subject,
            email=identity.email,
            status=identity.status.value,
        )

    def update_from_domain(self, identity: AuthIdentity) -> None:
        self.user_id = identity.user_id
        self.provider = identity.provider.value
        self.subject = identity.subject
        self.email = identity.email
        self.status = identity.status.value

    def to_domain(self) -> AuthIdentity:
        return AuthIdentity(
            identity_id=self.identity_id,
            user_id=self.user_id,
            provider=AuthProvider(self.provider),
            subject=self.subject,
            email=self.email,
            status=UserStatus(self.status),
        )


class UserHistoryEventRecord(Base):
    """Persistent user security history row."""

    __tablename__ = "user_history_events"

    history_id: Mapped[str] = mapped_column(String(120), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(80), ForeignKey("users.user_id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    detail: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    company_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    project_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)

    @classmethod
    def from_domain(cls, event: UserHistoryEvent) -> "UserHistoryEventRecord":
        return cls(**event.model_dump())

    def to_domain(self) -> UserHistoryEvent:
        return UserHistoryEvent(
            history_id=self.history_id,
            user_id=self.user_id,
            action=self.action,
            detail=self.detail,
            company_id=self.company_id,
            project_id=self.project_id,
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
    customer_id: Mapped[str | None] = mapped_column(
        String(80),
        ForeignKey("portfolio_customers.customer_id"),
        nullable=True,
        index=True,
    )
    program_id: Mapped[str | None] = mapped_column(
        String(80),
        ForeignKey("portfolio_programs.program_id"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    lifecycle_stage: Mapped[str] = mapped_column(String(80), nullable=False)
    websig_instance_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    websig_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    nas_root_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    gis_binding_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    google_drive_folder_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
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
            customer_id=project.customer_id,
            program_id=project.program_id,
            status=project.status.value,
            lifecycle_stage=project.lifecycle_stage.value,
            websig_instance_id=project.websig_instance_id,
            websig_url=project.websig_url,
            nas_root_uri=project.nas_root_uri,
            gis_binding_id=project.gis_binding_id,
            google_drive_folder_id=project.google_drive_folder_id,
            created_at=now,
            updated_at=now,
        )

    def update_from_domain(self, project: PortfolioProject) -> None:
        """Apply domain values to an existing database record."""

        self.name = project.name
        self.company_id = project.company_id
        self.cui = project.cui
        self.customer_id = project.customer_id
        self.program_id = project.program_id
        self.status = project.status.value
        self.lifecycle_stage = project.lifecycle_stage.value
        self.websig_instance_id = project.websig_instance_id
        self.websig_url = project.websig_url
        self.nas_root_uri = project.nas_root_uri
        self.gis_binding_id = project.gis_binding_id
        self.google_drive_folder_id = project.google_drive_folder_id
        self.updated_at = datetime.now(UTC)

    def to_domain(self) -> PortfolioProject:
        """Convert the database record to a domain project."""

        return PortfolioProject(
            project_id=self.project_id,
            company_id=self.company_id,
            name=self.name,
            cui=self.cui,
            customer_id=self.customer_id,
            program_id=self.program_id,
            status=ProjectStatus(self.status),
            lifecycle_stage=ProjectLifecycleStage(self.lifecycle_stage),
            websig_instance_id=self.websig_instance_id,
            websig_url=self.websig_url,
            nas_root_uri=self.nas_root_uri,
            gis_binding_id=self.gis_binding_id,
            google_drive_folder_id=self.google_drive_folder_id,
        )


class PostgisSchemaRecord(Base):
    """Persistent corporate PostGIS schema reference."""

    __tablename__ = "gis_postgis_schemas"

    schema_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(80), ForeignKey("portfolio_projects.project_id"), nullable=False, index=True)
    schema_name: Mapped[str] = mapped_column(String(160), nullable=False)
    database_ref: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)

    @classmethod
    def from_domain(cls, schema: PostgisSchema) -> "PostgisSchemaRecord":
        return cls(**schema.model_dump(mode="json"))

    def update_from_domain(self, schema: PostgisSchema) -> None:
        self.company_id = schema.company_id
        self.project_id = schema.project_id
        self.schema_name = schema.schema_name
        self.database_ref = schema.database_ref
        self.status = schema.status.value

    def to_domain(self) -> PostgisSchema:
        return PostgisSchema(
            schema_id=self.schema_id,
            company_id=self.company_id,
            project_id=self.project_id,
            schema_name=self.schema_name,
            database_ref=self.database_ref,
            status=GisResourceStatus(self.status),
        )


class GeoServerWorkspaceRecord(Base):
    """Persistent corporate GeoServer workspace reference."""

    __tablename__ = "gis_geoserver_workspaces"

    workspace_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(80), ForeignKey("portfolio_projects.project_id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    geoserver_url: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)

    @classmethod
    def from_domain(cls, workspace: GeoServerWorkspace) -> "GeoServerWorkspaceRecord":
        return cls(**workspace.model_dump(mode="json"))

    def update_from_domain(self, workspace: GeoServerWorkspace) -> None:
        self.company_id = workspace.company_id
        self.project_id = workspace.project_id
        self.name = workspace.name
        self.geoserver_url = workspace.geoserver_url
        self.status = workspace.status.value

    def to_domain(self) -> GeoServerWorkspace:
        return GeoServerWorkspace(
            workspace_id=self.workspace_id,
            company_id=self.company_id,
            project_id=self.project_id,
            name=self.name,
            geoserver_url=self.geoserver_url,
            status=GisResourceStatus(self.status),
        )


class GeoServerDatastoreRecord(Base):
    """Persistent corporate GeoServer datastore reference."""

    __tablename__ = "gis_geoserver_datastores"

    datastore_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(80), ForeignKey("portfolio_projects.project_id"), nullable=False, index=True)
    workspace_id: Mapped[str] = mapped_column(String(80), ForeignKey("gis_geoserver_workspaces.workspace_id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    postgis_schema_id: Mapped[str] = mapped_column(String(80), ForeignKey("gis_postgis_schemas.schema_id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(80), nullable=False)

    @classmethod
    def from_domain(cls, datastore: GeoServerDatastore) -> "GeoServerDatastoreRecord":
        return cls(**datastore.model_dump(mode="json"))

    def update_from_domain(self, datastore: GeoServerDatastore) -> None:
        self.company_id = datastore.company_id
        self.project_id = datastore.project_id
        self.workspace_id = datastore.workspace_id
        self.name = datastore.name
        self.postgis_schema_id = datastore.postgis_schema_id
        self.status = datastore.status.value

    def to_domain(self) -> GeoServerDatastore:
        return GeoServerDatastore(
            datastore_id=self.datastore_id,
            company_id=self.company_id,
            project_id=self.project_id,
            workspace_id=self.workspace_id,
            name=self.name,
            postgis_schema_id=self.postgis_schema_id,
            status=GisResourceStatus(self.status),
        )


class GeoServerLayerRecord(Base):
    """Persistent corporate GeoServer layer reference."""

    __tablename__ = "gis_geoserver_layers"

    layer_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(80), ForeignKey("portfolio_projects.project_id"), nullable=False, index=True)
    workspace_id: Mapped[str] = mapped_column(String(80), ForeignKey("gis_geoserver_workspaces.workspace_id"), nullable=False, index=True)
    datastore_id: Mapped[str] = mapped_column(String(80), ForeignKey("gis_geoserver_datastores.datastore_id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    wms_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    wfs_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(80), nullable=False)

    @classmethod
    def from_domain(cls, layer: GeoServerLayer) -> "GeoServerLayerRecord":
        return cls(**layer.model_dump(mode="json"))

    def update_from_domain(self, layer: GeoServerLayer) -> None:
        self.company_id = layer.company_id
        self.project_id = layer.project_id
        self.workspace_id = layer.workspace_id
        self.datastore_id = layer.datastore_id
        self.name = layer.name
        self.title = layer.title
        self.wms_url = layer.wms_url
        self.wfs_url = layer.wfs_url
        self.status = layer.status.value

    def to_domain(self) -> GeoServerLayer:
        return GeoServerLayer(
            layer_id=self.layer_id,
            company_id=self.company_id,
            project_id=self.project_id,
            workspace_id=self.workspace_id,
            datastore_id=self.datastore_id,
            name=self.name,
            title=self.title,
            wms_url=self.wms_url,
            wfs_url=self.wfs_url,
            status=GisResourceStatus(self.status),
        )


class ProjectGisBindingRecord(Base):
    """Persistent project GIS infrastructure binding."""

    __tablename__ = "gis_project_bindings"

    binding_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(80), ForeignKey("portfolio_projects.project_id"), nullable=False, unique=True, index=True)
    postgis_schema_id: Mapped[str] = mapped_column(String(80), ForeignKey("gis_postgis_schemas.schema_id"), nullable=False)
    geoserver_workspace_id: Mapped[str] = mapped_column(String(80), ForeignKey("gis_geoserver_workspaces.workspace_id"), nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)

    @classmethod
    def from_domain(cls, binding: ProjectGisBinding) -> "ProjectGisBindingRecord":
        return cls(**binding.model_dump(mode="json"))

    def update_from_domain(self, binding: ProjectGisBinding) -> None:
        self.company_id = binding.company_id
        self.project_id = binding.project_id
        self.postgis_schema_id = binding.postgis_schema_id
        self.geoserver_workspace_id = binding.geoserver_workspace_id
        self.status = binding.status.value

    def to_domain(self) -> ProjectGisBinding:
        return ProjectGisBinding(
            binding_id=self.binding_id,
            company_id=self.company_id,
            project_id=self.project_id,
            postgis_schema_id=self.postgis_schema_id,
            geoserver_workspace_id=self.geoserver_workspace_id,
            status=GisResourceStatus(self.status),
        )


class CorporateGisSourceRecord(Base):
    """Persistent Corporate GIS Intelligence source reference."""

    __tablename__ = "corporate_gis_sources"

    source_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(80), ForeignKey("portfolio_projects.project_id"), nullable=False, index=True)
    program_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    websig_instance_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    service_kind: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    service_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    discipline: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    layer_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    updated_on: Mapped[date] = mapped_column(Date, nullable=False)
    metadata_document: Mapped[str] = mapped_column(Text, nullable=False)

    @classmethod
    def from_domain(cls, source: CorporateGisSource) -> "CorporateGisSourceRecord":
        return cls(
            source_id=source.source_id,
            company_id=source.company_id,
            project_id=source.project_id,
            program_id=source.program_id,
            websig_instance_id=source.websig_instance_id,
            service_kind=source.service_kind.value,
            service_url=source.service_url,
            discipline=source.discipline.value,
            layer_type=source.layer_type.value,
            status=source.status.value,
            updated_on=source.updated_on,
            metadata_document=json.dumps(source.metadata),
        )

    def update_from_domain(self, source: CorporateGisSource) -> None:
        self.company_id = source.company_id
        self.project_id = source.project_id
        self.program_id = source.program_id
        self.websig_instance_id = source.websig_instance_id
        self.service_kind = source.service_kind.value
        self.service_url = source.service_url
        self.discipline = source.discipline.value
        self.layer_type = source.layer_type.value
        self.status = source.status.value
        self.updated_on = source.updated_on
        self.metadata_document = json.dumps(source.metadata)

    def to_domain(self) -> CorporateGisSource:
        return CorporateGisSource(
            source_id=self.source_id,
            company_id=self.company_id,
            project_id=self.project_id,
            program_id=self.program_id,
            websig_instance_id=self.websig_instance_id,
            service_kind=GisServiceKind(self.service_kind),
            service_url=self.service_url,
            discipline=GisDiscipline(self.discipline),
            layer_type=CorporateLayerType(self.layer_type),
            status=CorporateGisSourceStatus(self.status),
            updated_on=self.updated_on,
            metadata=json.loads(self.metadata_document),
        )


class CorporateLayerRecord(Base):
    """Persistent Corporate GIS Intelligence layer reference."""

    __tablename__ = "corporate_gis_layers"

    layer_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(80), ForeignKey("corporate_gis_sources.source_id"), nullable=False, index=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(80), ForeignKey("portfolio_projects.project_id"), nullable=False, index=True)
    program_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    layer_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    discipline: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    spatial_indicator: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    indicator_value: Mapped[str] = mapped_column(String(80), nullable=False)
    updated_on: Mapped[date] = mapped_column(Date, nullable=False)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    risk_level: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    metadata_document: Mapped[str] = mapped_column(Text, nullable=False)

    @classmethod
    def from_domain(cls, layer: CorporateLayer) -> "CorporateLayerRecord":
        return cls(
            layer_id=layer.layer_id,
            source_id=layer.source_id,
            company_id=layer.company_id,
            project_id=layer.project_id,
            program_id=layer.program_id,
            name=layer.name,
            layer_type=layer.layer_type.value,
            discipline=layer.discipline.value,
            status=layer.status.value,
            spatial_indicator=layer.spatial_indicator,
            indicator_value=str(layer.indicator_value),
            updated_on=layer.updated_on,
            region=layer.region,
            risk_level=layer.risk_level,
            metadata_document=json.dumps(layer.metadata),
        )

    def update_from_domain(self, layer: CorporateLayer) -> None:
        self.source_id = layer.source_id
        self.company_id = layer.company_id
        self.project_id = layer.project_id
        self.program_id = layer.program_id
        self.name = layer.name
        self.layer_type = layer.layer_type.value
        self.discipline = layer.discipline.value
        self.status = layer.status.value
        self.spatial_indicator = layer.spatial_indicator
        self.indicator_value = str(layer.indicator_value)
        self.updated_on = layer.updated_on
        self.region = layer.region
        self.risk_level = layer.risk_level
        self.metadata_document = json.dumps(layer.metadata)

    def to_domain(self) -> CorporateLayer:
        return CorporateLayer(
            layer_id=self.layer_id,
            source_id=self.source_id,
            company_id=self.company_id,
            project_id=self.project_id,
            program_id=self.program_id,
            name=self.name,
            layer_type=CorporateLayerType(self.layer_type),
            discipline=GisDiscipline(self.discipline),
            status=CorporateLayerStatus(self.status),
            spatial_indicator=self.spatial_indicator,
            indicator_value=float(self.indicator_value),
            updated_on=self.updated_on,
            region=self.region,
            risk_level=self.risk_level,
            metadata=json.loads(self.metadata_document),
        )


class CorporateWorkflowRecord(Base):
    """Persistent Corporate Workflow Engine instance."""

    __tablename__ = "corporate_workflows"

    workflow_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    project_id: Mapped[str | None] = mapped_column(String(80), ForeignKey("portfolio_projects.project_id"), nullable=True, index=True)
    program_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    current_stage: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    completed_stages_document: Mapped[str] = mapped_column(Text, nullable=False)
    rollback_available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_by: Mapped[str] = mapped_column(String(160), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(160), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, workflow: CorporateWorkflowInstance) -> "CorporateWorkflowRecord":
        now = datetime.now(UTC)
        return cls(
            workflow_id=workflow.workflow_id,
            company_id=workflow.company_id,
            project_id=workflow.project_id,
            program_id=workflow.program_id,
            current_stage=workflow.current_stage.value,
            status=workflow.status.value,
            completed_stages_document=json.dumps([stage.value for stage in workflow.completed_stages]),
            rollback_available=workflow.rollback_available,
            created_by=workflow.created_by,
            updated_by=workflow.updated_by,
            created_at=workflow.created_at or now,
            updated_at=workflow.updated_at or now,
        )

    def update_from_domain(self, workflow: CorporateWorkflowInstance) -> None:
        self.company_id = workflow.company_id
        self.project_id = workflow.project_id
        self.program_id = workflow.program_id
        self.current_stage = workflow.current_stage.value
        self.status = workflow.status.value
        self.completed_stages_document = json.dumps([stage.value for stage in workflow.completed_stages])
        self.rollback_available = workflow.rollback_available
        self.updated_by = workflow.updated_by
        self.updated_at = datetime.now(UTC)

    def to_domain(self) -> CorporateWorkflowInstance:
        return CorporateWorkflowInstance(
            workflow_id=self.workflow_id,
            company_id=self.company_id,
            project_id=self.project_id,
            program_id=self.program_id,
            current_stage=CorporateWorkflowStage(self.current_stage),
            status=CorporateWorkflowStatus(self.status),
            completed_stages=[
                CorporateWorkflowStage(stage)
                for stage in json.loads(self.completed_stages_document)
            ],
            rollback_available=self.rollback_available,
            created_by=self.created_by,
            updated_by=self.updated_by,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class CorporateWorkflowTransitionRecord(Base):
    """Persistent auditable Corporate Workflow Engine transition."""

    __tablename__ = "corporate_workflow_transitions"

    transition_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    workflow_id: Mapped[str] = mapped_column(String(80), ForeignKey("corporate_workflows.workflow_id"), nullable=False, index=True)
    company_id: Mapped[str] = mapped_column(String(80), ForeignKey("companies.company_id"), nullable=False, index=True)
    project_id: Mapped[str | None] = mapped_column(String(80), ForeignKey("portfolio_projects.project_id"), nullable=True, index=True)
    from_stage: Mapped[str | None] = mapped_column(String(80), nullable=True)
    to_stage: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    actor: Mapped[str] = mapped_column(String(160), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    rollback: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    rollback_of: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, transition: CorporateWorkflowTransition) -> "CorporateWorkflowTransitionRecord":
        return cls(
            transition_id=transition.transition_id,
            workflow_id=transition.workflow_id,
            company_id=transition.company_id,
            project_id=transition.project_id,
            from_stage=transition.from_stage.value if transition.from_stage is not None else None,
            to_stage=transition.to_stage.value,
            actor=transition.actor,
            reason=transition.reason,
            rollback=transition.rollback,
            rollback_of=transition.rollback_of,
            created_at=transition.created_at or datetime.now(UTC),
        )

    def to_domain(self) -> CorporateWorkflowTransition:
        return CorporateWorkflowTransition(
            transition_id=self.transition_id,
            workflow_id=self.workflow_id,
            company_id=self.company_id,
            project_id=self.project_id,
            from_stage=CorporateWorkflowStage(self.from_stage) if self.from_stage else None,
            to_stage=CorporateWorkflowStage(self.to_stage),
            actor=self.actor,
            reason=self.reason,
            rollback=self.rollback,
            rollback_of=self.rollback_of,
            created_at=self.created_at,
        )


class EnterpriseWizardSessionRecord(Base):
    """Persistent Enterprise Wizard session."""

    __tablename__ = "enterprise_wizard_sessions"

    wizard_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    company_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    project_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    workflow_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    current_step: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    steps_document: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str] = mapped_column(String(160), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(160), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, session: EnterpriseWizardSession) -> "EnterpriseWizardSessionRecord":
        now = datetime.now(UTC)
        return cls(
            wizard_id=session.wizard_id,
            company_id=session.company_id,
            project_id=session.project_id,
            workflow_id=session.workflow_id,
            status=session.status.value,
            current_step=session.current_step.value,
            steps_document=json.dumps([step.model_dump(mode="json") for step in session.steps]),
            created_by=session.created_by,
            updated_by=session.updated_by,
            created_at=session.created_at or now,
            updated_at=session.updated_at or now,
        )

    def update_from_domain(self, session: EnterpriseWizardSession) -> None:
        self.company_id = session.company_id
        self.project_id = session.project_id
        self.workflow_id = session.workflow_id
        self.status = session.status.value
        self.current_step = session.current_step.value
        self.steps_document = json.dumps([step.model_dump(mode="json") for step in session.steps])
        self.updated_by = session.updated_by
        self.updated_at = datetime.now(UTC)

    def to_domain(self) -> EnterpriseWizardSession:
        return EnterpriseWizardSession(
            wizard_id=self.wizard_id,
            company_id=self.company_id,
            project_id=self.project_id,
            workflow_id=self.workflow_id,
            status=EnterpriseWizardStatus(self.status),
            current_step=EnterpriseWizardStep(self.current_step),
            steps=[
                EnterpriseWizardStepState.model_validate(step)
                for step in json.loads(self.steps_document)
            ],
            created_by=self.created_by,
            updated_by=self.updated_by,
            created_at=self.created_at,
            updated_at=self.updated_at,
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
    execution_mode: Mapped[str] = mapped_column(String(80), nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String(160), nullable=True)
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
            execution_mode=request.execution_mode.value,
            approved_by=request.approved_by,
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
            execution_mode=ProvisioningExecutionMode(self.execution_mode),
            approved_by=self.approved_by,
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
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
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
            category=asset.category.value,
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
        self.category = asset.category.value
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
            category=InformationCategory(self.category),
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


class SqlAlchemyCorporateCustomerRepository:
    """SQLAlchemy implementation of the portfolio customer repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save(self, customer: CorporateCustomer) -> CorporateCustomer:
        """Persist a corporate customer."""

        with self._sessions.session() as db:
            record = db.get(CorporateCustomerRecord, customer.customer_id)
            if record is None:
                record = CorporateCustomerRecord.from_domain(customer)
                db.add(record)
            else:
                record.update_from_domain(customer)
            db.flush()
            return record.to_domain()

    def list_by_company(self, company_id: str) -> list[CorporateCustomer]:
        """Return customers for one company."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(CorporateCustomerRecord)
                .where(CorporateCustomerRecord.company_id == company_id)
                .order_by(CorporateCustomerRecord.customer_id)
            )
            return [record.to_domain() for record in records]

    def get(self, customer_id: str) -> CorporateCustomer | None:
        """Return one customer when it exists."""

        with self._sessions.session() as db:
            record = db.get(CorporateCustomerRecord, customer_id)
            return record.to_domain() if record is not None else None


class SqlAlchemyCorporateProgramRepository:
    """SQLAlchemy implementation of the portfolio program repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save(self, program: CorporateProgram) -> CorporateProgram:
        """Persist a corporate program."""

        with self._sessions.session() as db:
            record = db.get(CorporateProgramRecord, program.program_id)
            if record is None:
                record = CorporateProgramRecord.from_domain(program)
                db.add(record)
            else:
                record.update_from_domain(program)
            db.flush()
            return record.to_domain()

    def list_by_company(self, company_id: str) -> list[CorporateProgram]:
        """Return programs for one company."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(CorporateProgramRecord)
                .where(CorporateProgramRecord.company_id == company_id)
                .order_by(CorporateProgramRecord.program_id)
            )
            return [record.to_domain() for record in records]

    def get(self, program_id: str) -> CorporateProgram | None:
        """Return one program when it exists."""

        with self._sessions.session() as db:
            record = db.get(CorporateProgramRecord, program_id)
            return record.to_domain() if record is not None else None


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
                record.execution_mode = request.execution_mode.value
                record.approved_by = request.approved_by
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


class SqlAlchemySpecialtyRepository:
    """SQLAlchemy implementation of the specialty repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save(self, specialty: Specialty) -> Specialty:
        """Persist a specialty."""

        with self._sessions.session() as db:
            record = db.get(SpecialtyRecord, specialty.specialty_id)
            if record is None:
                record = SpecialtyRecord.from_domain(specialty)
                db.add(record)
            else:
                record.update_from_domain(specialty)
            db.flush()
            return record.to_domain()

    def list(self) -> list[Specialty]:
        """Return specialties."""

        with self._sessions.session() as db:
            records = db.scalars(select(SpecialtyRecord).order_by(SpecialtyRecord.specialty_id))
            return [record.to_domain() for record in records]

    def get(self, specialty_id: str) -> Specialty | None:
        """Return one specialty."""

        with self._sessions.session() as db:
            record = db.get(SpecialtyRecord, specialty_id)
            return record.to_domain() if record is not None else None


class SqlAlchemyUserSpecialtyRepository:
    """SQLAlchemy implementation of the user specialty repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save(self, assignment: UserSpecialty) -> UserSpecialty:
        """Persist a user specialty assignment."""

        with self._sessions.session() as db:
            record = db.get(UserSpecialtyRecord, assignment.user_specialty_id)
            if record is None:
                record = UserSpecialtyRecord.from_domain(assignment)
                db.add(record)
            db.flush()
            return record.to_domain()

    def list_by_user(self, user_id: str) -> list[UserSpecialty]:
        """Return user specialty assignments."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(UserSpecialtyRecord)
                .where(UserSpecialtyRecord.user_id == user_id)
                .order_by(UserSpecialtyRecord.user_specialty_id)
            )
            return [record.to_domain() for record in records]


class SqlAlchemyProjectMembershipRepository:
    """SQLAlchemy implementation of the project membership repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save(self, membership: ProjectMembership) -> ProjectMembership:
        """Persist a project membership."""

        with self._sessions.session() as db:
            record = db.get(ProjectMembershipRecord, membership.project_membership_id)
            if record is None:
                record = ProjectMembershipRecord.from_domain(membership)
                db.add(record)
            else:
                record.update_from_domain(membership)
            db.flush()
            return record.to_domain()

    def list_by_project(self, company_id: str, project_id: str) -> list[ProjectMembership]:
        """Return memberships for one project."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(ProjectMembershipRecord)
                .where(ProjectMembershipRecord.company_id == company_id)
                .where(ProjectMembershipRecord.project_id == project_id)
                .order_by(ProjectMembershipRecord.project_membership_id)
            )
            return [record.to_domain() for record in records]

    def list_by_user(self, user_id: str) -> list[ProjectMembership]:
        """Return project memberships for one user."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(ProjectMembershipRecord)
                .where(ProjectMembershipRecord.user_id == user_id)
                .order_by(ProjectMembershipRecord.project_membership_id)
            )
            return [record.to_domain() for record in records]


class SqlAlchemyRolePermissionRepository:
    """SQLAlchemy implementation of the role permission repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save(self, permission: RolePermission) -> RolePermission:
        """Persist a role permission."""

        with self._sessions.session() as db:
            record = db.get(RolePermissionRecord, permission.role_permission_id)
            if record is None:
                record = RolePermissionRecord.from_domain(permission)
                db.add(record)
            db.flush()
            return record.to_domain()

    def list_by_role(self, role: str) -> list[RolePermission]:
        """Return permissions for one role."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(RolePermissionRecord)
                .where(RolePermissionRecord.role == role)
                .order_by(RolePermissionRecord.role_permission_id)
            )
            return [record.to_domain() for record in records]


class SqlAlchemyAuthIdentityRepository:
    """SQLAlchemy implementation of the authentication identity repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save(self, identity: AuthIdentity) -> AuthIdentity:
        """Persist an authentication identity."""

        with self._sessions.session() as db:
            record = db.get(AuthIdentityRecord, identity.identity_id)
            if record is None:
                record = AuthIdentityRecord.from_domain(identity)
                db.add(record)
            else:
                record.update_from_domain(identity)
            db.flush()
            return record.to_domain()

    def list_by_user(self, user_id: str) -> list[AuthIdentity]:
        """Return identities for one user."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(AuthIdentityRecord)
                .where(AuthIdentityRecord.user_id == user_id)
                .order_by(AuthIdentityRecord.identity_id)
            )
            return [record.to_domain() for record in records]

    def get_by_provider_subject(self, provider: str, subject: str) -> AuthIdentity | None:
        """Return identity for provider and subject."""

        with self._sessions.session() as db:
            record = db.scalars(
                select(AuthIdentityRecord)
                .where(AuthIdentityRecord.provider == provider)
                .where(AuthIdentityRecord.subject == subject)
            ).first()
            return record.to_domain() if record is not None else None


class SqlAlchemyUserHistoryRepository:
    """SQLAlchemy implementation of the user history repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save(self, event: UserHistoryEvent) -> UserHistoryEvent:
        """Persist a user history event."""

        with self._sessions.session() as db:
            record = UserHistoryEventRecord.from_domain(event)
            db.add(record)
            db.flush()
            return record.to_domain()

    def list_by_user(self, user_id: str) -> list[UserHistoryEvent]:
        """Return history for one user."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(UserHistoryEventRecord)
                .where(UserHistoryEventRecord.user_id == user_id)
                .order_by(UserHistoryEventRecord.history_id)
            )
            return [record.to_domain() for record in records]


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


class SqlAlchemyCorporateGisRepository:
    """SQLAlchemy implementation of the corporate GIS repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save_postgis_schema(self, schema: PostgisSchema) -> PostgisSchema:
        """Persist a PostGIS schema reference."""

        with self._sessions.session() as db:
            record = db.get(PostgisSchemaRecord, schema.schema_id)
            if record is None:
                record = PostgisSchemaRecord.from_domain(schema)
                db.add(record)
            else:
                record.update_from_domain(schema)
            db.flush()
            return record.to_domain()

    def get_postgis_schema(self, schema_id: str) -> PostgisSchema | None:
        """Return one PostGIS schema reference."""

        with self._sessions.session() as db:
            record = db.get(PostgisSchemaRecord, schema_id)
            return record.to_domain() if record is not None else None

    def list_postgis_schemas(self, company_id: str, project_id: str | None = None) -> list[PostgisSchema]:
        """Return PostGIS schemas by company and optional project."""

        with self._sessions.session() as db:
            statement = select(PostgisSchemaRecord).where(PostgisSchemaRecord.company_id == company_id)
            if project_id is not None:
                statement = statement.where(PostgisSchemaRecord.project_id == project_id)
            records = db.scalars(statement.order_by(PostgisSchemaRecord.schema_id))
            return [record.to_domain() for record in records]

    def save_workspace(self, workspace: GeoServerWorkspace) -> GeoServerWorkspace:
        """Persist a GeoServer workspace reference."""

        with self._sessions.session() as db:
            record = db.get(GeoServerWorkspaceRecord, workspace.workspace_id)
            if record is None:
                record = GeoServerWorkspaceRecord.from_domain(workspace)
                db.add(record)
            else:
                record.update_from_domain(workspace)
            db.flush()
            return record.to_domain()

    def get_workspace(self, workspace_id: str) -> GeoServerWorkspace | None:
        """Return one GeoServer workspace reference."""

        with self._sessions.session() as db:
            record = db.get(GeoServerWorkspaceRecord, workspace_id)
            return record.to_domain() if record is not None else None

    def list_workspaces(self, company_id: str, project_id: str | None = None) -> list[GeoServerWorkspace]:
        """Return GeoServer workspaces by company and optional project."""

        with self._sessions.session() as db:
            statement = select(GeoServerWorkspaceRecord).where(
                GeoServerWorkspaceRecord.company_id == company_id
            )
            if project_id is not None:
                statement = statement.where(GeoServerWorkspaceRecord.project_id == project_id)
            records = db.scalars(statement.order_by(GeoServerWorkspaceRecord.workspace_id))
            return [record.to_domain() for record in records]

    def save_datastore(self, datastore: GeoServerDatastore) -> GeoServerDatastore:
        """Persist a GeoServer datastore reference."""

        with self._sessions.session() as db:
            record = db.get(GeoServerDatastoreRecord, datastore.datastore_id)
            if record is None:
                record = GeoServerDatastoreRecord.from_domain(datastore)
                db.add(record)
            else:
                record.update_from_domain(datastore)
            db.flush()
            return record.to_domain()

    def get_datastore(self, datastore_id: str) -> GeoServerDatastore | None:
        """Return one GeoServer datastore reference."""

        with self._sessions.session() as db:
            record = db.get(GeoServerDatastoreRecord, datastore_id)
            return record.to_domain() if record is not None else None

    def list_datastores(self, company_id: str, project_id: str | None = None) -> list[GeoServerDatastore]:
        """Return GeoServer datastores by company and optional project."""

        with self._sessions.session() as db:
            statement = select(GeoServerDatastoreRecord).where(
                GeoServerDatastoreRecord.company_id == company_id
            )
            if project_id is not None:
                statement = statement.where(GeoServerDatastoreRecord.project_id == project_id)
            records = db.scalars(statement.order_by(GeoServerDatastoreRecord.datastore_id))
            return [record.to_domain() for record in records]

    def save_layer(self, layer: GeoServerLayer) -> GeoServerLayer:
        """Persist a GeoServer layer reference."""

        with self._sessions.session() as db:
            record = db.get(GeoServerLayerRecord, layer.layer_id)
            if record is None:
                record = GeoServerLayerRecord.from_domain(layer)
                db.add(record)
            else:
                record.update_from_domain(layer)
            db.flush()
            return record.to_domain()

    def list_layers(self, company_id: str, project_id: str | None = None) -> list[GeoServerLayer]:
        """Return GeoServer layers by company and optional project."""

        with self._sessions.session() as db:
            statement = select(GeoServerLayerRecord).where(GeoServerLayerRecord.company_id == company_id)
            if project_id is not None:
                statement = statement.where(GeoServerLayerRecord.project_id == project_id)
            records = db.scalars(statement.order_by(GeoServerLayerRecord.layer_id))
            return [record.to_domain() for record in records]

    def save_binding(self, binding: ProjectGisBinding) -> ProjectGisBinding:
        """Persist a project GIS binding."""

        with self._sessions.session() as db:
            record = db.get(ProjectGisBindingRecord, binding.binding_id)
            if record is None:
                existing = db.scalars(
                    select(ProjectGisBindingRecord)
                    .where(ProjectGisBindingRecord.company_id == binding.company_id)
                    .where(ProjectGisBindingRecord.project_id == binding.project_id)
                ).first()
                record = existing or ProjectGisBindingRecord.from_domain(binding)
                if existing is None:
                    db.add(record)
            record.update_from_domain(binding)
            db.flush()
            return record.to_domain()

    def get_binding(self, company_id: str, project_id: str) -> ProjectGisBinding | None:
        """Return the GIS binding for one project."""

        with self._sessions.session() as db:
            record = db.scalars(
                select(ProjectGisBindingRecord)
                .where(ProjectGisBindingRecord.company_id == company_id)
                .where(ProjectGisBindingRecord.project_id == project_id)
            ).first()
            return record.to_domain() if record is not None else None


class SqlAlchemyCorporateGisIntelligenceRepository:
    """SQLAlchemy implementation of the Corporate GIS Intelligence repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save_source(self, source: CorporateGisSource) -> CorporateGisSource:
        """Persist a published WEB SIG GIS source reference."""

        with self._sessions.session() as db:
            record = db.get(CorporateGisSourceRecord, source.source_id)
            if record is None:
                record = CorporateGisSourceRecord.from_domain(source)
                db.add(record)
            else:
                record.update_from_domain(source)
            db.flush()
            return record.to_domain()

    def get_source(self, source_id: str) -> CorporateGisSource | None:
        """Return one Corporate GIS Intelligence source."""

        with self._sessions.session() as db:
            record = db.get(CorporateGisSourceRecord, source_id)
            return record.to_domain() if record is not None else None

    def list_sources(self, company_id: str, project_id: str | None = None) -> list[CorporateGisSource]:
        """Return sources by company and optional project."""

        with self._sessions.session() as db:
            statement = select(CorporateGisSourceRecord).where(
                CorporateGisSourceRecord.company_id == company_id
            )
            if project_id is not None:
                statement = statement.where(CorporateGisSourceRecord.project_id == project_id)
            records = db.scalars(statement.order_by(CorporateGisSourceRecord.source_id))
            return [record.to_domain() for record in records]

    def save_layer(self, layer: CorporateLayer) -> CorporateLayer:
        """Persist a corporate layer reference."""

        with self._sessions.session() as db:
            record = db.get(CorporateLayerRecord, layer.layer_id)
            if record is None:
                record = CorporateLayerRecord.from_domain(layer)
                db.add(record)
            else:
                record.update_from_domain(layer)
            db.flush()
            return record.to_domain()

    def list_layers(self, company_id: str, project_id: str | None = None) -> list[CorporateLayer]:
        """Return layers by company and optional project."""

        with self._sessions.session() as db:
            statement = select(CorporateLayerRecord).where(
                CorporateLayerRecord.company_id == company_id
            )
            if project_id is not None:
                statement = statement.where(CorporateLayerRecord.project_id == project_id)
            records = db.scalars(statement.order_by(CorporateLayerRecord.layer_id))
            return [record.to_domain() for record in records]


class SqlAlchemyCorporateWorkflowRepository:
    """SQLAlchemy implementation of the Corporate Workflow Engine repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save_workflow(self, workflow: CorporateWorkflowInstance) -> CorporateWorkflowInstance:
        """Persist one workflow instance."""

        with self._sessions.session() as db:
            record = db.get(CorporateWorkflowRecord, workflow.workflow_id)
            if record is None:
                record = CorporateWorkflowRecord.from_domain(workflow)
                db.add(record)
            else:
                record.update_from_domain(workflow)
            db.flush()
            return record.to_domain()

    def get_workflow(self, workflow_id: str) -> CorporateWorkflowInstance | None:
        """Return one workflow instance."""

        with self._sessions.session() as db:
            record = db.get(CorporateWorkflowRecord, workflow_id)
            return record.to_domain() if record is not None else None

    def list_workflows(self, company_id: str) -> list[CorporateWorkflowInstance]:
        """Return workflow instances for one company."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(CorporateWorkflowRecord)
                .where(CorporateWorkflowRecord.company_id == company_id)
                .order_by(CorporateWorkflowRecord.updated_at.desc())
            )
            return [record.to_domain() for record in records]

    def save_transition(self, transition: CorporateWorkflowTransition) -> CorporateWorkflowTransition:
        """Persist one auditable workflow transition."""

        with self._sessions.session() as db:
            record = CorporateWorkflowTransitionRecord.from_domain(transition)
            db.add(record)
            db.flush()
            return record.to_domain()

    def list_transitions(self, workflow_id: str) -> list[CorporateWorkflowTransition]:
        """Return transitions for one workflow."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(CorporateWorkflowTransitionRecord)
                .where(CorporateWorkflowTransitionRecord.workflow_id == workflow_id)
                .order_by(CorporateWorkflowTransitionRecord.created_at)
            )
            return [record.to_domain() for record in records]


class SqlAlchemyEnterpriseWizardRepository:
    """SQLAlchemy implementation of the Enterprise Wizard repository port."""

    def __init__(self, sessions: SqlAlchemySessionProvider) -> None:
        self._sessions = sessions

    def save(self, session: EnterpriseWizardSession) -> EnterpriseWizardSession:
        """Persist one wizard session."""

        with self._sessions.session() as db:
            record = db.get(EnterpriseWizardSessionRecord, session.wizard_id)
            if record is None:
                record = EnterpriseWizardSessionRecord.from_domain(session)
                db.add(record)
            else:
                record.update_from_domain(session)
            db.flush()
            return record.to_domain()

    def get(self, wizard_id: str) -> EnterpriseWizardSession | None:
        """Return one wizard session."""

        with self._sessions.session() as db:
            record = db.get(EnterpriseWizardSessionRecord, wizard_id)
            return record.to_domain() if record is not None else None

    def list(self) -> list[EnterpriseWizardSession]:
        """Return wizard sessions."""

        with self._sessions.session() as db:
            records = db.scalars(
                select(EnterpriseWizardSessionRecord).order_by(
                    EnterpriseWizardSessionRecord.updated_at.desc()
                )
            )
            return [record.to_domain() for record in records]
