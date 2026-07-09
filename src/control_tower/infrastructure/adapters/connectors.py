"""Real controlled infrastructure connectors.

ADR references:
- ADR-0007: NAS integration.
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0010: Google Workspace transition integration.
- ADR-0021: DevSecOps operating model.
"""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from sqlalchemy import create_engine, text

from control_tower.application.infrastructure_connectors import (
    InfrastructureConnectorAction,
    InfrastructureConnectorKind,
    InfrastructureConnectorRequest,
    InfrastructureConnectorResult,
    InfrastructureConnectorStatus,
)


class PostGISInfrastructureConnector:
    """PostGIS connector for health checks and controlled schema creation."""

    kind = InfrastructureConnectorKind.POSTGIS

    def __init__(self, database_url: str | None = None) -> None:
        self._database_url = database_url

    def health(self) -> InfrastructureConnectorResult:
        """Run a lightweight database health check."""

        if not self._database_url:
            return self._result(InfrastructureConnectorAction.HEALTH, InfrastructureConnectorStatus.MISCONFIGURED, False, "CONTROL_TOWER_POSTGIS_DATABASE_URL is not configured.")
        try:
            engine = create_engine(self._database_url, future=True)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except Exception as exc:  # pragma: no cover - exercised with mocks in unit tests
            return self._result(InfrastructureConnectorAction.HEALTH, InfrastructureConnectorStatus.UNHEALTHY, True, str(exc))
        return self._result(InfrastructureConnectorAction.HEALTH, InfrastructureConnectorStatus.HEALTHY, True, "PostGIS connection is reachable.")

    def validate(self) -> InfrastructureConnectorResult:
        """Validate PostGIS connector configuration."""

        if not self._database_url:
            return self._result(InfrastructureConnectorAction.VALIDATE, InfrastructureConnectorStatus.MISCONFIGURED, False, "Missing PostGIS database URL.")
        return self._result(InfrastructureConnectorAction.VALIDATE, InfrastructureConnectorStatus.CONFIGURED, True, "PostGIS database URL is configured.")

    def dry_run(self, request: InfrastructureConnectorRequest) -> InfrastructureConnectorResult:
        """Plan schema provisioning without side effects."""

        schema = self._schema_name(request)
        return self._result(
            InfrastructureConnectorAction.DRY_RUN,
            InfrastructureConnectorStatus.PLANNED,
            bool(self._database_url),
            f"PostGIS schema would be ensured: {schema}.",
            reference=f"postgis://schema/{schema}",
            metadata={"schema": schema},
        )

    def execute(self, request: InfrastructureConnectorRequest) -> InfrastructureConnectorResult:
        """Create a PostGIS schema when configured."""

        if not self._database_url:
            return self._result(InfrastructureConnectorAction.EXECUTE, InfrastructureConnectorStatus.MISCONFIGURED, False, "Missing PostGIS database URL.")
        schema = self._schema_name(request)
        try:
            engine = create_engine(self._database_url, future=True)
            with engine.begin() as connection:
                connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
        except Exception as exc:  # pragma: no cover - exercised with mocks in unit tests
            return self._result(InfrastructureConnectorAction.EXECUTE, InfrastructureConnectorStatus.FAILED, True, str(exc))
        return self._result(
            InfrastructureConnectorAction.EXECUTE,
            InfrastructureConnectorStatus.EXECUTED,
            True,
            f"PostGIS schema ensured: {schema}.",
            reference=f"postgis://schema/{schema}",
            metadata={"schema": schema},
        )

    @staticmethod
    def _schema_name(request: InfrastructureConnectorRequest) -> str:
        raw = request.target.get("schema_name") or "_".join(part for part in [request.company_id, request.project_id] if part) or "control_tower"
        return re.sub(r"[^a-zA-Z0-9_]+", "_", raw).strip("_").lower()

    def _result(
        self,
        action: InfrastructureConnectorAction,
        status: InfrastructureConnectorStatus,
        configured: bool,
        detail: str,
        reference: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> InfrastructureConnectorResult:
        return InfrastructureConnectorResult(
            connector=self.kind,
            action=action,
            status=status,
            configured=configured,
            reference=reference,
            detail=detail,
            metadata=metadata or {},
        )


class GeoServerInfrastructureConnector:
    """GeoServer REST connector for health checks and controlled workspace creation."""

    kind = InfrastructureConnectorKind.GEOSERVER

    def __init__(self, base_url: str | None = None, username: str | None = None, password: str | None = None) -> None:
        self._base_url = base_url.rstrip("/") if base_url else None
        self._username = username
        self._password = password

    def health(self) -> InfrastructureConnectorResult:
        """Check GeoServer REST availability."""

        if not self._base_url:
            return self._result(InfrastructureConnectorAction.HEALTH, InfrastructureConnectorStatus.MISCONFIGURED, False, "CONTROL_TOWER_GEOSERVER_URL is not configured.")
        try:
            self._open(Request(f"{self._base_url}/rest/workspaces", method="GET"))
        except (HTTPError, URLError, TimeoutError) as exc:
            return self._result(InfrastructureConnectorAction.HEALTH, InfrastructureConnectorStatus.UNHEALTHY, True, str(exc))
        return self._result(InfrastructureConnectorAction.HEALTH, InfrastructureConnectorStatus.HEALTHY, True, "GeoServer REST endpoint is reachable.")

    def validate(self) -> InfrastructureConnectorResult:
        """Validate GeoServer connector configuration."""

        if not self._base_url:
            return self._result(InfrastructureConnectorAction.VALIDATE, InfrastructureConnectorStatus.MISCONFIGURED, False, "Missing GeoServer base URL.")
        if not self._username or not self._password:
            return self._result(InfrastructureConnectorAction.VALIDATE, InfrastructureConnectorStatus.CONFIGURED, True, "GeoServer URL configured; credentials not configured.")
        return self._result(InfrastructureConnectorAction.VALIDATE, InfrastructureConnectorStatus.CONFIGURED, True, "GeoServer URL and credentials are configured.")

    def dry_run(self, request: InfrastructureConnectorRequest) -> InfrastructureConnectorResult:
        """Plan workspace creation without side effects."""

        workspace = self._workspace(request)
        return self._result(
            InfrastructureConnectorAction.DRY_RUN,
            InfrastructureConnectorStatus.PLANNED,
            bool(self._base_url),
            f"GeoServer workspace would be ensured: {workspace}.",
            reference=f"geoserver://workspace/{workspace}",
            metadata={"workspace": workspace},
        )

    def execute(self, request: InfrastructureConnectorRequest) -> InfrastructureConnectorResult:
        """Create a GeoServer workspace through REST when configured."""

        if not self._base_url:
            return self._result(InfrastructureConnectorAction.EXECUTE, InfrastructureConnectorStatus.MISCONFIGURED, False, "Missing GeoServer base URL.")
        workspace = self._workspace(request)
        payload = f"<workspace><name>{workspace}</name></workspace>".encode("utf-8")
        api_request = Request(
            f"{self._base_url}/rest/workspaces",
            data=payload,
            method="POST",
            headers={"Content-Type": "text/xml"},
        )
        try:
            self._open(api_request)
        except HTTPError as exc:
            if exc.code != 409:
                return self._result(InfrastructureConnectorAction.EXECUTE, InfrastructureConnectorStatus.FAILED, True, str(exc))
        except (URLError, TimeoutError) as exc:
            return self._result(InfrastructureConnectorAction.EXECUTE, InfrastructureConnectorStatus.FAILED, True, str(exc))
        return self._result(
            InfrastructureConnectorAction.EXECUTE,
            InfrastructureConnectorStatus.EXECUTED,
            True,
            f"GeoServer workspace ensured: {workspace}.",
            reference=f"geoserver://workspace/{workspace}",
            metadata={"workspace": workspace},
        )

    def _open(self, request: Request) -> None:
        if self._username and self._password:
            token = base64.b64encode(f"{self._username}:{self._password}".encode("utf-8")).decode("ascii")
            request.add_header("Authorization", f"Basic {token}")
        with urlopen(request, timeout=10):
            pass

    @staticmethod
    def _workspace(request: InfrastructureConnectorRequest) -> str:
        raw = request.target.get("workspace") or "_".join(part for part in [request.company_id, request.project_id] if part) or "control_tower"
        return re.sub(r"[^a-zA-Z0-9_]+", "_", raw).strip("_")

    def _result(
        self,
        action: InfrastructureConnectorAction,
        status: InfrastructureConnectorStatus,
        configured: bool,
        detail: str,
        reference: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> InfrastructureConnectorResult:
        return InfrastructureConnectorResult(
            connector=self.kind,
            action=action,
            status=status,
            configured=configured,
            reference=reference,
            detail=detail,
            metadata=metadata or {},
        )


class NasFilesystemInfrastructureConnector:
    """Filesystem NAS connector for controlled directory validation and creation."""

    kind = InfrastructureConnectorKind.NAS

    def __init__(self, root_path: str | None = None) -> None:
        self._root_path = Path(root_path).resolve() if root_path else None

    def health(self) -> InfrastructureConnectorResult:
        """Check NAS filesystem root availability."""

        if self._root_path is None:
            return self._result(InfrastructureConnectorAction.HEALTH, InfrastructureConnectorStatus.MISCONFIGURED, False, "CONTROL_TOWER_NAS_ROOT is not configured.")
        if not self._root_path.exists():
            return self._result(InfrastructureConnectorAction.HEALTH, InfrastructureConnectorStatus.UNHEALTHY, True, f"NAS root does not exist: {self._root_path}.")
        return self._result(InfrastructureConnectorAction.HEALTH, InfrastructureConnectorStatus.HEALTHY, True, "NAS root is reachable.", reference=str(self._root_path))

    def validate(self) -> InfrastructureConnectorResult:
        """Validate NAS connector configuration."""

        if self._root_path is None:
            return self._result(InfrastructureConnectorAction.VALIDATE, InfrastructureConnectorStatus.MISCONFIGURED, False, "Missing NAS root path.")
        return self._result(InfrastructureConnectorAction.VALIDATE, InfrastructureConnectorStatus.CONFIGURED, True, "NAS root path is configured.", reference=str(self._root_path))

    def dry_run(self, request: InfrastructureConnectorRequest) -> InfrastructureConnectorResult:
        """Plan directory creation without side effects."""

        target = self._target(request)
        return self._result(
            InfrastructureConnectorAction.DRY_RUN,
            InfrastructureConnectorStatus.PLANNED,
            self._root_path is not None,
            f"NAS directory would be ensured: {target}.",
            reference=str(target),
        )

    def execute(self, request: InfrastructureConnectorRequest) -> InfrastructureConnectorResult:
        """Create a project NAS directory when configured."""

        if self._root_path is None:
            return self._result(InfrastructureConnectorAction.EXECUTE, InfrastructureConnectorStatus.MISCONFIGURED, False, "Missing NAS root path.")
        target = self._target(request)
        self._ensure_inside_root(target)
        target.mkdir(parents=True, exist_ok=True)
        return self._result(
            InfrastructureConnectorAction.EXECUTE,
            InfrastructureConnectorStatus.EXECUTED,
            True,
            f"NAS directory ensured: {target}.",
            reference=str(target),
        )

    def _target(self, request: InfrastructureConnectorRequest) -> Path:
        if self._root_path is None:
            return Path(request.target.get("path", "unconfigured"))
        parts = [
            request.target.get("relative_path"),
            request.company_id,
            request.project_id,
            request.target.get("folder", "websig"),
        ]
        safe_parts = [re.sub(r"[^a-zA-Z0-9_.-]+", "_", part) for part in parts if part]
        return self._root_path.joinpath(*safe_parts)

    def _ensure_inside_root(self, target: Path) -> None:
        if self._root_path is None:
            raise ValueError("NAS root path is not configured")
        root = self._root_path.resolve()
        resolved = target.resolve()
        if resolved != root and root not in resolved.parents:
            raise ValueError(f"Refusing to create NAS path outside root: {resolved}")

    def _result(
        self,
        action: InfrastructureConnectorAction,
        status: InfrastructureConnectorStatus,
        configured: bool,
        detail: str,
        reference: str | None = None,
    ) -> InfrastructureConnectorResult:
        return InfrastructureConnectorResult(
            connector=self.kind,
            action=action,
            status=status,
            configured=configured,
            reference=reference,
            detail=detail,
        )


class GoogleDriveInfrastructureConnector:
    """Google Drive REST connector for governed folder checks and creation."""

    kind = InfrastructureConnectorKind.GOOGLE_DRIVE

    def __init__(
        self,
        root_id: str | None = None,
        access_token: str | None = None,
        credentials_file: str | None = None,
    ) -> None:
        self._root_id = root_id
        self._access_token = access_token
        self._credentials_file = Path(credentials_file).resolve() if credentials_file else None

    def health(self) -> InfrastructureConnectorResult:
        """Check Google Drive configuration and optional REST availability."""

        validation = self.validate()
        if validation.status == InfrastructureConnectorStatus.MISCONFIGURED:
            return validation.model_copy(update={"action": InfrastructureConnectorAction.HEALTH})
        if not self._access_token:
            return self._result(InfrastructureConnectorAction.HEALTH, InfrastructureConnectorStatus.CONFIGURED, True, "Google Drive configuration is present; access token is not configured for live REST check.")
        try:
            self._open(Request(f"https://www.googleapis.com/drive/v3/files/{self._root_id}?fields=id,name", method="GET"))
        except (HTTPError, URLError, TimeoutError) as exc:
            return self._result(InfrastructureConnectorAction.HEALTH, InfrastructureConnectorStatus.UNHEALTHY, True, str(exc))
        return self._result(InfrastructureConnectorAction.HEALTH, InfrastructureConnectorStatus.HEALTHY, True, "Google Drive root folder is reachable.", reference=f"gdrive://folders/{self._root_id}")

    def validate(self) -> InfrastructureConnectorResult:
        """Validate Google Drive connector configuration without exposing secrets."""

        if not self._root_id:
            return self._result(InfrastructureConnectorAction.VALIDATE, InfrastructureConnectorStatus.MISCONFIGURED, False, "CONTROL_TOWER_GOOGLE_DRIVE_ROOT_ID is not configured.")
        if self._credentials_file is not None and not self._credentials_file.exists():
            return self._result(InfrastructureConnectorAction.VALIDATE, InfrastructureConnectorStatus.MISCONFIGURED, False, "Google Drive credentials file does not exist.")
        return self._result(InfrastructureConnectorAction.VALIDATE, InfrastructureConnectorStatus.CONFIGURED, True, "Google Drive root is configured.", reference=f"gdrive://folders/{self._root_id}")

    def dry_run(self, request: InfrastructureConnectorRequest) -> InfrastructureConnectorResult:
        """Plan Google Drive folder creation without side effects."""

        folder = self._folder_name(request)
        return self._result(
            InfrastructureConnectorAction.DRY_RUN,
            InfrastructureConnectorStatus.PLANNED,
            bool(self._root_id),
            f"Google Drive folder would be ensured under the configured root: {folder}.",
            reference=f"gdrive://folders/{self._root_id}/{folder}" if self._root_id else None,
            metadata={"folder": folder},
        )

    def execute(self, request: InfrastructureConnectorRequest) -> InfrastructureConnectorResult:
        """Create a Google Drive folder when token and root are configured."""

        if not self._root_id:
            return self._result(InfrastructureConnectorAction.EXECUTE, InfrastructureConnectorStatus.MISCONFIGURED, False, "Missing Google Drive root id.")
        if not self._access_token:
            return self._result(InfrastructureConnectorAction.EXECUTE, InfrastructureConnectorStatus.MISCONFIGURED, True, "Missing Google Drive access token for live folder creation.")
        folder = self._folder_name(request)
        payload = json.dumps(
            {
                "name": folder,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [self._root_id],
            }
        ).encode("utf-8")
        api_request = Request(
            "https://www.googleapis.com/drive/v3/files",
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            self._open(api_request)
        except (HTTPError, URLError, TimeoutError) as exc:
            return self._result(InfrastructureConnectorAction.EXECUTE, InfrastructureConnectorStatus.FAILED, True, str(exc))
        return self._result(
            InfrastructureConnectorAction.EXECUTE,
            InfrastructureConnectorStatus.EXECUTED,
            True,
            f"Google Drive folder creation requested: {folder}.",
            reference=f"gdrive://folders/{self._root_id}/{folder}",
            metadata={"folder": folder},
        )

    def _open(self, request: Request) -> None:
        if self._access_token:
            request.add_header("Authorization", f"Bearer {self._access_token}")
        with urlopen(request, timeout=10):
            pass

    @staticmethod
    def _folder_name(request: InfrastructureConnectorRequest) -> str:
        raw = request.target.get("folder") or "-".join(part for part in [request.company_id, request.project_id] if part) or "control-tower"
        return re.sub(r"[^a-zA-Z0-9_. -]+", "_", raw).strip()

    def _result(
        self,
        action: InfrastructureConnectorAction,
        status: InfrastructureConnectorStatus,
        configured: bool,
        detail: str,
        reference: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> InfrastructureConnectorResult:
        return InfrastructureConnectorResult(
            connector=self.kind,
            action=action,
            status=status,
            configured=configured,
            reference=reference,
            detail=detail,
            metadata=metadata or {},
        )


def default_infrastructure_connectors(
    postgis_database_url: str | None = None,
    geoserver_url: str | None = None,
    geoserver_user: str | None = None,
    geoserver_password: str | None = None,
    nas_root: str | None = None,
    google_drive_root_id: str | None = None,
    google_drive_access_token: str | None = None,
    google_credentials_file: str | None = None,
) -> list:
    """Build controlled infrastructure connectors from environment configuration."""

    return [
        PostGISInfrastructureConnector(postgis_database_url),
        GeoServerInfrastructureConnector(geoserver_url, geoserver_user, geoserver_password),
        NasFilesystemInfrastructureConnector(nas_root),
        GoogleDriveInfrastructureConnector(
            google_drive_root_id,
            google_drive_access_token,
            google_credentials_file,
        ),
    ]
