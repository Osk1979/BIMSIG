from control_tower.application.enterprise_service import CompanyService, CorporateUserSecurityService
from control_tower.application.portfolio_service import PortfolioService
from control_tower.domain.enterprise import (
    AuthIdentity,
    Company,
    PermissionAction,
    PermissionScope,
    ProjectMembership,
    RolePermission,
    Specialty,
    User,
    UserRole,
    UserSpecialty,
)
from control_tower.domain.portfolio import PortfolioProject
from tests.unit.fakes import (
    FakeAuditEventRepository,
    FakeAuthIdentityRepository,
    FakeCompanyRepository,
    FakePortfolioProjectRepository,
    FakeProjectMembershipRepository,
    FakeRolePermissionRepository,
    FakeSpecialtyRepository,
    FakeUserHistoryRepository,
    FakeUserRepository,
    FakeUserSpecialtyRepository,
)


def test_corporate_user_security_manages_roles_sso_and_history() -> None:
    audit = FakeAuditEventRepository()
    users = FakeUserRepository()
    companies = CompanyService(FakeCompanyRepository(), audit)
    portfolio = PortfolioService(FakePortfolioProjectRepository(), audit)
    service = CorporateUserSecurityService(
        users,
        companies,
        portfolio,
        FakeSpecialtyRepository(),
        FakeUserSpecialtyRepository(),
        FakeProjectMembershipRepository(),
        FakeRolePermissionRepository(),
        FakeAuthIdentityRepository(),
        FakeUserHistoryRepository(),
        audit,
    )
    companies.register(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    users.save(User(user_id="USR-001", email="admin@example.com", display_name="Admin"))
    portfolio.register_for_company(
        "CRTG",
        PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"),
    )

    specialty = service.create_specialty(Specialty(specialty_id="SPEC-BIM", name="BIM"))
    assignment = service.assign_specialty(
        UserSpecialty(
            user_specialty_id="USPEC-001",
            user_id="USR-001",
            specialty_id="SPEC-BIM",
        )
    )
    membership = service.assign_project_membership(
        ProjectMembership(
            project_membership_id="PMEM-001",
            company_id="CRTG",
            project_id="PSZ-2026",
            user_id="USR-001",
            role=UserRole.PROJECT_OPERATOR,
        )
    )
    permission = service.grant_role_permission(
        RolePermission(
            role_permission_id="PERM-001",
            role=UserRole.PROJECT_OPERATOR,
            scope=PermissionScope.NAS,
            action=PermissionAction.WRITE,
        )
    )
    identity = service.register_auth_identity(
        AuthIdentity(
            identity_id="IDP-001",
            user_id="USR-001",
            provider="oidc",
            subject="aad|001",
            email="admin@example.com",
        )
    )

    resolved = service.authenticate_sso("oidc", "aad|001")
    history_actions = {event.action for event in service.list_user_history("USR-001")}

    assert specialty.name == "BIM"
    assert assignment.specialty_id == "SPEC-BIM"
    assert membership.project_id == "PSZ-2026"
    assert permission.scope == PermissionScope.NAS
    assert identity.identity_id == resolved.identity_id
    assert service.has_permission(
        "USR-001",
        PermissionScope.NAS,
        PermissionAction.WRITE,
        company_id="CRTG",
        project_id="PSZ-2026",
    )
    assert history_actions >= {
        "user_specialty.assigned",
        "project_membership.assigned",
        "auth_identity.linked",
        "auth_identity.authenticated",
    }
    assert {
        event.action for event in audit.events
    } >= {
        "specialty.saved",
        "user_specialty.assigned",
        "project_membership.assigned",
        "role_permission.granted",
        "auth_identity.linked",
    }
