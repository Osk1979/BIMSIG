from control_tower.application.auth_service import EnterpriseAuthService
from control_tower.application.enterprise_service import CompanyService, CorporateUserSecurityService, UserService
from control_tower.application.portfolio_service import PortfolioService
from control_tower.domain.enterprise import AuthIdentity, Company, CompanyMembership, ProjectMembership, User
from control_tower.domain.portfolio import PortfolioProject
from tests.unit.fakes import (
    FakeAuditEventRepository,
    FakeAuthIdentityRepository,
    FakeCompanyRepository,
    FakeMembershipRepository,
    FakePortfolioProjectRepository,
    FakeProjectMembershipRepository,
    FakeRolePermissionRepository,
    FakeSpecialtyRepository,
    FakeUserHistoryRepository,
    FakeUserRepository,
    FakeUserSpecialtyRepository,
)


def test_enterprise_auth_service_issues_claims_and_revokes_session() -> None:
    audit = FakeAuditEventRepository()
    user_repository = FakeUserRepository()
    companies = CompanyService(FakeCompanyRepository(), audit)
    users = UserService(user_repository, FakeMembershipRepository(), companies, audit)
    portfolio = PortfolioService(FakePortfolioProjectRepository(), audit)
    project_memberships = FakeProjectMembershipRepository()
    auth_identities = FakeAuthIdentityRepository()
    security = CorporateUserSecurityService(
        user_repository,
        companies,
        portfolio,
        FakeSpecialtyRepository(),
        FakeUserSpecialtyRepository(),
        project_memberships,
        FakeRolePermissionRepository(),
        auth_identities,
        FakeUserHistoryRepository(),
        audit,
    )
    companies.register(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    users.register_user(User(user_id="USR-001", email="admin@example.com", display_name="Admin"))
    users.add_membership(
        CompanyMembership(
            membership_id="MEM-001",
            company_id="CRTG",
            user_id="USR-001",
            role="portfolio_manager",
        )
    )
    portfolio.register_for_company(
        "CRTG",
        PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"),
    )
    security.assign_project_membership(
        ProjectMembership(
            project_membership_id="PMEM-001",
            company_id="CRTG",
            project_id="PSZ-2026",
            user_id="USR-001",
            role="project_operator",
        )
    )
    security.register_auth_identity(
        AuthIdentity(
            identity_id="IDP-001",
            user_id="USR-001",
            provider="oidc",
            subject="aad|001",
            email="admin@example.com",
        )
    )
    auth = EnterpriseAuthService(
        security,
        users,
        companies,
        signing_secret="test-auth-secret-32-characters",
        audit=audit,
    )

    session = auth.login("oidc", "aad|001")
    principal = auth.verify(session.access_token)

    assert session.token_type == "bearer"
    assert principal.user_id == "USR-001"
    assert principal.company_ids == ["CRTG"]
    assert principal.project_ids == ["PSZ-2026"]
    assert {role.value for role in principal.roles} == {"portfolio_manager", "project_operator"}
    assert "auth.session.created" in {event.action for event in audit.events}

    auth.logout(session.access_token)

    assert "auth.session.revoked" in {event.action for event in audit.events}
