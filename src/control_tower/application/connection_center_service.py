"""Connection Center application service.

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0021: DevSecOps operating model.
- ADR-0029: Enterprise portal gateway.
- ADR-0030: Connection Center.
"""

from control_tower.application.infrastructure_connectors import InfrastructureConnectorService
from control_tower.application.portal_gateway_service import PortalGatewayService
from control_tower.domain.connection_center import (
    ConnectionCenterHealth,
    ConnectionCenterReadiness,
    ConnectionCenterTopology,
    ConnectionEdge,
    ConnectionKind,
    ConnectionNode,
    ConnectionStatus,
)


class ConnectionCenterService:
    """Builds the governed integration view for Portal, Tower, WEB SIG, and connectors."""

    def __init__(
        self,
        portal_gateway: PortalGatewayService,
        infrastructure_connectors: InfrastructureConnectorService,
        *,
        portal_origin: str,
        tower_base_url: str,
        websig_base_url: str,
        default_company_id: str = "CRTG",
    ) -> None:
        self._portal_gateway = portal_gateway
        self._infrastructure_connectors = infrastructure_connectors
        self._portal_origin = portal_origin.rstrip("/")
        self._tower_base_url = tower_base_url.rstrip("/")
        self._websig_base_url = websig_base_url.rstrip("/")
        self._default_company_id = default_company_id

    def topology(self, company_id: str | None = None) -> ConnectionCenterTopology:
        """Return the current enterprise connection topology."""

        resolved_company = company_id or self._default_company_id
        nodes = [
            ConnectionNode(
                node_id="portal",
                label="BIM-SIG Enterprise Portal",
                kind=ConnectionKind.PORTAL,
                url=self._portal_origin,
                description="Public enterprise entry point for BIM-SIG users.",
            ),
            ConnectionNode(
                node_id="control-tower",
                label="Corporate Control Tower",
                kind=ConnectionKind.CONTROL_TOWER,
                url=self._tower_base_url,
                description="REV12 backend for governance, KPIs, reporting, and provisioning.",
            ),
            ConnectionNode(
                node_id="websig",
                label="WEB SIG Enterprise",
                kind=ConnectionKind.WEB_SIG,
                url=self._websig_base_url,
                description="Project GIS, field, assets, documents, and operational views.",
            ),
            ConnectionNode(
                node_id="reporting",
                label="Corporate Reporting Engine",
                kind=ConnectionKind.REPORTING,
                url=f"{self._tower_base_url}/api/v1/reports/template-catalog",
                description="Governed printable report catalog and emission API.",
            ),
            ConnectionNode(
                node_id="infrastructure",
                label="Infrastructure Connectors",
                kind=ConnectionKind.INFRASTRUCTURE,
                url=f"{self._tower_base_url}/api/v1/infrastructure/connectors/health",
                description="PostGIS, GeoServer, NAS, and Google Drive connector health.",
            ),
        ]
        edges = [
            ConnectionEdge(
                source="portal",
                target="control-tower",
                contract=f"/api/v1/portal-gateway/companies/{resolved_company}/snapshot",
            ),
            ConnectionEdge(
                source="control-tower",
                target="websig",
                contract="/api/v1/portal-gateway/config",
            ),
            ConnectionEdge(
                source="control-tower",
                target="reporting",
                contract="/api/v1/reports/template-catalog",
            ),
            ConnectionEdge(
                source="control-tower",
                target="infrastructure",
                contract="/api/v1/infrastructure/connectors/health",
            ),
        ]
        return ConnectionCenterTopology(
            nodes=nodes,
            edges=edges,
            links=self._portal_gateway.links(resolved_company),
        )

    def health(self) -> ConnectionCenterHealth:
        """Return normalized Connection Center health."""

        connectors = self._infrastructure_connectors.health()
        infrastructure_status = self._infrastructure_status(connectors)
        status = (
            ConnectionStatus.READY
            if infrastructure_status == ConnectionStatus.READY
            else ConnectionStatus.DEGRADED
        )
        return ConnectionCenterHealth(
            status=status,
            portal_gateway=ConnectionStatus.READY,
            infrastructure=infrastructure_status,
            connectors=connectors,
        )

    def readiness(self, company_id: str) -> ConnectionCenterReadiness:
        """Return company-scoped topology and health in one payload."""

        health = self.health()
        return ConnectionCenterReadiness(
            company_id=company_id,
            status=health.status,
            topology=self.topology(company_id),
            health=health,
        )

    @staticmethod
    def _infrastructure_status(connectors: list) -> ConnectionStatus:
        if not connectors:
            return ConnectionStatus.BLOCKED
        if all(item.configured for item in connectors):
            return ConnectionStatus.READY
        return ConnectionStatus.DEGRADED
