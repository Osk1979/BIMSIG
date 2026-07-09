from control_tower.application.rbac_policy import RbacPolicy
from control_tower.domain.enterprise import AuthProvider, AuthenticatedPrincipal, PermissionAction, PermissionScope, UserRole


def test_rbac_policy_applies_role_company_and_project_scope() -> None:
    policy = RbacPolicy()
    auditor = AuthenticatedPrincipal(
        user_id="USR-001",
        email="audit@example.com",
        display_name="Auditor",
        provider=AuthProvider.OIDC,
        subject="aad|audit",
        company_ids=["CRTG"],
        project_ids=["PSZ-2026"],
        roles=[UserRole.AUDITOR],
    )

    assert policy.is_allowed(auditor, PermissionScope.DASHBOARD, PermissionAction.READ, company_id="CRTG")
    assert policy.is_allowed(
        auditor,
        PermissionScope.PROJECT,
        PermissionAction.READ,
        company_id="CRTG",
        project_id="PSZ-2026",
    )
    assert not policy.is_allowed(auditor, PermissionScope.PROVISIONING, PermissionAction.EXECUTE, company_id="CRTG")
    assert not policy.is_allowed(auditor, PermissionScope.DASHBOARD, PermissionAction.READ, company_id="OTHER")


def test_platform_admin_bypasses_context() -> None:
    policy = RbacPolicy()
    admin = AuthenticatedPrincipal(
        user_id="USR-ADM",
        email="admin@example.com",
        display_name="Admin",
        provider=AuthProvider.LOCAL,
        subject="local|admin",
        roles=[UserRole.PLATFORM_ADMIN],
    )

    assert policy.is_allowed(admin, PermissionScope.PROVISIONING, PermissionAction.EXECUTE, company_id="ANY")
