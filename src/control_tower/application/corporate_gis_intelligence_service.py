"""Corporate GIS Intelligence application service.

ADR references:
- ADR-0009: GeoServer integration.
- ADR-0010: Google Workspace transition integration.
- ADR-0011: Deployment strategy.
- ADR-0013: Corporate GIS Intelligence.
- ADR-0015: Tower vs WEB SIG operational boundary.
"""

from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from control_tower.application.enterprise_service import CompanyService
from control_tower.application.portfolio_service import PortfolioService
from control_tower.application.repositories import AuditEventRepository, CorporateGisIntelligenceRepository
from control_tower.domain.audit import AuditEvent
from control_tower.domain.corporate_gis_intelligence import (
    CorporateGisAvailability,
    CorporateGisIntelligenceMap,
    CorporateGisLayerPanel,
    CorporateGisServiceValidation,
    CorporateGisSource,
    CorporateGisSourceStatus,
    CorporateGisSummary,
    CorporateLayer,
    CorporateLayerLegendItem,
    CorporateLayerStatus,
    CorporateLayerType,
    GisServiceKind,
    ProjectSpatialIndicator,
)


class CorporateGisIntelligenceService:
    """Consolidates published WEB SIG GIS references for corporate analysis."""

    THEME_ALIASES = {
        "estado": None,
        "riesgo": CorporateLayerType.RISKS,
        "risk": CorporateLayerType.RISKS,
        "calidad": CorporateLayerType.QUALITY,
        "quality": CorporateLayerType.QUALITY,
        "ssoma": CorporateLayerType.SSOMA,
        "ambiental": CorporateLayerType.ENVIRONMENTAL,
        "environmental": CorporateLayerType.ENVIRONMENTAL,
        "produccion": CorporateLayerType.PRODUCTION,
        "production": CorporateLayerType.PRODUCTION,
        "cronograma": CorporateLayerType.SCHEDULE,
        "schedule": CorporateLayerType.SCHEDULE,
        "predios": CorporateLayerType.LAND_PARCELS,
        "land_parcels": CorporateLayerType.LAND_PARCELS,
        "interferencias": CorporateLayerType.INTERFERENCES,
        "interferences": CorporateLayerType.INTERFERENCES,
        "avance": CorporateLayerType.PHYSICAL_PROGRESS,
        "physical_progress": CorporateLayerType.PHYSICAL_PROGRESS,
    }

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

    def register_real_service(self, source: CorporateGisSource, *, validate: bool = True) -> CorporateGisSource:
        """Register a published GIS service and optionally validate its availability."""

        saved = self.register_source(source)
        if validate:
            validation = self.validate_source(saved)
            status = self._source_status_for_availability(validation.availability)
            if status != saved.status:
                saved = self._repository.save_source(saved.model_copy(update={"status": status}))
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

    def validate_source(self, source: CorporateGisSource) -> CorporateGisServiceValidation:
        """Validate a published WEB SIG GIS source without editing geometry."""

        checked_url = self._capabilities_url(source)
        if source.service_kind == GisServiceKind.VECTOR_TILES:
            return self._validate_vector_tiles(source)
        try:
            request = Request(checked_url, method="GET", headers={"User-Agent": "BIMSIG-Control-Tower/REV13"})
            with urlopen(request, timeout=10) as response:
                body = response.read(4096).decode("utf-8", errors="ignore").casefold()
                status_code = getattr(response, "status", 200)
        except HTTPError as exc:
            return self._validation(source, CorporateGisAvailability.UNAVAILABLE, f"HTTP {exc.code}: {exc.reason}", checked_url, exc.code)
        except (URLError, TimeoutError, OSError) as exc:
            return self._validation(source, CorporateGisAvailability.UNAVAILABLE, str(exc), checked_url)
        expected = {
            GisServiceKind.WMS: "wms_capabilities",
            GisServiceKind.WFS: "wfs_capabilities",
            GisServiceKind.WMTS: "capabilities",
        }.get(source.service_kind)
        detected = expected in body or "capabilities" in body
        availability = CorporateGisAvailability.AVAILABLE if detected else CorporateGisAvailability.DEGRADED
        detail = "Capabilities document detected." if detected else "Service responded but capabilities signature was not detected."
        return self._validation(source, availability, detail, checked_url, status_code, detected)

    def validate_sources(
        self,
        company_id: str,
        project_id: str | None = None,
    ) -> list[CorporateGisServiceValidation]:
        """Validate all published GIS services for a company or project."""

        sources = self.list_sources(company_id, project_id)
        validations = [self.validate_source(source) for source in sources]
        for validation in validations:
            self._audit_event(
                f"gis_intelligence.{validation.service_kind.value}_validated",
                "corporate_gis_source",
                validation.source_id,
            )
        return validations

    def layer_panel(
        self,
        company_id: str,
        project_id: str | None = None,
        *,
        discipline: str | None = None,
        estado: str | None = None,
        riesgo: str | None = None,
    ) -> CorporateGisLayerPanel:
        """Return the read-only layer panel, legend, availability, and filters."""

        layers = self.list_layers(company_id, project_id)
        if discipline:
            layers = [layer for layer in layers if layer.discipline.value == discipline]
        if estado:
            layers = [layer for layer in layers if layer.status.value == estado]
        if riesgo:
            layers = [layer for layer in layers if layer.risk_level == riesgo]
        source_by_id = {source.source_id: source for source in self.list_sources(company_id, project_id)}
        validations = [
            self.validate_source(source_by_id[layer.source_id])
            for layer in layers
            if layer.source_id in source_by_id
        ]
        validation_by_source = {validation.source_id: validation for validation in validations}
        return CorporateGisLayerPanel(
            company_id=company_id,
            project_id=project_id,
            layers=[
                self._legend_item(layer, source_by_id.get(layer.source_id), validation_by_source.get(layer.source_id))
                for layer in layers
            ],
            validations=validations,
            filters=self._panel_filters(self.list_layers(company_id, project_id)),
        )

    def layer_status(self, company_id: str, project_id: str) -> list[CorporateLayer]:
        """Return layer status for one governed project."""

        return self.list_layers(company_id, project_id)

    def corporate_map(self, company_id: str) -> CorporateGisIntelligenceMap:
        """Return corporate spatial map references for one company."""

        self._require_company(company_id)
        sources = self._repository.list_sources(company_id)
        layers = self._repository.list_layers(company_id)
        return self._map_from(company_id, sources, layers)

    def company_map(self, company_id: str) -> CorporateGisIntelligenceMap:
        """Return company-scoped corporate layers."""

        return self.corporate_map(company_id)

    def regional_map(self, company_id: str, region: str) -> CorporateGisIntelligenceMap:
        """Return corporate layers filtered by region."""

        self._require_company(company_id)
        layers = [
            layer
            for layer in self._repository.list_layers(company_id)
            if (layer.region or "").casefold() == region.casefold()
        ]
        return self._map_from(company_id, self._sources_for_layers(company_id, layers), layers)

    def program_map(self, company_id: str, program_id: str) -> CorporateGisIntelligenceMap:
        """Return corporate layers for one portfolio program."""

        self._require_company(company_id)
        layers = [
            layer
            for layer in self._repository.list_layers(company_id)
            if layer.program_id == program_id
        ]
        sources = [
            source
            for source in self._repository.list_sources(company_id)
            if source.program_id == program_id or source.source_id in {layer.source_id for layer in layers}
        ]
        return self._map_from(company_id, sources, layers)

    def project_map(self, company_id: str, project_id: str) -> CorporateGisIntelligenceMap:
        """Return corporate layers for one project without editing them."""

        self._require_company_project(company_id, project_id)
        return self._map_from(
            company_id,
            self._repository.list_sources(company_id, project_id),
            self._repository.list_layers(company_id, project_id),
        )

    def thematic_map(self, company_id: str, theme: str) -> CorporateGisIntelligenceMap:
        """Return corporate layers for one thematic view."""

        self._require_company(company_id)
        layer_type = self._layer_type_for_theme(theme)
        layers = self._repository.list_layers(company_id)
        if layer_type is not None:
            layers = [layer for layer in layers if layer.layer_type == layer_type]
        return self._map_from(company_id, self._sources_for_layers(company_id, layers), layers)

    def filtered_map(
        self,
        company_id: str,
        *,
        estado: str | None = None,
        riesgo: str | None = None,
        calidad: str | None = None,
        ssoma: str | None = None,
        ambiental: str | None = None,
        produccion: str | None = None,
        cronograma: str | None = None,
        predios: str | None = None,
        interferencias: str | None = None,
    ) -> CorporateGisIntelligenceMap:
        """Return corporate layers matching business filters."""

        self._require_company(company_id)
        layers = self._repository.list_layers(company_id)
        if estado:
            layers = [
                layer
                for layer in layers
                if layer.status.value == estado or layer.metadata.get("estado") == estado
            ]
        if riesgo:
            layers = [
                layer
                for layer in layers
                if layer.risk_level == riesgo
                or layer.layer_type == CorporateLayerType.RISKS
                and self._filter_value_matches(layer, riesgo)
            ]
        typed_filters = {
            CorporateLayerType.QUALITY: calidad,
            CorporateLayerType.SSOMA: ssoma,
            CorporateLayerType.ENVIRONMENTAL: ambiental,
            CorporateLayerType.PRODUCTION: produccion,
            CorporateLayerType.SCHEDULE: cronograma,
            CorporateLayerType.LAND_PARCELS: predios,
            CorporateLayerType.INTERFERENCES: interferencias,
        }
        for layer_type, value in typed_filters.items():
            if value:
                layers = [
                    layer
                    for layer in layers
                    if layer.layer_type == layer_type and self._filter_value_matches(layer, value)
                ]
        return self._map_from(company_id, self._sources_for_layers(company_id, layers), layers)

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
        return self._summary_from(company_id, sources, layers)

    def _map_from(
        self,
        company_id: str,
        sources: list[CorporateGisSource],
        layers: list[CorporateLayer],
    ) -> CorporateGisIntelligenceMap:
        return CorporateGisIntelligenceMap(
            company_id=company_id,
            sources=sources,
            layers=layers,
            summary=self._summary_from(company_id, sources, layers),
        )

    def _summary_from(
        self,
        company_id: str,
        sources: list[CorporateGisSource],
        layers: list[CorporateLayer],
    ) -> CorporateGisSummary:
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

    def _sources_for_layers(
        self,
        company_id: str,
        layers: list[CorporateLayer],
    ) -> list[CorporateGisSource]:
        source_ids = {layer.source_id for layer in layers}
        return [
            source
            for source in self._repository.list_sources(company_id)
            if source.source_id in source_ids
        ]

    def _layer_type_for_theme(self, theme: str) -> CorporateLayerType | None:
        normalized = theme.casefold()
        if normalized in self.THEME_ALIASES:
            return self.THEME_ALIASES[normalized]
        try:
            return CorporateLayerType(normalized)
        except ValueError as exc:
            raise ValueError(f"Unsupported corporate GIS theme: {theme}") from exc

    @staticmethod
    def _filter_value_matches(layer: CorporateLayer, value: str) -> bool:
        normalized = value.casefold()
        if normalized in {"1", "true", "yes", "si", "sí", "all", "todos"}:
            return True
        return (
            layer.status.value == value
            or layer.risk_level == value
            or layer.spatial_indicator == value
            or value in layer.metadata.values()
            or layer.metadata.get(layer.layer_type.value) == value
        )

    def _capabilities_url(self, source: CorporateGisSource) -> str:
        service = {
            GisServiceKind.WMS: "WMS",
            GisServiceKind.WFS: "WFS",
            GisServiceKind.WMTS: "WMTS",
        }.get(source.service_kind)
        if service is None:
            return source.service_url
        separator = "&" if "?" in source.service_url else "?"
        return f"{source.service_url}{separator}{urlencode({'service': service, 'request': 'GetCapabilities'})}"

    def _validate_vector_tiles(self, source: CorporateGisSource) -> CorporateGisServiceValidation:
        if not source.service_url:
            return self._validation(source, CorporateGisAvailability.NOT_CONFIGURED, "Vector Tiles URL is not configured.", None)
        try:
            request = Request(source.service_url, method="GET", headers={"User-Agent": "BIMSIG-Control-Tower/REV13"})
            with urlopen(request, timeout=10) as response:
                body = response.read(4096).decode("utf-8", errors="ignore").casefold()
                status_code = getattr(response, "status", 200)
        except HTTPError as exc:
            return self._validation(source, CorporateGisAvailability.UNAVAILABLE, f"HTTP {exc.code}: {exc.reason}", source.service_url, exc.code)
        except (URLError, TimeoutError, OSError) as exc:
            return self._validation(source, CorporateGisAvailability.UNAVAILABLE, str(exc), source.service_url)
        detected = "tiles" in body or "vector_layers" in body or source.service_url.endswith(".pbf")
        availability = CorporateGisAvailability.AVAILABLE if detected else CorporateGisAvailability.DEGRADED
        detail = "Vector tiles metadata detected." if detected else "Vector tile endpoint responded without tile metadata signature."
        return self._validation(source, availability, detail, source.service_url, status_code, detected)

    @staticmethod
    def _validation(
        source: CorporateGisSource,
        availability: CorporateGisAvailability,
        detail: str,
        checked_url: str | None,
        status_code: int | None = None,
        capability_detected: bool = False,
    ) -> CorporateGisServiceValidation:
        return CorporateGisServiceValidation(
            source_id=source.source_id,
            service_kind=source.service_kind,
            service_url=source.service_url,
            availability=availability,
            status_code=status_code,
            capability_detected=capability_detected,
            detail=detail,
            checked_url=checked_url,
        )

    @staticmethod
    def _source_status_for_availability(availability: CorporateGisAvailability) -> CorporateGisSourceStatus:
        if availability == CorporateGisAvailability.AVAILABLE:
            return CorporateGisSourceStatus.ACTIVE
        if availability == CorporateGisAvailability.DEGRADED:
            return CorporateGisSourceStatus.DEGRADED
        return CorporateGisSourceStatus.UNAVAILABLE

    @staticmethod
    def _legend_item(
        layer: CorporateLayer,
        source: CorporateGisSource | None,
        validation: CorporateGisServiceValidation | None,
    ) -> CorporateLayerLegendItem:
        legend_url = None
        if source and source.service_kind == GisServiceKind.WMS:
            separator = "&" if "?" in source.service_url else "?"
            legend_url = f"{source.service_url}{separator}{urlencode({'service': 'WMS', 'request': 'GetLegendGraphic', 'format': 'image/png', 'layer': layer.name})}"
        return CorporateLayerLegendItem(
            layer_id=layer.layer_id,
            name=layer.name,
            service_kind=source.service_kind if source else GisServiceKind.GIS_API,
            layer_type=layer.layer_type,
            discipline=layer.discipline,
            status=layer.status,
            availability=validation.availability if validation else CorporateGisAvailability.NOT_CONFIGURED,
            risk_level=layer.risk_level,
            indicator_value=layer.indicator_value,
            service_url=source.service_url if source else None,
            legend_url=legend_url,
        )

    @staticmethod
    def _panel_filters(layers: list[CorporateLayer]) -> dict[str, list[str]]:
        return {
            "discipline": sorted({layer.discipline.value for layer in layers}),
            "estado": sorted({layer.status.value for layer in layers}),
            "riesgo": sorted({layer.risk_level for layer in layers}),
            "layer_type": sorted({layer.layer_type.value for layer in layers}),
        }

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
