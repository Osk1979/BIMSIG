"""Enterprise authentication and SSO session service.

ADR references:
- ADR-0006: Authentication and authorization.
- ADR-0020: Corporate user security system.
"""

from __future__ import annotations

import base64
import hmac
import json
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import uuid4

from control_tower.domain.audit import AuditEvent
from control_tower.domain.enterprise import (
    AuthIdentity,
    AuthProvider,
    AuthSession,
    AuthenticatedPrincipal,
    ProjectMembership,
    UserRole,
)

from .enterprise_service import CompanyService, CorporateUserSecurityService, UserService
from .repositories import AuditEventRepository


class EnterpriseAuthService:
    """Issues and validates signed Enterprise API sessions."""

    def __init__(
        self,
        user_security: CorporateUserSecurityService,
        users: UserService,
        companies: CompanyService,
        signing_secret: str,
        audit: AuditEventRepository | None = None,
        ttl_minutes: int = 480,
    ) -> None:
        if len(signing_secret) < 16:
            raise ValueError("Authentication signing secret must be at least 16 characters")
        self._security = user_security
        self._users = users
        self._companies = companies
        self._secret = signing_secret.encode("utf-8")
        self._audit = audit
        self._ttl = timedelta(minutes=ttl_minutes)
        self._revoked_tokens: set[str] = set()

    def login(self, provider: str, subject: str) -> AuthSession:
        """Authenticate an existing local/OIDC/SAML identity and issue a session."""

        identity = self._security.authenticate_sso(provider, subject)
        principal = self._principal(identity)
        session = self._session(principal)
        self._audit_event(
            actor=principal.user_id,
            action="auth.session.created",
            entity_id=principal.user_id,
            detail=f"Session issued for {principal.provider.value}/{principal.subject}",
        )
        return session

    def verify(self, token: str) -> AuthenticatedPrincipal:
        """Verify a signed bearer token and return the authenticated actor."""

        if token in self._revoked_tokens:
            raise ValueError("Authentication token has been revoked")
        payload = self._decode_token(token)
        expires_at = datetime.fromisoformat(str(payload["exp"]))
        if expires_at <= datetime.now(UTC):
            raise ValueError("Authentication token has expired")
        return AuthenticatedPrincipal(
            user_id=str(payload["sub"]),
            email=str(payload["email"]),
            display_name=str(payload["name"]),
            provider=AuthProvider(str(payload["provider"])),
            subject=str(payload["provider_subject"]),
            company_ids=list(payload.get("companies", [])),
            project_ids=list(payload.get("projects", [])),
            roles=[UserRole(role) for role in payload.get("roles", [])],
        )

    def logout(self, token: str) -> None:
        """Revoke a bearer token for the current process lifetime."""

        principal = self.verify(token)
        self._revoked_tokens.add(token)
        self._audit_event(
            actor=principal.user_id,
            action="auth.session.revoked",
            entity_id=principal.user_id,
            detail="Session revoked by logout.",
        )

    def _principal(self, identity: AuthIdentity) -> AuthenticatedPrincipal:
        user = self._users.get_user(identity.user_id)
        if user is None:
            raise ValueError(f"User is not registered: {identity.user_id}")
        memberships = self._users.list_memberships_for_user(identity.user_id)
        project_memberships = self._security.list_project_memberships_for_user(identity.user_id)
        roles = {membership.role for membership in memberships}
        roles.update(membership.role for membership in project_memberships)
        return AuthenticatedPrincipal(
            user_id=user.user_id,
            email=user.email,
            display_name=user.display_name,
            provider=identity.provider,
            subject=identity.subject,
            company_ids=sorted(
                {membership.company_id for membership in memberships}.union(
                    self._companies_for_projects(project_memberships)
                )
            ),
            project_ids=sorted({membership.project_id for membership in project_memberships}),
            roles=sorted(roles, key=lambda role: role.value),
        )

    @staticmethod
    def _companies_for_projects(project_memberships: list[ProjectMembership]) -> set[str]:
        return {membership.company_id for membership in project_memberships}

    def _session(self, principal: AuthenticatedPrincipal) -> AuthSession:
        expires_at = datetime.now(UTC) + self._ttl
        claims: dict[str, str | list[str]] = {
            "sub": principal.user_id,
            "email": principal.email,
            "name": principal.display_name,
            "provider": principal.provider.value,
            "provider_subject": principal.subject,
            "companies": principal.company_ids,
            "projects": principal.project_ids,
            "roles": [role.value for role in principal.roles],
            "jti": uuid4().hex,
            "exp": expires_at.isoformat(),
        }
        return AuthSession(
            access_token=self._encode_token(claims),
            expires_at=expires_at,
            principal=principal,
            claims=claims,
        )

    def _encode_token(self, claims: dict[str, str | list[str]]) -> str:
        payload = self._b64(json.dumps(claims, separators=(",", ":"), sort_keys=True).encode("utf-8"))
        signature = self._signature(payload)
        return f"{payload}.{signature}"

    def _decode_token(self, token: str) -> dict:
        try:
            payload, signature = token.split(".", 1)
        except ValueError as exc:
            raise ValueError("Invalid authentication token format") from exc
        expected = self._signature(payload)
        if not hmac.compare_digest(signature, expected):
            raise ValueError("Invalid authentication token signature")
        try:
            return json.loads(base64.urlsafe_b64decode(self._pad(payload)).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("Invalid authentication token payload") from exc

    def _signature(self, payload: str) -> str:
        digest = hmac.new(self._secret, payload.encode("ascii"), sha256).digest()
        return self._b64(digest)

    @staticmethod
    def _b64(value: bytes) -> str:
        return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")

    @staticmethod
    def _pad(value: str) -> bytes:
        return (value + ("=" * (-len(value) % 4))).encode("ascii")

    def _audit_event(self, actor: str, action: str, entity_id: str, detail: str) -> None:
        if self._audit is None:
            return
        self._audit.save(
            AuditEvent(
                actor=actor,
                action=action,
                entity_type="auth_session",
                entity_id=entity_id,
                detail=detail,
            )
        )
