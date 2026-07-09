from control_tower.application.infrastructure_connectors import (
    InfrastructureConnectorAction,
    InfrastructureConnectorKind,
    InfrastructureConnectorResult,
    InfrastructureConnectorStatus,
)
from control_tower.application.observability_service import ObservabilityService


def test_observability_service_records_api_metrics_and_prometheus_output() -> None:
    service = ObservabilityService("corporate-control-tower", "REV12")

    service.record_request("get", "/health", 200, 10.0)
    service.record_request("GET", "/health", 200, 30.0)

    metrics = service.metrics()
    prometheus = service.prometheus()

    assert metrics.total_requests == 2
    assert metrics.error_requests == 0
    assert metrics.routes[0].count == 2
    assert metrics.routes[0].avg_duration_ms == 20.0
    assert 'control_tower_http_requests_total{method="GET",path="/health",status_code="200"} 2' in prometheus


def test_observability_service_builds_deep_health_and_connector_alerts() -> None:
    service = ObservabilityService("corporate-control-tower", "REV12")
    connector = InfrastructureConnectorResult(
        connector=InfrastructureConnectorKind.POSTGIS,
        action=InfrastructureConnectorAction.HEALTH,
        status=InfrastructureConnectorStatus.MISCONFIGURED,
        configured=False,
        detail="PostGIS database URL is not configured.",
    )

    health = service.health("ok", [connector])
    alerts = service.alerts([connector])

    assert health.status == "degraded"
    assert alerts[0].alert_id == "connector-postgis"
    assert alerts[0].severity == "warning"
