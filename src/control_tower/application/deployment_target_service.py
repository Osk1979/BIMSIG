"""Deployment Target Manager application service.

ADR references:
- ADR-0011: Deployment strategy.
- ADR-0021: DevSecOps operating model.
- ADR-0031: Deployment Target Manager.
"""

from __future__ import annotations

from datetime import UTC, datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from control_tower.domain.deployment_targets import (
    DeploymentTarget,
    DeploymentTargetCatalog,
    DeploymentTargetCheck,
    DeploymentTargetStatus,
    DeploymentTargetType,
    DeploymentTargetValidation,
)


DEFAULT_HEALTH_ENDPOINTS = [
    "/health",
    "/api/v1/operational/readiness",
    "/api/v1/portal-gateway/health",
    "/api/v1/connection-center/health",
]


class DeploymentTargetService:
    """Manages selectable backend deployment targets for the Tower."""

    def __init__(
        self,
        *,
        local_backend_url: str = "http://127.0.0.1:8000",
        public_backend_url: str | None = None,
        cloud_backend_url: str | None = None,
        tunnel_backend_url: str | None = None,
        active_target_id: str = "local-docker",
        cors_origin: str = "https://bimsig-enterprise.oscarsalas1979.chatgpt.site",
    ) -> None:
        self._active_target_id = active_target_id
        self._cors_origin = cors_origin
        self._targets = {
            target.target_id: target
            for target in [
                self._target(
                    "local-docker",
                    "Local Docker",
                    DeploymentTargetType.LOCAL_DOCKER,
                    local_backend_url,
                    public=False,
                    description="Local Docker runtime used for development and controlled validation.",
                ),
                self._target(
                    "production-public-api",
                    "Production Public API",
                    DeploymentTargetType.VPS,
                    public_backend_url,
                    public=True,
                    description="Public backend API endpoint hosted on VPS or managed server.",
                ),
                self._target(
                    "cloud-container",
                    "Cloud Container",
                    DeploymentTargetType.CLOUD_CONTAINER,
                    cloud_backend_url,
                    public=True,
                    description="Managed container endpoint hosted by a cloud provider.",
                ),
                self._target(
                    "temporary-tunnel",
                    "Temporary Tunnel",
                    DeploymentTargetType.TEMPORARY_TUNNEL,
                    tunnel_backend_url,
                    public=True,
                    description="Short-lived tunnel endpoint for validation before production hosting.",
                ),
            ]
        }
        if self._active_target_id not in self._targets:
            self._active_target_id = "local-docker"
        self._sync_active_flags()

    def catalog(self) -> DeploymentTargetCatalog:
        """Return the full target catalog."""

        return DeploymentTargetCatalog(
            active_target_id=self._active_target_id,
            targets=list(self._targets.values()),
        )

    def active(self) -> DeploymentTarget:
        """Return the active target."""

        return self._targets[self._active_target_id]

    def activate(self, target_id: str) -> DeploymentTarget:
        """Activate one known target."""

        if target_id not in self._targets:
            raise ValueError(f"Deployment target is not registered: {target_id}")
        self._active_target_id = target_id
        self._sync_active_flags()
        return self.active()

    def validate(self, target_id: str) -> DeploymentTargetValidation:
        """Validate the health endpoints for one target."""

        target = self._targets.get(target_id)
        if target is None:
            raise ValueError(f"Deployment target is not registered: {target_id}")
        checked_at = datetime.now(UTC)
        if target.backend_url is None:
            validation = DeploymentTargetValidation(
                target_id=target.target_id,
                backend_url=None,
                status=DeploymentTargetStatus.NOT_CONFIGURED,
                checked_at=checked_at,
                checks=[
                    DeploymentTargetCheck(
                        endpoint="backend_url",
                        status=DeploymentTargetStatus.NOT_CONFIGURED,
                        detail="Deployment target does not have a backend_url.",
                    )
                ],
            )
            self._apply_validation(target, validation)
            return validation

        checks = [
            self._check_endpoint(target.backend_url, endpoint)
            for endpoint in target.health_endpoints
        ]
        status = (
            DeploymentTargetStatus.VALIDATED
            if all(check.status == DeploymentTargetStatus.VALIDATED for check in checks)
            else DeploymentTargetStatus.UNREACHABLE
        )
        validation = DeploymentTargetValidation(
            target_id=target.target_id,
            backend_url=target.backend_url,
            status=status,
            checked_at=checked_at,
            checks=checks,
        )
        self._apply_validation(target, validation)
        return validation

    def _check_endpoint(self, backend_url: str, endpoint: str) -> DeploymentTargetCheck:
        url = f"{backend_url.rstrip('/')}{endpoint}"
        request = Request(url, headers={"Origin": self._cors_origin})
        try:
            with urlopen(request, timeout=3) as response:
                status_code = response.status
        except HTTPError as exc:
            return DeploymentTargetCheck(
                endpoint=endpoint,
                status=DeploymentTargetStatus.UNREACHABLE,
                status_code=exc.code,
                detail=f"HTTP error from target: {exc.code}",
            )
        except (TimeoutError, URLError, OSError) as exc:
            return DeploymentTargetCheck(
                endpoint=endpoint,
                status=DeploymentTargetStatus.UNREACHABLE,
                detail=f"Target unreachable: {exc}",
            )
        if 200 <= status_code < 300:
            return DeploymentTargetCheck(
                endpoint=endpoint,
                status=DeploymentTargetStatus.VALIDATED,
                status_code=status_code,
                detail="Endpoint returned a successful response.",
            )
        return DeploymentTargetCheck(
            endpoint=endpoint,
            status=DeploymentTargetStatus.DEGRADED,
            status_code=status_code,
            detail=f"Endpoint returned non-success status: {status_code}",
        )

    def _apply_validation(
        self,
        target: DeploymentTarget,
        validation: DeploymentTargetValidation,
    ) -> None:
        self._targets[target.target_id] = target.model_copy(
            update={
                "status": validation.status,
                "last_validated_at": validation.checked_at,
            }
        )
        self._sync_active_flags()

    def _sync_active_flags(self) -> None:
        self._targets = {
            target_id: target.model_copy(update={"active": target_id == self._active_target_id})
            for target_id, target in self._targets.items()
        }

    @staticmethod
    def _target(
        target_id: str,
        label: str,
        target_type: DeploymentTargetType,
        backend_url: str | None,
        *,
        public: bool,
        description: str,
    ) -> DeploymentTarget:
        return DeploymentTarget(
            target_id=target_id,
            label=label,
            target_type=target_type,
            backend_url=backend_url.rstrip("/") if backend_url else None,
            public=public,
            status=(
                DeploymentTargetStatus.DEGRADED
                if backend_url
                else DeploymentTargetStatus.NOT_CONFIGURED
            ),
            description=description,
            health_endpoints=DEFAULT_HEALTH_ENDPOINTS,
        )
