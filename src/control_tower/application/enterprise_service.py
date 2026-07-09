"""Enterprise company, identity, and licensing application services.

ADR references:
- ADR-0006: Authentication and authorization.
- ADR-0014: Enterprise multitenancy.
- ADR-0016: Enterprise licensing.
"""

from control_tower.domain.audit import AuditEvent
from control_tower.domain.enterprise import (
    AuthIdentity,
    Company,
    CompanyLicense,
    CompanyMembership,
    LicensePlan,
    PermissionAction,
    PermissionScope,
    ProjectMembership,
    RolePermission,
    Specialty,
    User,
    UserHistoryEvent,
    UserRole,
    UserSpecialty,
)

from .portfolio_service import PortfolioService
from .repositories import (
    AuditEventRepository,
    AuthIdentityRepository,
    CompanyLicenseRepository,
    CompanyMembershipRepository,
    CompanyRepository,
    LicensePlanRepository,
    ProjectMembershipRepository,
    RolePermissionRepository,
    SpecialtyRepository,
    UserHistoryRepository,
    UserRepository,
    UserSpecialtyRepository,
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

    def get_user(self, user_id: str) -> User | None:
        """Return one user when it exists."""

        return self._users.get(user_id)

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

    def list_memberships_for_user(self, user_id: str) -> list[CompanyMembership]:
        """Return company memberships for one user."""

        if self._users.get(user_id) is None:
            raise ValueError(f"User is not registered: {user_id}")
        return [
            membership
            for company in self._companies.list_companies()
            for membership in self._memberships.list_by_company(company.company_id)
            if membership.user_id == user_id
        ]

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


class CorporateUserSecurityService:
    """Coordinates enterprise users, specialties, permissions, SSO, and history."""

    def __init__(
        self,
        users: UserRepository,
        companies: CompanyService,
        portfolio: PortfolioService,
        specialties: SpecialtyRepository,
        user_specialties: UserSpecialtyRepository,
        project_memberships: ProjectMembershipRepository,
        role_permissions: RolePermissionRepository,
        auth_identities: AuthIdentityRepository,
        history: UserHistoryRepository,
        audit: AuditEventRepository | None = None,
    ) -> None:
        self._users = users
        self._companies = companies
        self._portfolio = portfolio
        self._specialties = specialties
        self._user_specialties = user_specialties
        self._project_memberships = project_memberships
        self._role_permissions = role_permissions
        self._auth_identities = auth_identities
        self._history = history
        self._audit = audit

    def create_specialty(self, specialty: Specialty) -> Specialty:
        """Create or update a corporate specialty."""

        saved = self._specialties.save(specialty)
        self._audit_event("specialty.saved", "specialty", saved.specialty_id)
        return saved

    def list_specialties(self) -> list[Specialty]:
        """Return corporate specialties."""

        return self._specialties.list()

    def assign_specialty(self, assignment: UserSpecialty) -> UserSpecialty:
        """Assign a specialty to a user."""

        self._require_user(assignment.user_id)
        if self._specialties.get(assignment.specialty_id) is None:
            raise ValueError(f"Specialty is not registered: {assignment.specialty_id}")
        saved = self._user_specialties.save(assignment)
        self._record_history(
            assignment.user_id,
            "user_specialty.assigned",
            f"Specialty assigned: {assignment.specialty_id}",
        )
        self._audit_event("user_specialty.assigned", "user_specialty", saved.user_specialty_id)
        return saved

    def list_user_specialties(self, user_id: str) -> list[UserSpecialty]:
        """Return specialties assigned to a user."""

        self._require_user(user_id)
        return self._user_specialties.list_by_user(user_id)

    def assign_project_membership(self, membership: ProjectMembership) -> ProjectMembership:
        """Assign a user role inside one project."""

        self._require_user(membership.user_id)
        self._require_company_project(membership.company_id, membership.project_id)
        saved = self._project_memberships.save(membership)
        self._record_history(
            membership.user_id,
            "project_membership.assigned",
            f"Project role assigned: {membership.company_id}/{membership.project_id}/{membership.role.value}",
            company_id=membership.company_id,
            project_id=membership.project_id,
        )
        self._audit_event("project_membership.assigned", "project_membership", saved.project_membership_id)
        return saved

    def list_project_memberships(self, company_id: str, project_id: str) -> list[ProjectMembership]:
        """Return memberships for one project."""

        self._require_company_project(company_id, project_id)
        return self._project_memberships.list_by_project(company_id, project_id)

    def list_project_memberships_for_user(self, user_id: str) -> list[ProjectMembership]:
        """Return project memberships for one user."""

        self._require_user(user_id)
        return self._project_memberships.list_by_user(user_id)

    def grant_role_permission(self, permission: RolePermission) -> RolePermission:
        """Grant a permission to an enterprise role."""

        saved = self._role_permissions.save(permission)
        self._audit_event("role_permission.granted", "role_permission", saved.role_permission_id)
        return saved

    def list_role_permissions(self, role: UserRole) -> list[RolePermission]:
        """Return permissions for one role."""

        return self._role_permissions.list_by_role(role.value)

    def register_auth_identity(self, identity: AuthIdentity) -> AuthIdentity:
        """Link a local or SSO identity to a user."""

        self._require_user(identity.user_id)
        existing = self._auth_identities.get_by_provider_subject(identity.provider.value, identity.subject)
        if existing is not None and existing.identity_id != identity.identity_id:
            raise ValueError("Authentication identity subject is already linked")
        saved = self._auth_identities.save(identity)
        self._record_history(
            identity.user_id,
            "auth_identity.linked",
            f"Identity linked: {identity.provider.value}/{identity.subject}",
        )
        self._audit_event("auth_identity.linked", "auth_identity", saved.identity_id)
        return saved

    def list_auth_identities(self, user_id: str) -> list[AuthIdentity]:
        """Return authentication identities for a user."""

        self._require_user(user_id)
        return self._auth_identities.list_by_user(user_id)

    def authenticate_sso(self, provider: str, subject: str) -> AuthIdentity:
        """Resolve an SSO identity for authentication."""

        identity = self._auth_identities.get_by_provider_subject(provider, subject)
        if identity is None:
            raise ValueError("Authentication identity is not registered")
        self._record_history(
            identity.user_id,
            "auth_identity.authenticated",
            f"SSO authentication: {provider}/{subject}",
        )
        return identity

    def list_user_history(self, user_id: str) -> list[UserHistoryEvent]:
        """Return security history for one user."""

        self._require_user(user_id)
        return self._history.list_by_user(user_id)

    def has_permission(
        self,
        user_id: str,
        scope: PermissionScope,
        action: PermissionAction,
        company_id: str | None = None,
        project_id: str | None = None,
    ) -> bool:
        """Return whether a user has a permission through project roles."""

        self._require_user(user_id)
        roles: set[UserRole] = set()
        for membership in self._project_memberships.list_by_user(user_id):
            if company_id is not None and membership.company_id != company_id:
                continue
            if project_id is not None and membership.project_id != project_id:
                continue
            roles.add(membership.role)
        for role in roles:
            permissions = self._role_permissions.list_by_role(role.value)
            if any(permission.scope == scope and permission.action == action for permission in permissions):
                return True
        return False

    def _require_user(self, user_id: str) -> User:
        user = self._users.get(user_id)
        if user is None:
            raise ValueError(f"User is not registered: {user_id}")
        return user

    def _require_company_project(self, company_id: str, project_id: str) -> None:
        if not self._companies.exists(company_id):
            raise ValueError(f"Company is not registered: {company_id}")
        if self._portfolio.get_project_for_company(company_id, project_id) is None:
            raise ValueError(f"Project is not registered for company {company_id}: {project_id}")

    def _record_history(
        self,
        user_id: str,
        action: str,
        detail: str,
        company_id: str | None = None,
        project_id: str | None = None,
    ) -> None:
        self._history.save(
            UserHistoryEvent(
                history_id=f"HIST-{user_id}-{len(self._history.list_by_user(user_id)) + 1}",
                user_id=user_id,
                action=action,
                detail=detail,
                company_id=company_id,
                project_id=project_id,
            )
        )

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
