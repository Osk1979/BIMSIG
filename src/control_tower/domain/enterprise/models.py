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


class CompanyMembership(BaseModel):
    """User membership and role inside a company."""

    membership_id: str = Field(min_length=3, examples=["MEM-001"])
    company_id: str = Field(min_length=3, examples=["CRTG"])
    user_id: str = Field(min_length=3, examples=["USR-001"])
    role: UserRole
    status: MembershipStatus = MembershipStatus.ACTIVE


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
