"""Infrastructure provisioning adapters.

ADR references:
- ADR-0003: Project provisioning as a port.
- ADR-0007: NAS integration.
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0017: Project Provisioning Engine.
"""

from __future__ import annotations

import base64
import json
import re
import shutil
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from sqlalchemy import create_engine, text

from control_tower.application.provisioning_adapters import ProvisioningAdapterContext
from control_tower.domain.provisioning import (
    ProvisioningResourceType,
    ProvisioningStep,
    ProvisioningStepStatus,
)


class ReferenceProvisioningAdapter:
    """Adapter that registers controlled-plane references without external side effects."""

    def __init__(self, resource_type: ProvisioningResourceType, step_id: str, name: str, reference: str) -> None:
        self.resource_type = resource_type
        self._step_id = step_id
        self._name = name
        self._reference = reference

    def plan(self, context: ProvisioningAdapterContext) -> ProvisioningStep:
        """Return the reference step planned for execution."""

        return self._step(context, ProvisioningStepStatus.PLANNED)

    def execute(self, context: ProvisioningAdapterContext) -> ProvisioningStep:
        """Register the reference as successfully executed."""

        return self._step(context, ProvisioningStepStatus.SUCCEEDED)

    def _step(self, context: ProvisioningAdapterContext, status: ProvisioningStepStatus) -> ProvisioningStep:
        return ProvisioningStep(
            step_id=self._step_id,
            resource_type=self.resource_type,
            name=self._name,
            status=status,
            reference=self._reference.format(
                company_id=context.company_id,
                project_id=context.project_id,
                websig_slug=context.websig_slug,
                dashboard_id=context.dashboard_id,
            ),
        )


