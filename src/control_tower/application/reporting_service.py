"""Corporate reporting and print application service.

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0018: Corporate executive dashboard.
- ADR-0019: NAS Corporate Information Center.
- ADR-0025: Corporate Portfolio Domain.
"""

from __future__ import annotations

from datetime import UTC, datetime
from io import BytesIO
from hashlib import sha256
from html import escape
from pathlib import Path

from control_tower.application.dashboard_service import DashboardService
from control_tower.application.repositories import AuditEventRepository
from control_tower.domain.audit import AuditEvent
from control_tower.domain.dashboard import CorporateDashboard
from control_tower.domain.nas import (
    InformationAsset,
    InformationAssetStatus,
    InformationAssetType,
    InformationCategory,
)
from control_tower.domain.reports import ReportFormat
from control_tower.domain.reports import CorporatePrintReport, ReportManifest, ReportRequest

from .nas_service import NasInformationCenterService


class CorporateReportingService:
    """Issues print-ready corporate reports from consolidated Tower data."""

    def __init__(
        self,
        dashboard_service: DashboardService,
        audit_repository: AuditEventRepository | None = None,
        nas_service: NasInformationCenterService | None = None,
        output_dir: str | None = None,
    ) -> None:
        self._dashboard = dashboard_service
        self._audit = audit_repository
        self._nas = nas_service
        self._output_dir = Path(output_dir or "output/pdf")

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

    def export_pdf(self, request: ReportRequest) -> CorporatePrintReport:
        """Issue a governed corporate PDF report and register its NAS metadata."""

        pdf_request = request.model_copy(update={"output_format": ReportFormat.PDF})
        dashboard = self._dashboard.executive_dashboard(pdf_request.company_id)
        html = self._render_html(pdf_request, dashboard)
        created_at = datetime.now(UTC)
        report_id = self._report_id(pdf_request, created_at)
        pdf_bytes = self._render_pdf(pdf_request, dashboard, report_id, created_at)
        checksum = sha256(pdf_bytes).hexdigest()
        pdf_path = self._write_pdf(report_id, pdf_bytes)
        manifest = ReportManifest(
            report_id=report_id,
            company_id=pdf_request.company_id,
            template=pdf_request.template,
            scope=pdf_request.scope,
            title=self._title(pdf_request),
            output_format=ReportFormat.PDF,
            requested_by=pdf_request.requested_by,
            project_id=pdf_request.project_id,
            program_id=pdf_request.program_id,
            filters=pdf_request.filters,
            data_sources=[
                "portfolio_domain",
                "executive_dashboard",
                "corporate_gis_intelligence",
                "nas_information_center",
                "audit_events",
            ],
            nas_logical_uri=self._nas_uri(pdf_request, report_id, extension="pdf"),
            checksum_sha256=checksum,
            status="issued",
            created_at=created_at,
        )
        report = CorporatePrintReport(
            manifest=manifest,
            html=html,
            print_css=self._print_css(),
            pdf_path=str(pdf_path),
            pdf_size_bytes=len(pdf_bytes),
        )
        self._register_nas_report(pdf_request, report)
        self._audit_event(pdf_request, report.manifest)
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
            nas_logical_uri=self._nas_uri(request, report_id, extension="html"),
            checksum_sha256=checksum,
            status=status,
            created_at=created_at,
        )
        return CorporatePrintReport(manifest=manifest, html=html, print_css=self._print_css())

    def _render_pdf(
        self,
        request: ReportRequest,
        dashboard: CorporateDashboard,
        report_id: str,
        created_at: datetime,
    ) -> bytes:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            PageBreak,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
        )

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=16 * mm,
            leftMargin=16 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
            title=self._title(request),
            author=request.requested_by,
            subject="Corporate Control Tower report",
        )
        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name="CoverTitle",
                parent=styles["Title"],
                fontSize=24,
                leading=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#123026"),
                spaceAfter=16,
            )
        )
        styles.add(
            ParagraphStyle(
                name="SectionTitle",
                parent=styles["Heading2"],
                fontSize=14,
                leading=18,
                textColor=colors.HexColor("#187a59"),
                spaceBefore=10,
                spaceAfter=8,
            )
        )
        story: list = []
        generated = created_at.strftime("%Y-%m-%d %H:%M UTC")
        story.extend(
            [
                Spacer(1, 42 * mm),
                Paragraph("BIMSIG Enterprise", styles["Heading2"]),
                Paragraph(self._title(request), styles["CoverTitle"]),
                Paragraph(f"Empresa: {request.company_id}", styles["Normal"]),
                Paragraph(f"Reporte: {report_id}", styles["Normal"]),
                Paragraph(f"Solicitante: {request.requested_by}", styles["Normal"]),
                Paragraph(f"Emitido: {generated}", styles["Normal"]),
                Spacer(1, 14 * mm),
                Paragraph(
                    "Documento corporativo emitido por la Corporate Control Tower. "
                    "La Torre consolida informacion, no edita geometria ni opera WEB SIG.",
                    styles["Normal"],
                ),
                PageBreak(),
                Paragraph("Indice", styles["SectionTitle"]),
                self._table(
                    [["Seccion", "Contenido"], ["1", "KPIs"], ["2", "Portafolio"], ["3", "GIS summary"], ["4", "Auditoria"], ["5", "Firma y metadata"]],
                    [35 * mm, 120 * mm],
                ),
                PageBreak(),
                Paragraph("1. KPIs", styles["SectionTitle"]),
                self._table(self._kpi_rows(dashboard), [65 * mm, 35 * mm, 45 * mm]),
                Paragraph("2. Portafolio", styles["SectionTitle"]),
                self._table(self._portfolio_rows(dashboard), [42 * mm, 32 * mm, 26 * mm, 26 * mm, 24 * mm]),
                PageBreak(),
                Paragraph("3. GIS Summary", styles["SectionTitle"]),
                self._table(self._gis_rows(dashboard), [70 * mm, 50 * mm, 35 * mm]),
                Paragraph("4. Auditoria", styles["SectionTitle"]),
                self._table(self._audit_rows(), [45 * mm, 40 * mm, 70 * mm]),
                Paragraph("5. Firma y Metadata", styles["SectionTitle"]),
                self._table(
                    [
                        ["Campo", "Valor"],
                        ["Reporte", report_id],
                        ["Formato", ReportFormat.PDF.value],
                        ["NAS logical URI", self._nas_uri(request, report_id, extension="pdf")],
                        ["Responsable", request.requested_by],
                        ["Estado", "issued"],
                    ],
                    [45 * mm, 110 * mm],
                ),
            ]
        )
        doc.build(story, onFirstPage=self._page_footer, onLaterPages=self._page_footer)
        return buffer.getvalue()

    @staticmethod
    def _table(rows: list[list[str]], widths: list[float]):
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle

        table = Table(rows, colWidths=widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf4ef")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#123026")),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#c8d6d0")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7faf9")]),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        return table

    @staticmethod
    def _page_footer(canvas, doc) -> None:
        from reportlab.lib import colors
        from reportlab.lib.units import mm

        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#5c6b73"))
        canvas.drawString(16 * mm, 10 * mm, "BIMSIG Enterprise - Corporate Control Tower")
        canvas.drawRightString(195 * mm, 10 * mm, f"Pagina {doc.page}")
        canvas.restoreState()

    @staticmethod
    def _kpi_rows(dashboard: CorporateDashboard) -> list[list[str]]:
        metrics = dashboard.kpis + dashboard.production + dashboard.schedule + dashboard.environmental + dashboard.ssoma
        rows = [["KPI", "Valor", "Estado"]]
        rows.extend([metric.label, metric.value, metric.status] for metric in metrics)
        return rows

    @staticmethod
    def _portfolio_rows(dashboard: CorporateDashboard) -> list[list[str]]:
        rows = [["Proyecto", "Programa", "Ciclo", "Gobierno", "WEB SIG"]]
        rows.extend(
            [
                item.project_name,
                item.program or "Programa pendiente",
                item.lifecycle_stage,
                item.governance_status,
                item.websig,
            ]
            for item in dashboard.portfolio_governance
        )
        if len(rows) == 1:
            rows.append(["Sin proyectos", "-", "-", "-", "-"])
        return rows

    @staticmethod
    def _gis_rows(dashboard: CorporateDashboard) -> list[list[str]]:
        summary = dashboard.gis_intelligence
        rows = [["Indicador GIS", "Valor", "Fuente"]]
        if summary is None:
            rows.append(["GIS corporativo", "Sin fuentes activas", "corporate_gis_intelligence"])
            return rows
        rows.extend(
            [
                ["Proyectos georreferenciados", str(summary.total_projects_georeferenced), "corporate_layers"],
                ["Proyectos con capas activas", str(summary.projects_with_active_layers), "corporate_layers"],
                ["Riesgos espaciales", str(summary.projects_with_spatial_risks), "corporate_layers"],
                ["Alertas ambientales", str(summary.projects_with_environmental_alerts), "corporate_layers"],
                ["Restricciones activas", str(summary.projects_with_active_restrictions), "corporate_layers"],
                ["Avance espacial agregado", f"{summary.aggregated_spatial_progress}%", "corporate_layers"],
            ]
        )
        return rows

    def _audit_rows(self) -> list[list[str]]:
        rows = [["Accion", "Entidad", "Detalle"]]
        if self._audit is None:
            rows.append(["audit.unavailable", "audit", "Repositorio de auditoria no configurado"])
            return rows
        events = self._audit.list(limit=8)
        rows.extend([event.action, event.entity_type, event.detail or event.entity_id] for event in events)
        if len(rows) == 1:
            rows.append(["Sin eventos", "audit", "No hay eventos recientes"])
        return rows

    def _write_pdf(self, report_id: str, pdf_bytes: bytes) -> Path:
        self._output_dir.mkdir(parents=True, exist_ok=True)
        path = self._output_dir / f"{report_id}.pdf"
        path.write_bytes(pdf_bytes)
        return path

    def _register_nas_report(self, request: ReportRequest, report: CorporatePrintReport) -> None:
        if self._nas is None or not request.register_nas_reference:
            return
        self._nas.register_asset(
            InformationAsset(
                asset_id=f"NAS-{report.manifest.report_id}",
                company_id=request.company_id,
                project_id=request.project_id,
                name=report.manifest.title,
                asset_type=InformationAssetType.DOCUMENTATION,
                category=InformationCategory.PMO,
                logical_uri=report.manifest.nas_logical_uri,
                version="v1",
                status=InformationAssetStatus.APPROVED,
                metadata={
                    "report_id": report.manifest.report_id,
                    "template": report.manifest.template.value,
                    "format": report.manifest.output_format.value,
                    "pdf_path": report.pdf_path or "",
                    "issued_by": request.requested_by,
                },
                checksum_sha256=report.manifest.checksum_sha256,
            )
        )

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
    def _nas_uri(request: ReportRequest, report_id: str, *, extension: str) -> str:
        scope = request.project_id or request.program_id or "corporate"
        return f"nas://{request.company_id}/reports/{scope}/{report_id}.{extension}"

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
