"""Corporate reporting and print application service.

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0018: Corporate executive dashboard.
- ADR-0019: NAS Corporate Information Center.
- ADR-0025: Corporate Portfolio Domain.
"""

from datetime import UTC, datetime
from hashlib import sha256
from html import escape

from control_tower.application.dashboard_service import DashboardService
from control_tower.application.repositories import AuditEventRepository
from control_tower.domain.audit import AuditEvent
from control_tower.domain.dashboard import CorporateDashboard
from control_tower.domain.reports import CorporatePrintReport, ReportManifest, ReportRequest


class CorporateReportingService:
    """Issues print-ready corporate reports from consolidated Tower data."""

    def __init__(
        self,
        dashboard_service: DashboardService,
        audit_repository: AuditEventRepository | None = None,
    ) -> None:
        self._dashboard = dashboard_service
        self._audit = audit_repository

    def preview(self, request: ReportRequest) -> CorporatePrintReport:
        """Prepare a print-ready report without recording emission."""

        dashboard = self._dashboard.executive_dashboard(request.company_id)
        html = self._render_html(request, dashboard)
        return self._build_report(request, html, status="preview")

    def issue(self, request: ReportRequest) -> CorporatePrintReport:
        """Issue a governed corporate report and record an audit event."""

        dashboard = self._dashboard.executive_dashboard(request.company_id)
        html = self._render_html(request, dashboard)
        report = self._build_report(request, html, status="issued")
        self._audit_event(request, report.manifest)
        return report

    def _build_report(self, request: ReportRequest, html: str, *, status: str) -> CorporatePrintReport:
        created_at = datetime.now(UTC)
        checksum = sha256(html.encode("utf-8")).hexdigest()
        report_id = self._report_id(request, created_at)
        manifest = ReportManifest(
            report_id=report_id,
            company_id=request.company_id,
            template=request.template,
            scope=request.scope,
            title=self._title(request),
            output_format=request.output_format,
            requested_by=request.requested_by,
            project_id=request.project_id,
            program_id=request.program_id,
            filters=request.filters,
            data_sources=[
                "portfolio_domain",
                "executive_dashboard",
                "corporate_gis_intelligence",
                "nas_information_center",
                "audit_events",
            ],
            nas_logical_uri=self._nas_uri(request, report_id),
            checksum_sha256=checksum,
            status=status,
            created_at=created_at,
        )
        return CorporatePrintReport(manifest=manifest, html=html, print_css=self._print_css())

    def _render_html(self, request: ReportRequest, dashboard: CorporateDashboard) -> str:
        title = self._title(request)
        metrics = dashboard.kpis + dashboard.production + dashboard.schedule + dashboard.environmental + dashboard.ssoma
        metric_rows = "".join(
            f"<tr><td>{escape(metric.label)}</td><td>{escape(metric.value)}</td><td>{escape(metric.status)}</td></tr>"
            for metric in metrics
        )
        projects = "".join(
            "<tr>"
            f"<td>{escape(item.project_name)}</td>"
            f"<td>{escape(item.program or 'Programa pendiente')}</td>"
            f"<td>{escape(item.lifecycle_stage)}</td>"
            f"<td>{escape(item.governance_status)}</td>"
            f"<td>{escape(item.websig)}</td>"
            f"<td>{escape(item.nas)}</td>"
            f"<td>{escape(item.gis)}</td>"
            "</tr>"
            for item in dashboard.portfolio_governance
        )
        locations = "".join(
            "<tr>"
            f"<td>{escape(point.name)}</td>"
            f"<td>{escape(point.country or 'PE')}</td>"
            f"<td>{escape(point.region or 'Region pendiente')}</td>"
            f"<td>{escape(point.province or 'Provincia pendiente')}</td>"
            f"<td>{escape(point.district or 'Distrito pendiente')}</td>"
            f"<td>{escape(point.location_validation_status or 'pendiente')}</td>"
            "</tr>"
            for point in dashboard.map_points
        )
        generated = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
        return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>{escape(title)}</title>
  <style>{self._print_css()}</style>