class WebSigFactoryTemplateProvisioningAdapter:
    """Provision a WEB SIG instance from the approved Factory Template."""

    resource_type = ProvisioningResourceType.WEB_SIG

    def __init__(
        self,
        template_path: str | None = None,
        output_root: str | None = None,
    ) -> None:
        self._template_path = Path(template_path).resolve() if template_path else None
        self._output_root = Path(output_root).resolve() if output_root else None

    def plan(self, context: ProvisioningAdapterContext) -> ProvisioningStep:
        """Return the WEB SIG template provisioning plan without filesystem side effects."""

        return self._step(context, ProvisioningStepStatus.PLANNED)

    def execute(self, context: ProvisioningAdapterContext) -> ProvisioningStep:
        """Create a project WEB SIG instance and write the provisioning contract."""

        if self._template_path is not None or self._output_root is not None:
            if self._template_path is None or self._output_root is None:
                raise ValueError("WEB SIG Factory template_path and output_root must be configured together")
            if not self._template_path.is_dir():
                raise ValueError(f"WEB SIG Factory template path does not exist: {self._template_path}")
            target = self._target(context)
            if target.exists():
                self._ensure_target_is_inside_output_root(target)
                shutil.rmtree(target)
            shutil.copytree(self._template_path, target, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            (target / "websig.config.json").write_text(
                json.dumps(self._config(context), indent=2, ensure_ascii=True),
                encoding="utf-8",
            )
        return self._step(context, ProvisioningStepStatus.SUCCEEDED)

    def _step(self, context: ProvisioningAdapterContext, status: ProvisioningStepStatus) -> ProvisioningStep:
        reference = str(self._target(context)) if self._output_root is not None else f"websig://{context.company_id}/{context.websig_slug}"
        return ProvisioningStep(
            step_id="websig-template",
            resource_type=self.resource_type,
            name="Provisionar WEB SIG Factory Template",
            status=status,
            reference=reference,
        )

    def _target(self, context: ProvisioningAdapterContext) -> Path:
        if self._output_root is None:
            return Path(f"{context.company_id}_{context.websig_slug}")
        return self._output_root / context.company_id / context.websig_slug

    def _ensure_target_is_inside_output_root(self, target: Path) -> None:
        if self._output_root is None:
            raise ValueError("WEB SIG Factory output root is not configured")
        output_root = self._output_root.resolve()
        resolved_target = target.resolve()
        if resolved_target == output_root or output_root not in resolved_target.parents:
            raise ValueError(f"Refusing to replace WEB SIG instance outside output root: {resolved_target}")

    @staticmethod
    def _config(context: ProvisioningAdapterContext) -> dict:
        return {
            "company_id": context.company_id,
            "program_id": None,
            "project_id": context.project_id,
            "websig_id": f"WEB-{context.company_id}-{context.project_id}",
            "websig_slug": context.websig_slug,
            "websig_url": context.websig_url,
            "postgis_schema": context.postgis_schema_name,
            "geoserver_workspace": context.geoserver_workspace,
            "nas_root_uri": context.nas_root_uri,
            "dashboard_id": context.dashboard_id,
            "enabled_modules": context.enabled_modules,
            "gis_services": {
                "wms_url": None,
                "wfs_url": None,
                "wmts_url": None,
                "vector_tiles_url": None,
            },
            "tower_boundary": {
                "control_tower_role": "governance_provisioning_monitoring",
                "websig_role": "project_operation",
                "geometry_editing_by_tower": False,
            },
        }


class PostGISProvisioningAdapter:
    """Provision a project PostGIS schema when a database URL is configured."""

    resource_type = ProvisioningResourceType.POSTGIS

    def __init__(self, database_url: str | None = None) -> None:
        self._database_url = database_url

    def plan(self, context: ProvisioningAdapterContext) -> ProvisioningStep:
        """Return the PostGIS schema creation plan."""

        return self._step(context, ProvisioningStepStatus.PLANNED)

    def execute(self, context: ProvisioningAdapterContext) -> ProvisioningStep:
        """Create a project schema in the configured PostGIS database."""

        if self._database_url is not None:
            schema_name = self._schema_name(context)
            engine = create_engine(self._database_url, future=True)
            with engine.begin() as connection:
                connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
        return self._step(context, ProvisioningStepStatus.SUCCEEDED)

    def _step(self, context: ProvisioningAdapterContext, status: ProvisioningStepStatus) -> ProvisioningStep:
        return ProvisioningStep(
            step_id="postgis",
            resource_type=self.resource_type,
            name="Create Base PostGIS",
            status=status,
            reference=f"postgis://{context.company_id}/{context.postgis_schema_name}",
        )

    @staticmethod
    def _schema_name(context: ProvisioningAdapterContext) -> str:
        raw = context.postgis_schema_name.lower()
        return re.sub(r"[^a-z0-9_]+", "_", raw).strip("_")


class NasProvisioningAdapter:
    """Provision a project NAS root when a filesystem root is configured."""

    resource_type = ProvisioningResourceType.NAS

    def __init__(self, root_path: str | None = None) -> None:
        self._root_path = Path(root_path).resolve() if root_path else None

    def plan(self, context: ProvisioningAdapterContext) -> ProvisioningStep:
        """Return the NAS root creation plan."""

        return self._step(context, ProvisioningStepStatus.PLANNED)

    def execute(self, context: ProvisioningAdapterContext) -> ProvisioningStep:
        """Create the project NAS root when configured."""

        if self._root_path is not None:
            self._target(context).mkdir(parents=True, exist_ok=True)
        return self._step(context, ProvisioningStepStatus.SUCCEEDED)

    def _step(self, context: ProvisioningAdapterContext, status: ProvisioningStepStatus) -> ProvisioningStep:
        return ProvisioningStep(
            step_id="nas",
            resource_type=self.resource_type,
            name="Create Espacio NAS",
            status=status,
            reference=context.nas_root_uri,
        )

    def _target(self, context: ProvisioningAdapterContext) -> Path:
        if self._root_path is None:
            raise ValueError("NAS root path is not configured")
        return self._root_path / context.company_id / context.project_id / "websig"


class DocumentStructureProvisioningAdapter:
    """Provision project document folders under the configured NAS root."""

    resource_type = ProvisioningResourceType.DOCUMENT_STRUCTURE

    def __init__(self, root_path: str | None = None) -> None:
        self._root_path = Path(root_path).resolve() if root_path else None

    def plan(self, context: ProvisioningAdapterContext) -> ProvisioningStep:
        """Return the document structure creation plan."""

        return self._step(context, ProvisioningStepStatus.PLANNED)

    def execute(self, context: ProvisioningAdapterContext) -> ProvisioningStep:
        """Create project document folders when a NAS root is configured."""

        if self._root_path is not None:
            base = self._root_path / context.company_id / context.project_id / "documents"
            for folder in context.document_structure:
                (base / folder).mkdir(parents=True, exist_ok=True)
        return self._step(context, ProvisioningStepStatus.SUCCEEDED)

    def _step(self, context: ProvisioningAdapterContext, status: ProvisioningStepStatus) -> ProvisioningStep:
        return ProvisioningStep(
            step_id="documents",
            resource_type=self.resource_type,
            name="Create estructura documental",
            status=status,
            reference=",".join(context.document_structure),
        )


class GeoServerProvisioningAdapter:
    """Provision or validate a GeoServer workspace when endpoint details are configured."""

    resource_type = ProvisioningResourceType.GEOSERVER

    def __init__(
        self,
        base_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/") if base_url else None
        self._username = username
        self._password = password

    def plan(self, context: ProvisioningAdapterContext) -> ProvisioningStep:
        """Return the GeoServer workspace registration plan."""

        return self._step(context, ProvisioningStepStatus.PLANNED)

    def execute(self, context: ProvisioningAdapterContext) -> ProvisioningStep:
        """Create a GeoServer workspace when endpoint details are configured."""

        if self._base_url is not None:
            workspace = self._workspace(context)
            payload = f"<workspace><name>{workspace}</name></workspace>".encode("utf-8")
            request = Request(
                f"{self._base_url}/rest/workspaces",
                data=payload,
                method="POST",
                headers={"Content-Type": "text/xml"},
            )
            if self._username and self._password:
                token = base64.b64encode(f"{self._username}:{self._password}".encode("utf-8")).decode("ascii")
                request.add_header("Authorization", f"Basic {token}")
            try:
                with urlopen(request, timeout=10):
                    pass
            except HTTPError as exc:
                if exc.code != 409:
                    raise
        return self._step(context, ProvisioningStepStatus.SUCCEEDED)

    def _step(self, context: ProvisioningAdapterContext, status: ProvisioningStepStatus) -> ProvisioningStep:
        return ProvisioningStep(
            step_id="geoserver",
            resource_type=self.resource_type,
            name="Registrar GeoServer",
            status=status,
            reference=f"geoserver://workspace/{self._workspace(context)}",
        )

    @staticmethod
    def _workspace(context: ProvisioningAdapterContext) -> str:
        return re.sub(r"[^A-Za-z0-9_]+", "_", context.geoserver_workspace)


class CatalogProvisioningAdapter:
    """Register requested project catalogs."""

    resource_type = ProvisioningResourceType.CATALOG

    def plan(self, context: ProvisioningAdapterContext) -> ProvisioningStep:
        """Return the catalog registration plan."""

        return self._step(context, ProvisioningStepStatus.PLANNED)

    def execute(self, context: ProvisioningAdapterContext) -> ProvisioningStep:
        """Register catalog references as executed."""

        return self._step(context, ProvisioningStepStatus.SUCCEEDED)

    def _step(self, context: ProvisioningAdapterContext, status: ProvisioningStepStatus) -> ProvisioningStep:
        return ProvisioningStep(
            step_id="catalogs",
            resource_type=self.resource_type,
            name="Crear Catalogos",
            status=status,
            reference=",".join(context.catalogs),
        )


def default_project_stack_adapters(
    nas_root: str | None = None,
    postgis_database_url: str | None = None,
    geoserver_url: str | None = None,
    geoserver_user: str | None = None,
    geoserver_password: str | None = None,
    websig_factory_template_path: str | None = None,
    websig_factory_output_root: str | None = None,
) -> list:
    """Build the default adapter set for Project Provisioning Engine."""

    return [
        WebSigFactoryTemplateProvisioningAdapter(
            websig_factory_template_path,
            websig_factory_output_root,
        ),
        PostGISProvisioningAdapter(postgis_database_url),
        NasProvisioningAdapter(nas_root),
        DocumentStructureProvisioningAdapter(nas_root),
        GeoServerProvisioningAdapter(geoserver_url, geoserver_user, geoserver_password),
        ReferenceProvisioningAdapter(
            ProvisioningResourceType.DASHBOARD,
            "dashboard",
            "Crear Dashboard",
            "dashboard://{dashboard_id}",
        ),
        CatalogProvisioningAdapter(),
    ]
