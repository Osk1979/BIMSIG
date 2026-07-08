"""Corporate GIS administration application service.

ADR references:
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0015: Tower vs WEB SIG boundary.
- ADR-0023: Corporate GIS administration.
"""

from control_tower.application.enterprise_service import CompanyService
from control_tower.application.portfolio_service import PortfolioService
from control_tower.application.repositories import AuditEventRepository, CorporateGisRepository
from control_tower.domain.audit import AuditEvent
from control_tower.domain.gis import (
    GeoServerDatastore,
    GeoServerLayer,
    GeoServerWorkspace,
    GisResourceStatus,
    GisResourceValidation,
    PostgisSchema,
    ProjectGisBinding,
    ProjectGisResources,
)


class CorporateGisService:
    """Govern corporate GIS infrastructure references without operating WEB SIG layers."""

    def __init__(
        self,
        repository: CorporateGisRepository,
        companies: CompanyService,
        portfolio: PortfolioService,
        audit: AuditEventRepository | None = None,
    ) -> None:
        self._repository = repository
        self._companies = companies
        self._portfolio = portfolio
        self._audit = audit

    def register_postgis_schema(self, schema: PostgisSchema) -> PostgisSchema:
        """Register a project PostGIS schema reference."""

        self._require_company_project(schema.company_id, schema.project_id)
        saved = self._repository.save_postgis_schema(schema)
        self._audit_event("gis.postgis_schema_registered", "postgis_schema", saved.schema_id)
        return saved

    def list_postgis_schemas(self, company_id: str, project_id: str | None = None) -> list[PostgisSchema]:
        """List PostGIS schema references by company and optional project."""

        self._require_company(company_id)
        if project_id is not None:
            self._require_company_project(company_id, project_id)
        return self._repository.list_postgis_schemas(company_id, project_id)

    def register_workspace(self, workspace: GeoServerWorkspace) -> GeoServerWorkspace:
        """Register a GeoServer workspace reference."""

        self._require_company_project(workspace.company_id, workspace.project_id)
        saved = self._repository.save_workspace(workspace)
        self._audit_event("gis.workspace_registered", "geoserver_workspace", saved.workspace_id)
        return saved

    def list_workspaces(self, company_id: str, project_id: str | None = None) -> list[GeoServerWorkspace]:
        """List GeoServer workspace references by company and optional project."""

        self._require_company(company_id)
        if project_id is not None:
            self._require_company_project(company_id, project_id)
        return self._repository.list_workspaces(company_id, project_id)

    def register_datastore(self, datastore: GeoServerDatastore) -> GeoServerDatastore:
        """Register a GeoServer datastore reference."""

        self._require_company_project(datastore.company_id, datastore.project_id)
        workspace = self._repository.get_workspace(datastore.workspace_id)
        if workspace is None or workspace.company_id != datastore.company_id:
            raise ValueError(f"GeoServer workspace is not registered: {datastore.workspace_id}")
        schema = self._repository.get_postgis_schema(datastore.postgis_schema_id)
        if schema is None or schema.company_id != datastore.company_id:
            raise ValueError(f"PostGIS schema is not registered: {datastore.postgis_schema_id}")
        saved = self._repository.save_datastore(datastore)
        self._audit_event("gis.datastore_registered", "geoserver_datastore", saved.datastore_id)
        return saved

    def list_datastores(self, company_id: str, project_id: str | None = None) -> list[GeoServerDatastore]:
        """List GeoServer datastore references by company and optional project."""

        self._require_company(company_id)
        if project_id is not None:
            self._require_company_project(company_id, project_id)
        return self._repository.list_datastores(company_id, project_id)

    def register_layer(self, layer: GeoServerLayer) -> GeoServerLayer:
        """Register a GeoServer layer reference."""

        self._require_company_project(layer.company_id, layer.project_id)
        workspace = self._repository.get_workspace(layer.workspace_id)
        datastore = self._repository.get_datastore(layer.datastore_id)
        if workspace is None or workspace.company_id != layer.company_id:
            raise ValueError(f"GeoServer workspace is not registered: {layer.workspace_id}")
        if datastore is None or datastore.company_id != layer.company_id:
            raise ValueError(f"GeoServer datastore is not registered: {layer.datastore_id}")
        if layer.wms_url is None and layer.wfs_url is None:
            raise ValueError("Layer must expose at least one WMS or WFS reference")
        saved = self._repository.save_layer(layer)
        self._audit_event("gis.layer_registered", "geoserver_layer", saved.layer_id)
        return saved

    def list_layers(self, company_id: str, project_id: str | None = None) -> list[GeoServerLayer]:
        """List GeoServer layer references by company and optional project."""

        self._require_company(company_id)
        if project_id is not None:
            self._require_company_project(company_id, project_id)
        return self._repository.list_layers(company_id, project_id)

    def bind_project_resources(self, binding: ProjectGisBinding) -> ProjectGisBinding:
        """Bind one project to its corporate GIS infrastructure references."""

        self._require_company_project(binding.company_id, binding.project_id)
        schema = self._repository.get_postgis_schema(binding.postgis_schema_id)
        workspace = self._repository.get_workspace(binding.geoserver_workspace_id)
        if schema is None or schema.project_id != binding.project_id:
            raise ValueError(f"PostGIS schema is not registered for project: {binding.postgis_schema_id}")
        if workspace is None or workspace.project_id != binding.project_id:
            raise ValueError(
                f"GeoServer workspace is not registered for project: {binding.geoserver_workspace_id}"
            )
        saved = self._repository.save_binding(binding)
        self._audit_event("gis.project_bound", "project_gis_binding", saved.binding_id)
        return saved

    def project_resources(self, company_id: str, project_id: str) -> ProjectGisResources:
        """Return corporate GIS resources for one project."""

        self._require_company_project(company_id, project_id)
        binding = self._repository.get_binding(company_id, project_id)
        schema = None
        workspace = None
        if binding is not None:
            schema = self._repository.get_postgis_schema(binding.postgis_schema_id)
            workspace = self._repository.get_workspace(binding.geoserver_workspace_id)
        return ProjectGisResources(
            company_id=company_id,
            project_id=project_id,
            binding=binding,
            postgis_schema=schema,
            geoserver_workspace=workspace,
            datastores=self._repository.list_datastores(company_id, project_id),
            layers=self._repository.list_layers(company_id, project_id),
        )

    def validate_project_resources(self, company_id: str, project_id: str) -> list[GisResourceValidation]:
        """Validate corporate GIS registry consistency for one project."""

        resources = self.project_resources(company_id, project_id)
        results: list[GisResourceValidation] = []
        if resources.binding is None:
            return [
                GisResourceValidation(
                    resource_type="project_gis_binding",
                    resource_id=project_id,
                    valid=False,
                    detail="Project has no corporate GIS binding",
                )
            ]
        results.append(
            self._validation(
                "postgis_schema",
                resources.binding.postgis_schema_id,
                resources.postgis_schema is not None
                and resources.postgis_schema.database_ref.startswith("postgis://"),
                "PostGIS schema reference is registered",
            )
        )
        results.append(
            self._validation(
                "geoserver_workspace",
                resources.binding.geoserver_workspace_id,
                resources.geoserver_workspace is not None
                and resources.geoserver_workspace.geoserver_url.startswith(("http://", "https://")),
                "GeoServer workspace reference is registered",
            )
        )
        for datastore in resources.datastores:
            results.append(
                self._validation(
                    "geoserver_datastore",
                    datastore.datastore_id,
                    datastore.workspace_id == resources.binding.geoserver_workspace_id
                    and datastore.postgis_schema_id == resources.binding.postgis_schema_id,
                    "Datastore links the bound workspace and PostGIS schema",
                )
            )
        for layer in resources.layers:
            results.append(
                self._validation(
                    "geoserver_layer",
                    layer.layer_id,
                    layer.workspace_id == resources.binding.geoserver_workspace_id
                    and (layer.wms_url is not None or layer.wfs_url is not None),
                    "Layer has WMS or WFS reference in the bound workspace",
                )
            )
        return results

    def mark_validated(self, company_id: str, project_id: str) -> ProjectGisResources:
        """Mark resources as validated when basic registry checks pass."""

        validations = self.validate_project_resources(company_id, project_id)
        if not validations or any(not validation.valid for validation in validations):
            raise ValueError("Corporate GIS resources are not valid")
        resources = self.project_resources(company_id, project_id)
        if resources.postgis_schema is not None:
            resources.postgis_schema.status = GisResourceStatus.VALIDATED
            self._repository.save_postgis_schema(resources.postgis_schema)
        if resources.geoserver_workspace is not None:
            resources.geoserver_workspace.status = GisResourceStatus.VALIDATED
            self._repository.save_workspace(resources.geoserver_workspace)
        for datastore in resources.datastores:
            datastore.status = GisResourceStatus.VALIDATED
            self._repository.save_datastore(datastore)
        for layer in resources.layers:
            layer.status = GisResourceStatus.VALIDATED
            self._repository.save_layer(layer)
        if resources.binding is not None:
            resources.binding.status = GisResourceStatus.VALIDATED
            self._repository.save_binding(resources.binding)
        self._audit_event("gis.resources_validated", "project", project_id)
        return self.project_resources(company_id, project_id)

    def _require_company(self, company_id: str) -> None:
        if not self._companies.exists(company_id):
            raise ValueError(f"Company is not registered: {company_id}")

    def _require_company_project(self, company_id: str, project_id: str) -> None:
        self._require_company(company_id)
        if self._portfolio.get_project_for_company(company_id, project_id) is None:
            raise ValueError(f"Project is not registered for company {company_id}: {project_id}")

    @staticmethod
    def _validation(
        resource_type: str,
        resource_id: str,
        valid: bool,
        success_detail: str,
    ) -> GisResourceValidation:
        return GisResourceValidation(
            resource_type=resource_type,
            resource_id=resource_id,
            valid=valid,
            detail=success_detail if valid else f"{resource_type} {resource_id} is invalid",
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
