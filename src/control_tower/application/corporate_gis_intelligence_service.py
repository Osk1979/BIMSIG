"""Corporate GIS Intelligence application service.

ADR references:
- ADR-0009: GeoServer integration.
- ADR-0010: Google Workspace transition integration.
- ADR-0011: Deployment strategy.
- ADR-0013: Corporate GIS Intelligence.
- ADR-0015: Tower vs WEB SIG operational boundary.
"""

from control_tower.application.enterprise_service import CompanyService
from control_tower.application.portfolio_service import PortfolioService
from control_tower.application.repositories import AuditEventRepository, CorporateGisIntelligenceRepository
from control_tower.domain.audit import AuditEvent
from control_tower.domain.corporate_gis_intelligence import (
    CorporateGisIntelligenceMap,
    CorporateGisSource,
    CorporateGisSummary,
    CorporateLayer,
    CorporateLayerStatus,
    CorporateLayerType,
    ProjectSpatialIndicator,
)


class CorporateGisIntelligenceService:
    """Consolidates published WEB SIG GIS references for corporate analysis."""

    def __init__(
        self,
        repository: CorporateGisIntelligenceRepository,
        companies: CompanyService,
        portfolio: PortfolioService,
        audit: AuditEventRepository | None = None,
    ) -> None:
        self._repository = repository
        self._companies = companies
        self._portfolio = portfolio
        self._audit = audit

    def register_source(self, source: CorporateGisSource) -> CorporateGisSource:
        """Register a published GIS source from a project WEB SIG."""

        self._require_company_project(source.company_id, source.project_id)
        project = self._portfolio.get_project_for_company(source.company_id, source.project_id)
        if source.program_id is not None and project is not None and source.program_id != project.program_id:
            raise ValueError("GIS source program_id must match project program_id")
        saved = self._repository.save_source(source)
        self._audit_event("gis_intelligence.source_registered", "corporate_gis_source", saved.source_id)
        return saved

    def list_sources(self, company_id: str, project_id: str | None = None) -> list[CorporateGisSource]:
        """List GIS sources by company and optional project."""

        self._require_company(company_id)
        if project_id is not None:
            self._require_company_project(company_id, project_id)
        return self._repository.list_sources(company_id, project_id)

    def register_layer(self, layer: CorporateLayer) -> CorporateLayer:
        """Register a corporate layer derived from a WEB SIG GIS source."""

        self._require_company_project(layer.company_id, layer.project_id)
        source = self._repository.get_source(layer.source_id)
        if source is None or source.company_id != layer.company_id or source.project_id != layer.project_id:
            raise ValueError(f"Corporate GIS source is not registered for project: {layer.source_id}")
        if source.layer_type != layer.layer_type:
            raise ValueError("Corporate layer type must match source layer_type")
        saved = self._repository.save_layer(layer)
        self._audit_event("gis_intelligence.layer_registered", "corporate_layer", saved.layer_id)
        return saved

    def list_layers(self, company_id: str, project_id: str | None = None) -> list[CorporateLayer]:
        """List corporate layers by company and optional project."""

        self._require_company(company_id)
        if project_id is not None:
            self._require_company_project(company_id, project_id)
        return self._repository.list_layers(company_id, project_id)

    def layer_status(self, company_id: str, project_id: str) -> list[CorporateLayer]:
        """Return layer status for one governed project."""

        return self.list_layers(company_id, project_id)

    def corporate_map(self, company_id: str) -> CorporateGisIntelligenceMap:
        """Return corporate spatial map references for one company."""

        return CorporateGisIntelligenceMap(
            company_id=company_id,
            sources=self.list_sources(company_id),
            layers=self.list_layers(company_id),
            summary=self.summary(company_id),
        )

    def filter_projects_by_indicator(
        self,
        company_id: str,
        indicator: str,
        minimum_value: float = 0,
        risk_level: str | None = None,
    ) -> list[ProjectSpatialIndicator]:
        """Return projects whose spatial indicators match corporate filters."""

        self._require_company(company_id)
        results: list[ProjectSpatialIndicator] = []
        for layer in self._repository.list_layers(company_id):
            if layer.spatial_indicator != indicator or layer.indicator_value < minimum_value:
                continue
            if risk_level is not None and layer.risk_level != risk_level:
                continue
            project = self._portfolio.get_project_for_company(company_id, layer.project_id)
            if project is None:
                continue
            results.append(
                ProjectSpatialIndicator(
                    company_id=company_id,
                    project_id=layer.project_id,
                    project_name=project.name,
                    indicator=indicator,
                    value=layer.indicator_value,
                    risk_level=layer.risk_level,
                    layer_id=layer.layer_id,
                )
            )
        return results

    def summary(self, company_id: str) -> CorporateGisSummary:
        """Return portfolio-level GIS intelligence summary."""

        self._require_company(company_id)
        sources = self._repository.list_sources(company_id)
        layers = self._repository.list_layers(company_id)
        active_layers = [
            layer
            for layer in layers
            if layer.status in {CorporateLayerStatus.AVAILABLE, CorporateLayerStatus.WARNING, CorporateLayerStatus.CRITICAL}
        ]
        active_projects = {layer.project_id for layer in active_layers}
        progress_layers = [
            layer
            for layer in active_layers
            if layer.layer_type == CorporateLayerType.PHYSICAL_PROGRESS
            or layer.spatial_indicator == "physical_progress"
        ]
        aggregated_progress = (
            0
            if not progress_layers
            else round(sum(layer.indicator_value for layer in progress_layers) / len(progress_layers), 2)
        )
        return CorporateGisSummary(
            company_id=company_id,
            total_projects_georeferenced=len({source.project_id for source in sources}),
            projects_with_active_layers=len(active_projects),
            projects_with_spatial_risks=len(
                {
                    layer.project_id
                    for layer in active_layers
                    if layer.layer_type == CorporateLayerType.RISKS
                    or layer.risk_level in {"medium", "high", "critical"}
                }
            ),
            projects_with_environmental_alerts=len(
                {
                    layer.project_id
                    for layer in active_layers
                    if layer.layer_type == CorporateLayerType.ENVIRONMENTAL
                    and layer.status in {CorporateLayerStatus.WARNING, CorporateLayerStatus.CRITICAL}
                }
            ),
            projects_with_active_restrictions=len(
                {
                    layer.project_id
                    for layer in active_layers
                    if layer.layer_type == CorporateLayerType.RESTRICTIONS
                }
            ),
            aggregated_spatial_progress=aggregated_progress,
            layers_by_type=self._count_by([layer.layer_type.value for layer in layers]),
            layers_by_status=self._count_by([layer.status.value for layer in layers]),
            regions=self._count_by([layer.region or "sin_region" for layer in layers]),
        )

    def _require_company(self, company_id: str) -> None:
        if not self._companies.exists(company_id):
            raise ValueError(f"Company is not registered: {company_id}")

    def _require_company_project(self, company_id: str, project_id: str) -> None:
        self._require_company(company_id)
        if self._portfolio.get_project_for_company(company_id, project_id) is None:
            raise ValueError(f"Project is not registered for company {company_id}: {project_id}")

    @staticmethod
    def _count_by(values: list[str]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for value in values:
            counts[value] = counts.get(value, 0) + 1
        return counts

    def _audit_event(self, action: str, entity_type: str, entity_id: str) -> None:
        if self._audit is None:
            return
        self._audit.save(
            AuditEvent(
                actor="system",
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                detail=f"{entity_type} {entity_id} registered for Corporate GIS Intelligence.",
            )
        )
