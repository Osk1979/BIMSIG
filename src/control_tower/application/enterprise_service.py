"""Enterprise company, identity, and licensing application services.

ADR references:
- ADR-0006: Authentication and authorization.
- ADR-0014: Enterprise multitenancy.
- ADR-0016: Enterprise licensing.
"""

from control_tower.domain.audit import AuditEvent
from control_tower.domain.enterprise import (
    Company,
    CompanyLicense,
    CompanyMembership,
    LicensePlan,
    User,
)

from .repositories import (
    AuditEventRepository,
    CompanyLicenseRepository,
    CompanyMembershipRepository,
    CompanyRepository,
    LicensePlanRepository,
    UserRepository,
)


class CompanyService:
    """Coordinates enterprise tenant registration and lookup."""

    def __init__(
        self,
        companies: CompanyRepository,
        audit: AuditEventRepository | None = None,
    ) -> None:
        self._companies = companies
        self._audit = audit

    def register(self, company: Company) -> Company:
        """Register or update a company."""

        saved = self._companies.save(company)
        self._audit_event("company.registered", "company", saved.company_id)
        return saved

    def list_companies(self) -> list[Company]:
        """Return all registered companies."""

        return self._companies.list()

    def get_company(self, company_id: str) -> Company | None:
        """Return one company when it exists."""

        return self._companies.get(company_id)

    def exists(self, company_id: str) -> bool:
        """Return whether a company exists."""

        return self._companies.get(company_id) is not None

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


class UserService:
    """Coordinates users and company memberships."""

    def __init__(
        self,
        users: UserRepository,
        memberships: CompanyMembershipRepository,
        companies: CompanyService,
        audit: AuditEventRepository | None = None,
    ) -> None:
        self._users = users
        self._memberships = memberships
        self._companies = companies
        self._audit = audit

    def register_user(self, user: User) -> User:
        """Register or update a user."""

        saved = self._users.save(user)
        self._audit_event("user.registered", "user", saved.user_id)
        return saved

    def list_users(self) -> list[User]:
        """Return all users."""

        return self._users.list()

    def add_membership(self, membership: CompanyMembership) -> CompanyMembership:
        """Assign a user role inside a company."""

        if not self._companies.exists(membership.company_id):
            raise ValueError(f"Company is not registered: {membership.company_id}")
        if self._users.get(membership.user_id) is None:
            raise ValueError(f"User is not registered: {membership.user_id}")
        saved = self._memberships.save(membership)
        self._audit_event("membership.assigned", "membership", saved.membership_id)
        return saved

    def list_memberships(self, company_id: str) -> list[CompanyMembership]:
        """Return memberships for a company."""

        if not self._companies.exists(company_id):
            raise ValueError(f"Company is not registered: {company_id}")
        return self._memberships.list_by_company(company_id)

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


class LicensingService:
    """Coordinates license plans and company license assignment."""

    def __init__(
        self,
        plans: LicensePlanRepository,
        licenses: CompanyLicenseRepository,
        companies: CompanyService,
        audit: AuditEventRepository | None = None,
    ) -> None:
        self._plans = plans
        self._licenses = licenses
        self._companies = companies
        self._audit = audit

    def create_plan(self, plan: LicensePlan) -> LicensePlan:
        """Create or update a license plan."""

        saved = self._plans.save(plan)
        self._audit_event("license_plan.saved", "license_plan", saved.plan_id)
        return saved

    def list_plans(self) -> list[LicensePlan]:
        """Return all license plans."""

        return self._plans.list()

    def assign_license(self, license_assignment: CompanyLicense) -> CompanyLicense:
        """Assign a license plan to a company."""

        if not self._companies.exists(license_assignment.company_id):
            raise ValueError(f"Company is not registered: {license_assignment.company_id}")
        if self._plans.get(license_assignment.plan_id) is None:
            raise ValueError(f"License plan is not registered: {license_assignment.plan_id}")
        saved = self._licenses.save(license_assignment)
        self._audit_event("company_license.assigned", "company_license", saved.company_license_id)
        return saved

    def list_company_licenses(self, company_id: str) -> list[CompanyLicense]:
        """Return licenses assigned to a company."""

        if not self._companies.exists(company_id):
            raise ValueError(f"Company is not registered: {company_id}")
        return self._licenses.list_by_company(company_id)

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
