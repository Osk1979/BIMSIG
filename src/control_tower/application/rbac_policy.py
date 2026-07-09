"""Enterprise RBAC policy matrix.

ADR references:
- ADR-0006: Authentication and authorization.
- ADR-0020: Corporate user security system.
"""

from dataclasses import dataclass

from control_tower.domain.enterprise import AuthenticatedPrincipal, PermissionAction, PermissionScope, UserRole


@dataclass(frozen=True)
class PermissionRule:
    """One role-to-permission matrix row."""

    role: UserRole
    scope: PermissionScope
    action: PermissionAction


DEFAULT_PERMISSION_MATRIX: tuple[PermissionRule, ...] = (
    PermissionRule(UserRole.PLATFORM_ADMIN, PermissionScope.PLATFORM, PermissionAction.ADMIN),
    PermissionRule(UserRole.PLATFORM_ADMIN, PermissionScope.COMPANY, PermissionAction.ADMIN),
    PermissionRule(UserRole.PLATFORM_ADMIN, PermissionScope.PROJECT, PermissionAction.ADMIN),
    PermissionRule(UserRole.PLATFORM_ADMIN, PermissionScope.NAS, PermissionAction.ADMIN),
    PermissionRule(UserRole.PLATFORM_ADMIN, PermissionScope.DASHBOARD, PermissionAction.ADMIN),
    PermissionRule(UserRole.PLATFORM_ADMIN, PermissionScope.PROVISIONING, PermissionAction.ADMIN),
    PermissionRule(UserRole.PORTFOLIO_MANAGER, PermissionScope.COMPANY, PermissionAction.READ),
    PermissionRule(UserRole.PORTFOLIO_MANAGER, PermissionScope.COMPANY, PermissionAction.WRITE),
    PermissionRule(UserRole.PORTFOLIO_MANAGER, PermissionScope.PROJECT, PermissionAction.READ),
    PermissionRule(UserRole.PORTFOLIO_MANAGER, PermissionScope.PROJECT, PermissionAction.WRITE),
    PermissionRule(UserRole.PORTFOLIO_MANAGER, PermissionScope.DASHBOARD, PermissionAction.READ),
    PermissionRule(UserRole.PORTFOLIO_MANAGER, PermissionScope.PROVISIONING, PermissionAction.APPROVE),
    PermissionRule(UserRole.PORTFOLIO_MANAGER, PermissionScope.PROVISIONING, PermissionAction.EXECUTE),
    PermissionRule(UserRole.PROJECT_OPERATOR, PermissionScope.PROJECT, PermissionAction.READ),
    PermissionRule(UserRole.PROJECT_OPERATOR, PermissionScope.PROJECT, PermissionAction.WRITE),
    PermissionRule(UserRole.PROJECT_OPERATOR, PermissionScope.NAS, PermissionAction.READ),
    PermissionRule(UserRole.PROJECT_OPERATOR, PermissionScope.NAS, PermissionAction.WRITE),
    PermissionRule(UserRole.PROJECT_OPERATOR, PermissionScope.DASHBOARD, PermissionAction.READ),
    PermissionRule(UserRole.AUDITOR, PermissionScope.COMPANY, PermissionAction.READ),
    PermissionRule(UserRole.AUDITOR, PermissionScope.PROJECT, PermissionAction.READ),
    PermissionRule(UserRole.AUDITOR, PermissionScope.NAS, PermissionAction.READ),
    PermissionRule(UserRole.AUDITOR, PermissionScope.DASHBOARD, PermissionAction.READ),
    PermissionRule(UserRole.AUDITOR, PermissionScope.PROVISIONING, PermissionAction.READ),
    PermissionRule(UserRole.SERVICE_ACCOUNT, PermissionScope.PROVISIONING, PermissionAction.EXECUTE),
    PermissionRule(UserRole.SERVICE_ACCOUNT, PermissionScope.NAS, PermissionAction.WRITE),
)


class RbacPolicy:
    """Evaluates enterprise role, company, and project permissions."""

    def __init__(self, rules: tuple[PermissionRule, ...] = DEFAULT_PERMISSION_MATRIX) -> None:
        self._rules = rules

    def matrix(self) -> list[dict[str, str]]:
        """Return the effective static role matrix."""

        return [
            {"role": rule.role.value, "scope": rule.scope.value, "action": rule.action.value}
            for rule in self._rules
        ]

    def is_allowed(
        self,
        principal: AuthenticatedPrincipal,
        scope: PermissionScope,
        action: PermissionAction,
        company_id: str | None = None,
        project_id: str | None = None,
    ) -> bool:
        """Return whether a principal can perform an action in context."""

        if UserRole.PLATFORM_ADMIN in principal.roles:
            return True
        if company_id and company_id not in principal.company_ids:
            return False
        if project_id and project_id not in principal.project_ids and UserRole.PORTFOLIO_MANAGER not in principal.roles:
            return False
        return any(
            rule.role in principal.roles
            and rule.scope == scope
            and (rule.action == action or rule.action == PermissionAction.ADMIN)
            for rule in self._rules
        )


def infer_permission(path: str, method: str) -> tuple[PermissionScope, PermissionAction]:
    """Infer a coarse permission from an API path and HTTP method."""

    action = PermissionAction.READ if method == "GET" else PermissionAction.WRITE
    if "/infrastructure/connectors" in path:
        action = PermissionAction.EXECUTE if path.endswith("/execute") else PermissionAction.READ
        return PermissionScope.PROVISIONING, action
    if "/websig-factory" in path or "/provisioning" in path:
        action = PermissionAction.EXECUTE if path.endswith("/execute") or method == "POST" else PermissionAction.READ
        return PermissionScope.PROVISIONING, action
    if "/nas/" in path:
        return PermissionScope.NAS, action
    if "/audit/" in path:
        return PermissionScope.PROVISIONING, PermissionAction.READ
    if "/reports/" in path:
        return PermissionScope.DASHBOARD, PermissionAction.READ
    if "/observability" in path or path == "/metrics":
        return PermissionScope.PLATFORM, PermissionAction.READ
    if "/dashboard" in path or "/gis-intelligence" in path:
        return PermissionScope.DASHBOARD, action
    if "/projects" in path:
        return PermissionScope.PROJECT, action
    if "/companies" in path:
        return PermissionScope.COMPANY, action
    return PermissionScope.PLATFORM, action
