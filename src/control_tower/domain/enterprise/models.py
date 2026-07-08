"""Enterprise tenant, identity, and licensing domain models.

ADR references:
- ADR-0006: Authentication and authorization.
- ADR-0014: Enterprise multitenancy.
- ADR-0016: Enterprise licensing.
"""

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class CompanyStatus(StrEnum):
    """Lifecycle status for an enterprise tenant."""

    ACTIVE = "active"
    SUSPENDED = "suspended"


class UserStatus(StrEnum):
    """Lifecycle status for a user identity."""

    ACTIVE = "active"
    DISABLED = "disabled"


class UserRole(StrEnum):
    """Company-scoped user role."""

    PLATFORM_ADMIN = "platform_admin"
    PORTFOLIO_MANAGER = "portfolio_manager"
    PROJECT_OPERATOR = "project_operator"
    AUDITOR = "auditor"
    SERVICE_ACCOUNT = "service_account"


class PermissionScope(StrEnum):
    """Enterprise security permission scope."""

    PLATFORM = "platform"
    COMPANY = "company"
    PROJECT = "project"
    NAS = "nas"
    DASHBOARD = "dashboard"
    PROVISIONING = "provisioning"


class PermissionAction(StrEnum):
    """Enterprise security permission action."""

    READ = "read"
    WRITE = "write"
    APPROVE = "approve"
    EXECUTE = "execute"
    ADMIN = "admin"


class AuthProvider(StrEnum):
    """Authentication provider type."""

    LOCAL = "local"
    OIDC = "oidc"
    SAML = "saml"


class MembershipStatus(StrEnum):
    """Lifecycle status for company membership."""

    ACTIVE = "active"
    SUSPENDED = "suspended"


class LicenseStatus(StrEnum):
    """Lifecycle status for company license assignment."""

    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class Company(BaseModel):
    """Enterprise tenant administered by Corporate Control Tower."""

    company_id: str = Field(min_length=3, examples=["CRTG"])
    legal_name: str = Field(min_length=3, examples=["CRTG S.A.C."])
    display_name: str = Field(min_length=2, examples=["CRTG"])
    tax_id: str | None = Field(default=None, examples=["RUC 00000000000"])
    status: CompanyStatus = CompanyStatus.ACTIVE


class User(BaseModel):
    """Person or service identity known by the platform."""

    user_id: str = Field(min_length=3, examples=["USR-001"])
    email: str = Field(min_length=5, examples=["admin@example.com"])
    display_name: str = Field(min_length=2, examples=["Usuario Admin"])
    identity_provider_subject: str | None = None
    status: UserStatus = UserStatus.ACTIVE


class Specialty(BaseModel):
    """Corporate user specialty or professional discipline."""

    specialty_id: str = Field(min_length=3, examples=["SPEC-BIM"])
    name: str = Field(min_length=3, examples=["BIM Management"])
    description: str | None = None


class UserSpecialty(BaseModel):
    """Specialty assigned to a platform user."""

    user_specialty_id: str = Field(min_length=3, examples=["USPEC-001"])
    user_id: str = Field(min_length=3, examples=["USR-001"])
    specialty_id: str = Field(min_length=3, examples=["SPEC-BIM"])


class CompanyMembership(BaseModel):
    """User membership and role inside a company."""

    membership_id: str = Field(min_length=3, examples=["MEM-001"])
    company_id: str = Field(min_length=3, examples=["CRTG"])
    user_id: str = Field(min_length=3, examples=["USR-001"])
    role: UserRole
    status: MembershipStatus = MembershipStatus.ACTIVE


class ProjectMembership(BaseModel):
    """User role assignment inside one project."""

    project_membership_id: str = Field(min_length=3, examples=["PMEM-001"])
    company_id: str = Field(min_length=3, examples=["CRTG"])
    project_id: str = Field(min_length=3, examples=["PSZ-2026"])
    user_id: str = Field(min_length=3, examples=["USR-001"])
    role: UserRole
    status: MembershipStatus = MembershipStatus.ACTIVE


class RolePermission(BaseModel):
    """Permission granted to an enterprise role."""

    role_permission_id: str = Field(min_length=3, examples=["PERM-001"])
    role: UserRole
    scope: PermissionScope
    action: PermissionAction


class AuthIdentity(BaseModel):
    """Authentication or SSO identity linked to a platform user."""

    identity_id: str = Field(min_length=3, examples=["IDP-001"])
    user_id: str = Field(min_length=3, examples=["USR-001"])
    provider: AuthProvider
    subject: str = Field(min_length=3, examples=["aad|00000000"])
    email: str = Field(min_length=5, examples=["admin@example.com"])
    status: UserStatus = UserStatus.ACTIVE


class UserHistoryEvent(BaseModel):
    """Auditable user security history entry."""

    history_id: str = Field(min_length=3, examples=["HIST-001"])
    user_id: str = Field(min_length=3, examples=["USR-001"])
    action: str = Field(min_length=3, examples=["project_membership.assigned"])
    detail: str | None = None
    company_id: str | None = Field(default=None, min_length=3)
    project_id: str | None = Field(default=None, min_length=3)


class LicensePlan(BaseModel):
    """Commercial entitlement plan."""

    plan_id: str = Field(min_length=3, examples=["PLAN-ENTERPRISE"])
    name: str = Field(min_length=3, examples=["Enterprise"])
    max_users: int = Field(ge=0, default=0)
    max_projects: int = Field(ge=0, default=0)
    max_websig_instances: int = Field(ge=0, default=0)
    enabled_modules: str = Field(default="portfolio,provisioning,audit")
    ai_enabled: bool = False
    reporting_enabled: bool = False


class CompanyLicense(BaseModel):
    """License plan assigned to a company."""

    company_license_id: str = Field(min_length=3, examples=["LIC-001"])
    company_id: str = Field(min_length=3, examples=["CRTG"])
    plan_id: str = Field(min_length=3, examples=["PLAN-ENTERPRISE"])
    valid_from: date
    valid_to: date | None = None
    status: LicenseStatus = LicenseStatus.ACTIVE
