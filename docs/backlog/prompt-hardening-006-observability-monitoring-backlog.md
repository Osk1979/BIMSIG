# PROMPT HARDENING-006 - Observability & Monitoring

ADR references:
- ADR-0021: DevSecOps operating model.
- ADR-0024: Corporate operating model.

## Objective

Enable Corporate Control Tower to operate in real environments with structured logs, API metrics, deep health, connector visibility, operational audit, basic alerts, and Prometheus/OpenTelemetry-ready exports.

## Delivered

- Structured JSON access logs through the DevSecOps middleware.
- Correlation ID support:
  - Reads `X-Correlation-ID`.
  - Falls back to `X-Request-ID`.
  - Returns `X-Correlation-ID` in responses.
- In-process API metrics registry:
  - Request counts.
  - Error counts.
  - Route duration sum, average, and max.
- Deep health endpoint:
  - `GET /api/v1/observability/health/deep`
- Connector observability endpoint:
  - `GET /api/v1/observability/connectors`
- Observability dashboard endpoint:
  - `GET /api/v1/observability/dashboard`
- Prometheus text export:
  - `GET /metrics`
- OpenTelemetry-ready JSON export:
  - `GET /api/v1/observability/otel`
- Operational audit for slow requests and server errors.
- Basic alerts for:
  - API 5xx errors.
  - Slow routes.
  - Misconfigured, unhealthy, or failed connectors.
- Unit and contract tests.

## Guardrails

- No mandatory external observability service was introduced.
- No WEB SIG operational logic was implemented.
- Existing PostGIS, GeoServer, NAS, and Google Drive connectors remain governed through the Tower.
- Observability is implemented as an application service, not as a new business domain.