</head>
<body>
  <header>
    <div class="eyebrow">BIMSIG Enterprise / Corporate Control Tower</div>
    <h1>{escape(title)}</h1>
    <p>Empresa: <strong>{escape(request.company_id)}</strong> - Emitido: {generated} - Solicitante: {escape(request.requested_by)}</p>
  </header>
  <section>
    <h2>Resumen ejecutivo</h2>
    <div class="cards">
      <article><span>Portafolio</span><strong>{dashboard.portfolio.get("total_projects", 0)}</strong></article>
      <article><span>Activos</span><strong>{dashboard.portfolio.get("active_projects", 0)}</strong></article>
      <article><span>Capas GIS</span><strong>{dashboard.gis_intelligence.projects_with_active_layers if dashboard.gis_intelligence else 0}</strong></article>
      <article><span>Alertas</span><strong>{dashboard.alerts[0].value if dashboard.alerts else "0"}</strong></article>
    </div>
  </section>
  <section>
    <h2>KPIs corporativos</h2>
    <table><thead><tr><th>KPI</th><th>Valor</th><th>Estado</th></tr></thead><tbody>{metric_rows}</tbody></table>
  </section>
  <section>
    <h2>Portafolio gobernado</h2>
    <table><thead><tr><th>Proyecto</th><th>Programa</th><th>Ciclo</th><th>Gobierno</th><th>WEB SIG</th><th>NAS</th><th>GIS</th></tr></thead><tbody>{projects}</tbody></table>
  </section>
  <section>
    <h2>Ubicacion administrativa</h2>
    <table><thead><tr><th>Proyecto</th><th>Pais</th><th>Region</th><th>Provincia</th><th>Distrito</th><th>Validacion</th></tr></thead><tbody>{locations}</tbody></table>
  </section>
  <footer>
    <p>Reporte generado desde datos consolidados. La Torre no edita geometria ni opera WEB SIG.</p>
  </footer>
</body>
</html>"""

    @staticmethod
    def _print_css() -> str:
        return """
@page { size: A4; margin: 16mm; }
body { font-family: Arial, sans-serif; color: #172026; font-size: 11px; }
header { border-bottom: 2px solid #187a59; margin-bottom: 18px; padding-bottom: 10px; }
.eyebrow { color: #187a59; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; }
h1 { font-size: 24px; margin: 6px 0; }
h2 { font-size: 15px; margin: 18px 0 8px; }
.cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
article { border: 1px solid #cfd8dc; padding: 10px; border-radius: 4px; }
article span { display: block; color: #5c6b73; }
article strong { display: block; font-size: 18px; margin-top: 4px; }
table { width: 100%; border-collapse: collapse; page-break-inside: avoid; }
th, td { border: 1px solid #d7e0e4; padding: 6px; text-align: left; }
th { background: #eef5f2; }
footer { margin-top: 18px; color: #5c6b73; border-top: 1px solid #cfd8dc; padding-top: 8px; }
"""

    @staticmethod
    def _title(request: ReportRequest) -> str:
        return f"Reporte {request.template.value.replace('_', ' ').title()} - {request.company_id}"

    @staticmethod
    def _report_id(request: ReportRequest, created_at: datetime) -> str:
        timestamp = created_at.strftime("%Y%m%d%H%M%S")
        return f"RPT-{request.company_id}-{request.template.value.upper()}-{timestamp}"

    @staticmethod
    def _nas_uri(request: ReportRequest, report_id: str) -> str:
        scope = request.project_id or request.program_id or "corporate"
        return f"nas://{request.company_id}/reports/{scope}/{report_id}.html"

    def _audit_event(self, request: ReportRequest, manifest: ReportManifest) -> None:
        if self._audit is None:
            return
        self._audit.save(
            AuditEvent(
                actor=request.requested_by,
                action="corporate_report.issued",
                entity_type="report",
                entity_id=manifest.report_id,
                detail=(
                    f"{manifest.title}; checksum={manifest.checksum_sha256}; "
                    f"nas={manifest.nas_logical_uri}"
                ),
            )
        )
