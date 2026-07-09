# PROMPT HARDENING-004 - Corporate PDF Reporting

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0018: Corporate executive dashboard.
- ADR-0019: NAS Corporate Information Center.
- ADR-0025: Corporate Portfolio Domain.

## Objective

Evolve Corporate Reporting & Print Engine into productive PDF reporting with corporate templates, traceability, checksum, and NAS registry metadata.

## Delivered

- Corporate PDF generation using `reportlab`.
- Corporate report structure:
  - Cover page.
  - Index.
  - KPI section.
  - Portfolio section.
  - GIS summary section.
  - Audit section.
  - Signature and metadata section.
- PDF export endpoints:
  - `POST /api/v1/reports/issue/pdf`
  - `POST /api/v1/reports/issue/pdf/download`
- PDF artifact writing under configurable `CONTROL_TOWER_REPORT_OUTPUT_DIR`, defaulting to `output/pdf`.
- Binary PDF SHA-256 checksum in `ReportManifest`.
- PDF path and file size in `CorporatePrintReport`.
- NAS information asset registration for issued PDF reports.
- Audit trail for issued PDF reports and NAS registration.
- Unit and contract tests for PDF generation, API download, checksum, and NAS metadata registration.

## Notes

- The Tower emits consolidated corporate reports only.
- The Tower does not edit WEB SIG data, GIS geometry, or project operation records.
- The database stores metadata and references only; PDF binaries are written to filesystem output.

## Acceptance Criteria

- PDF starts with `%PDF`.
- Report manifest checksum is calculated from the binary PDF.
- NAS logical URI ends with `.pdf`.
- Report is auditable through `corporate_report.issued`.
- Report is registered in NAS as an approved PMO documentation asset.
