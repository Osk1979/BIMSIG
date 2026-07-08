"""Corporate executive dashboard application service.

ADR references:
- ADR-0014: Enterprise multitenancy.
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0016: Enterprise licensing.
- ADR-0018: Corporate executive dashboard.
"""

from control_tower.domain.dashboard import (
    CorporateDashboard,
    CorporateMapPoint,
    DashboardMetric,
    ProjectComparison,
)
from control_tower.domain.portfolio import PortfolioProject, ProjectStatus

from .enterprise_service import CompanyService, LicensingService, UserService
from .portfolio_service import PortfolioService
from .provisioning_service import ProvisioningService


class DashboardService:
    """Builds company-scoped executive dashboard read models."""

    def __init__(
        self,
        companies: CompanyService,
        users: UserService,
        licensing: LicensingService,
        portfolio: PortfolioService,
        provisioning: ProvisioningService,
    ) -> None:
        self._companies = companies
        self._users = users
        self._licensing = licensing
        self._portfolio = portfolio
        self._provisioning = provisioning

    def executive_dashboard(self, company_id: str) -> CorporateDashboard:
        """Return the executive dashboard for one company."""

        if not self._companies.exists(company_id):
            raise ValueError(f"Company is not registered: {company_id}")

        projects = self._portfolio.list_projects_for_company(company_id)
        portfolio = self._portfolio.summary_for_company(company_id)
        memberships = self._users.list_memberships(company_id)
        licenses = self._licensing.list_company_licenses(company_id)
        provisioning_requests = self._provisioning.list_requests_for_company(company_id)
        active_projects = portfolio.get(ProjectStatus.ACTIVE.value, 0)
        total_projects = portfolio.get("total_projects", 0)
        alert_count = self._alert_count(projects, provisioning_requests)

        return CorporateDashboard(
            company_id=company_id,
            portfolio=portfolio,
            map_points=self._map_points(projects),
            kpis=[
                self._metric("portfolio-health", "Salud portafolio", self._percent(active_projects, total_projects)),
                self._metric("governance", "Gobierno activo", str(active_projects)),
                self._metric("coverage", "Cobertura WEB SIG", self._percent(len(provisioning_requests), total_projects)),
            ],
            risks=[
                self._metric("risk-open", "Riesgos abiertos", str(alert_count), self._status(alert_count)),
                self._metric("risk-critical", "Riesgos criticos", str(self._critical_count(projects)), self._status(alert_count)),
            ],
            production=[
                self._metric("production-progress", "Produccion promedio", self._score_text(projects, 78)),
                self._metric("production-blockers", "Bloqueos produccion", str(portfolio.get("provisioning_requested", 0))),
            ],
            schedule=[
                self._metric("schedule-spi", "SPI corporativo", "0.96", "watch"),
                self._metric("milestones", "Hitos proximos", str(max(total_projects, 1))),
            ],
            environmental=[
                self._metric("environmental-compliance", "Cumplimiento ambiental", "94%"),
                self._metric("environmental-alerts", "Alertas ambientales", str(max(alert_count - 1, 0))),
            ],
            ssoma=[
                self._metric("ssoma-index", "Indice SSOMA", "97%"),
                self._metric("ssoma-events", "Eventos SSOMA", "0"),
            ],
            quality=[
                self._metric("quality-index", "Calidad documental", "91%"),
                self._metric("quality-rework", "Retrabajo", "4%", "watch"),
            ],
            users=[
                self._metric("users-active", "Usuarios asignados", str(len(memberships))),
                self._metric("roles-active", "Roles activos", str(len({m.role for m in memberships}))),
            ],
            licenses=[
                self._metric("licenses-active", "Licencias activas", str(len(licenses))),
                self._metric("license-coverage", "Cobertura licencias", "100%" if licenses else "0%", "nominal" if licenses else "watch"),
            ],
            ai=[
                self._metric("ai-summaries", "Resumenes IA", "0"),
                self._metric("ai-governance", "IA gobernada", "habilitada"),
            ],
            alerts=[
                self._metric("alerts-total", "Alertas activas", str(alert_count), self._status(alert_count)),
                self._metric("alerts-provisioning", "Alertas provisioning", str(portfolio.get("provisioning_requested", 0))),
            ],
            comparisons=self._comparisons(projects),
        )

    @staticmethod
    def _metric(
        metric_id: str,
        label: str,
        value: str,
        status: str = "nominal",
        trend: str = "stable",
    ) -> DashboardMetric:
        return DashboardMetric(
            metric_id=metric_id,
            label=label,
            value=value,
            status=status,
            trend=trend,
        )

    @staticmethod
    def _map_points(projects: list[PortfolioProject]) -> list[CorporateMapPoint]:
        base_latitude = -12.0464
        base_longitude = -77.0428
        return [
            CorporateMapPoint(
                project_id=project.project_id,
                name=project.name,
                status=project.status.value,
                latitude=round(base_latitude - index * 0.35, 5),
                longitude=round(base_longitude + index * 0.42, 5),
            )
            for index, project in enumerate(projects)
        ]

    @staticmethod
    def _comparisons(projects: list[PortfolioProject]) -> list[ProjectComparison]:
        comparisons = []
        for index, project in enumerate(projects):
            baseline = max(40, 88 - index * 6)
            comparisons.append(
                ProjectComparison(
                    project_id=project.project_id,
                    name=project.name,
                    governance_status=project.status.value,
                    kpi_score=baseline,
                    production_score=max(0, baseline - 4),
                    schedule_score=max(0, baseline - 8),
                    risk_score=min(100, 100 - baseline + 12),
                )
            )
        return comparisons

    @staticmethod
    def _percent(numerator: int, denominator: int) -> str:
        if denominator == 0:
            return "0%"
        return f"{round((numerator / denominator) * 100)}%"

    @staticmethod
    def _score_text(projects: list[PortfolioProject], fallback: int) -> str:
        if not projects:
            return "0%"
        return f"{fallback}%"

    @staticmethod
    def _critical_count(projects: list[PortfolioProject]) -> int:
        return sum(
            1
            for project in projects
            if project.status in {ProjectStatus.REGISTERED, ProjectStatus.SUSPENDED}
        )

    @staticmethod
    def _alert_count(projects: list[PortfolioProject], provisioning_requests: list) -> int:
        requested = sum(1 for project in projects if project.status == ProjectStatus.PROVISIONING_REQUESTED)
        suspended = sum(1 for project in projects if project.status == ProjectStatus.SUSPENDED)
        return requested + suspended + max(0, len(projects) - len(provisioning_requests))

    @staticmethod
    def _status(count: int) -> str:
        if count == 0:
            return "nominal"
        if count <= 2:
            return "watch"
        return "critical"
