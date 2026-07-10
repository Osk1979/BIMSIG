"""Portal Gateway application service.

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0018: Corporate executive dashboard.
- ADR-0029: Enterprise portal gateway.
"""

from control_tower.application.dashboard_service import DashboardService
from control_tower.application.reporting_service import CorporateReportingService
from control_tower.domain.portal_gateway import (
    PortalGatewayConfig,
    PortalGatewayHealth,
    PortalGatewayLink,
    PortalGatewaySnapshot,
)


class PortalGatewayService:
    """Publishes the stable public contract consumed by the BIM-SIG portal."""

    def __init__(
        self,
        dashboard_service: DashboardService,
        reporting_service: CorporateReportingService,
        *,
        portal_origin: str,
        tower_base_url: str,
        websig_base_url: str,
        default_company_id: str = "CRTG",
    ) -> None:
        self._dashboard = dashboard_service
        self._reporting = reporting_service
        self._portal_origin = portal_origin.rstrip("/")
        self._tower_base_url = tower_base_url.rstrip("/")
        self._websig_base_url = websig_base_url.rstrip("/")
        self._default_company_id = default_company_id

    def config(self) -> PortalGatewayConfig:
        """Return public portal configuration and governed navigation links."""

        return PortalGatewayConfig(
            portal_origin=self._portal_origin,
            tower_base_url=self._tower_base_url,
            websig_base_url=self._websig_base_url,
            default_company_id=self._default_company_id,
            links=self.links(self._default_company_id),
        )

    def health(self) -> PortalGatewayHealth:
        """Return portal-to-Tower readiness metadata."""

        return PortalGatewayHealth()

    def links(self, company_id: str) -> list[PortalGatewayLink]:
        """Return official links exposed to the enterprise portal."""

        return [
            PortalGatewayLink(
                link_id="tower-dashboard",
                label="Torre de Control",
                href=f"{self._tower_base_url}/dashboard",
                description="Dashboard ejecutivo corporativo de la Torre de Control.",
            ),
            PortalGatewayLink(
                link_id="tower-executive-api",
                label="API ejecutiva",
                href=f"{self._tower_base_url}/api/v1/companies/{company_id}/dashboard/executive",
                description="Contrato JSON oficial para KPIs, cartera, GIS y gobierno.",
            ),
            PortalGatewayLink(
                link_id="tower-report-catalog",
                label="Reportes corporativos",
                href=f"{self._tower_base_url}/api/v1/reports/template-catalog",
                description="Catalogo gobernado de reportes imprimibles y PDF.",
            ),
            PortalGatewayLink(
                link_id="websig-enterprise",
                label="WEB SIG Enterprise",
                href=self._websig_base_url,
                description="Operacion georreferenciada, activos, campo y documentos del proyecto.",
            ),
        ]

    def snapshot(self, company_id: str) -> PortalGatewaySnapshot:
        """Return the consolidated payload needed by the enterprise portal."""

        dashboard = self._dashboard.executive_dashboard(company_id)
        metrics = [
            *dashboard.kpis,
            *dashboard.production[:2],
            *dashboard.schedule[:2],
            *dashboard.alerts[:2],
        ]
        return PortalGatewaySnapshot(
            company_id=company_id,
            title="BIM-SIG Enterprise Portal Gateway",
            metrics=metrics,
            links=self.links(company_id),
            dashboard=dashboard,
            report_templates=self._reporting.list_templates(),
        )
