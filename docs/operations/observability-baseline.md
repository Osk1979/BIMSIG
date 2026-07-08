# Observability Baseline

## Runtime Signals

Corporate Control Tower REV12 exposes:

- `GET /health`: basic liveness.
- `GET /api/v1/operational/health`: service and database health.
- `GET /api/v1/operational/readiness`: readiness for deployment and orchestration checks.
- `GET /api/v1/operational/version`: service version metadata.

## Request Traceability

Every HTTP response includes:

- `X-Request-ID`: caller-provided or generated correlation ID.
- `X-Response-Time-Ms`: request duration in milliseconds.

The API emits HTTP access log events with method, path, status code, duration, and request ID.

## Security Headers

Every HTTP response includes baseline security headers:

- `X-Content-Type-Options`.
- `X-Frame-Options`.
- `Referrer-Policy`.
- `Permissions-Policy`.

## Deferred Integrations

- Central log aggregation.
- Metrics time-series backend.
- Alert rules.
- Trace exporter.
- Error reporting backend.
