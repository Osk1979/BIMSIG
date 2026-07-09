"""Operational observability for Corporate Control Tower.

ADR references:
- ADR-0021: DevSecOps operating model.
- ADR-0024: Corporate operating model.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock

from pydantic import BaseModel, Field

from control_tower.application.infrastructure_connectors import InfrastructureConnectorResult


class ApiRouteMetric(BaseModel):
    """Aggregated API metric for one method, route, and status code."""

    method: str
    path: str
    status_code: int
    count: int
    total_duration_ms: float
    avg_duration_ms: float
    max_duration_ms: float


class ObservabilityMetrics(BaseModel):
    """Current API metrics snapshot."""

    service: str
    revision: str
    total_requests: int
    error_requests: int
    routes: list[ApiRouteMetric]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ObservabilityAlert(BaseModel):
    """Basic operational alert emitted without external services."""

    alert_id: str
    severity: str
    source: str
    title: str
    detail: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ObservabilityHealth(BaseModel):
    """Deep health state for platform and governed infrastructure."""

    status: str
    service: str
    revision: str
    database: str
    connectors: list[InfrastructureConnectorResult]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ObservabilityDashboard(BaseModel):
    """Operational dashboard payload for production monitoring."""

    status: str
    service: str
    revision: str
    metrics: ObservabilityMetrics
    health: ObservabilityHealth
    alerts: list[ObservabilityAlert]
    correlation_id: str | None = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ObservabilityOtelExport(BaseModel):
    """OpenTelemetry-ready payload without requiring an external collector."""

    resource: dict[str, str]
    metrics: ObservabilityMetrics
    alerts: list[ObservabilityAlert]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


@dataclass
class _MetricBucket:
    count: int = 0
    total_duration_ms: float = 0.0
    max_duration_ms: float = 0.0


class ObservabilityService:
    """Collects request metrics, structured logs, deep health, and basic alerts."""

    def __init__(self, service: str, revision: str, slow_request_ms: float = 1000.0) -> None:
        self._service = service
        self._revision = revision
        self._slow_request_ms = slow_request_ms
        self._lock = Lock()
        self._buckets: dict[tuple[str, str, int], _MetricBucket] = {}
        self._total_requests = 0
        self._error_requests = 0

    def record_request(self, method: str, path: str, status_code: int, duration_ms: float) -> None:
        """Record one HTTP request after response generation."""

        key = (method.upper(), path, status_code)
        with self._lock:
            bucket = self._buckets.setdefault(key, _MetricBucket())
            bucket.count += 1
            bucket.total_duration_ms = round(bucket.total_duration_ms + duration_ms, 2)
            bucket.max_duration_ms = max(bucket.max_duration_ms, duration_ms)
            self._total_requests += 1
            if status_code >= 500:
                self._error_requests += 1

    def metrics(self) -> ObservabilityMetrics:
        """Return an immutable API metrics snapshot."""

        with self._lock:
            routes = [
                ApiRouteMetric(
                    method=method,
                    path=path,
                    status_code=status_code,
                    count=bucket.count,
                    total_duration_ms=round(bucket.total_duration_ms, 2),
                    avg_duration_ms=round(bucket.total_duration_ms / bucket.count, 2),
                    max_duration_ms=round(bucket.max_duration_ms, 2),
                )
                for (method, path, status_code), bucket in self._buckets.items()
            ]
            return ObservabilityMetrics(
                service=self._service,
                revision=self._revision,
                total_requests=self._total_requests,
                error_requests=self._error_requests,
                routes=sorted(routes, key=lambda item: (item.path, item.method, item.status_code)),
            )

    def health(
        self,
        database: str,
        connectors: list[InfrastructureConnectorResult],
    ) -> ObservabilityHealth:
        """Build deep health status from database and connector checks."""

        connector_degraded = any(
            result.status.value in {"unhealthy", "misconfigured", "failed"} for result in connectors
        )
        status = "ok"
        if database != "ok":
            status = "down"
        elif connector_degraded:
            status = "degraded"
        return ObservabilityHealth(
            status=status,
            service=self._service,
            revision=self._revision,
            database=database,
            connectors=connectors,
        )

    def alerts(
        self,
        connectors: list[InfrastructureConnectorResult],
    ) -> list[ObservabilityAlert]:
        """Return basic local alerts for API and connector operations."""

        alerts: list[ObservabilityAlert] = []
        metrics = self.metrics()
        if metrics.error_requests:
            alerts.append(
                ObservabilityAlert(
                    alert_id="api-5xx",
                    severity="critical",
                    source="api",
                    title="API errors detected",
                    detail=f"{metrics.error_requests} server errors recorded.",
                )
            )
        for route in metrics.routes:
            if route.max_duration_ms >= self._slow_request_ms:
                alerts.append(
                    ObservabilityAlert(
                        alert_id=f"slow-{route.method}-{route.path}",
                        severity="warning",
                        source="api",
                        title="Slow API request",
                        detail=f"{route.method} {route.path} reached {route.max_duration_ms} ms.",
                    )
                )
        for connector in connectors:
            if connector.status.value in {"unhealthy", "misconfigured", "failed"}:
                alerts.append(
                    ObservabilityAlert(
                        alert_id=f"connector-{connector.connector.value}",
                        severity="warning",
                        source="connector",
                        title=f"{connector.connector.value} requires attention",
                        detail=connector.detail,
                    )
                )
        return alerts

    def dashboard(
        self,
        database: str,
        connectors: list[InfrastructureConnectorResult],
        correlation_id: str | None = None,
    ) -> ObservabilityDashboard:
        """Build the production observability dashboard payload."""

        health = self.health(database, connectors)
        return ObservabilityDashboard(
            status=health.status,
            service=self._service,
            revision=self._revision,
            metrics=self.metrics(),
            health=health,
            alerts=self.alerts(connectors),
            correlation_id=correlation_id,
        )

    def otel_export(self, connectors: list[InfrastructureConnectorResult]) -> ObservabilityOtelExport:
        """Return an OpenTelemetry-ready export payload for future collectors."""

        return ObservabilityOtelExport(
            resource={"service.name": self._service, "service.version": self._revision},
            metrics=self.metrics(),
            alerts=self.alerts(connectors),
        )

    def prometheus(self) -> str:
        """Return Prometheus text exposition for current API metrics."""

        lines = [
            "# HELP control_tower_http_requests_total Total HTTP requests.",
            "# TYPE control_tower_http_requests_total counter",
        ]
        for route in self.metrics().routes:
            labels = self._prometheus_labels(route)
            lines.append(f"control_tower_http_requests_total{{{labels}}} {route.count}")
            lines.append(
                f"control_tower_http_request_duration_ms_sum{{{labels}}} {route.total_duration_ms}"
            )
            lines.append(
                f"control_tower_http_request_duration_ms_max{{{labels}}} {route.max_duration_ms}"
            )
        return "\n".join(lines) + "\n"

    def structured_log(
        self,
        *,
        request_id: str,
        correlation_id: str,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        actor: str,
    ) -> str:
        """Serialize one structured access log line as JSON."""

        return json.dumps(
            {
                "event": "http_request",
                "service": self._service,
                "revision": self._revision,
                "request_id": request_id,
                "correlation_id": correlation_id,
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "actor": actor,
                "timestamp": datetime.now(UTC).isoformat(),
            },
            sort_keys=True,
        )

    @staticmethod
    def _prometheus_labels(route: ApiRouteMetric) -> str:
        labels = {
            "method": route.method,
            "path": route.path,
            "status_code": str(route.status_code),
        }
        return ",".join(f'{key}="{value.replace(chr(34), "").replace(chr(92), "")}"' for key, value in labels.items())
