from control_tower.application.infrastructure_connectors import (
    InfrastructureConnectorAction,
    InfrastructureConnectorKind,
    InfrastructureConnectorRequest,
    InfrastructureConnectorResult,
    InfrastructureConnectorService,
    InfrastructureConnectorStatus,
)
from control_tower.infrastructure.adapters.connectors import NasFilesystemInfrastructureConnector

from .fakes import FakeAuditEventRepository


class FakeConnector:
    kind = InfrastructureConnectorKind.POSTGIS

    def health(self) -> InfrastructureConnectorResult:
        return InfrastructureConnectorResult(
            connector=self.kind,
            action=InfrastructureConnectorAction.HEALTH,
            status=InfrastructureConnectorStatus.HEALTHY,
            configured=True,
            detail="ok",
        )

    def validate(self) -> InfrastructureConnectorResult:
        return InfrastructureConnectorResult(
            connector=self.kind,
            action=InfrastructureConnectorAction.VALIDATE,
            status=InfrastructureConnectorStatus.CONFIGURED,
            configured=True,
            detail="configured",
        )

    def dry_run(self, request: InfrastructureConnectorRequest) -> InfrastructureConnectorResult:
        return InfrastructureConnectorResult(
            connector=self.kind,
            action=request.action,
            status=InfrastructureConnectorStatus.PLANNED,
            configured=True,
            reference=f"postgis://schema/{request.target['schema_name']}",
            detail="planned",
        )

    def execute(self, request: InfrastructureConnectorRequest) -> InfrastructureConnectorResult:
        return InfrastructureConnectorResult(
            connector=self.kind,
            action=request.action,
            status=InfrastructureConnectorStatus.EXECUTED,
            configured=True,
            reference=f"postgis://schema/{request.target['schema_name']}",
            detail="executed",
        )


def test_connector_service_dispatches_and_audits() -> None:
    audit = FakeAuditEventRepository()
    service = InfrastructureConnectorService([FakeConnector()], audit)

    result = service.run(
        InfrastructureConnectorKind.POSTGIS,
        InfrastructureConnectorRequest(
            action=InfrastructureConnectorAction.DRY_RUN,
            company_id="CRTG",
            project_id="PSZ-2026",
            target={"schema_name": "crtg_psz_2026"},
        ),
        actor="USR-ADMIN",
    )

    assert result.status == InfrastructureConnectorStatus.PLANNED
    assert result.reference == "postgis://schema/crtg_psz_2026"
    assert audit.events[-1].action == "infrastructure.postgis.dry_run"
    assert audit.events[-1].entity_id == "CRTG/PSZ-2026"


def test_execute_requires_approval_before_connector_side_effects() -> None:
    service = InfrastructureConnectorService([FakeConnector()])

    result = service.run(
        InfrastructureConnectorKind.POSTGIS,
        InfrastructureConnectorRequest(
            action=InfrastructureConnectorAction.EXECUTE,
            target={"schema_name": "crtg_psz_2026"},
        ),
    )

    assert result.status == InfrastructureConnectorStatus.FAILED
    assert result.detail == "Controlled execute requires approved_by."


def test_nas_connector_executes_inside_configured_root(tmp_path) -> None:
    connector = NasFilesystemInfrastructureConnector(str(tmp_path))

    result = connector.execute(
        InfrastructureConnectorRequest(
            action=InfrastructureConnectorAction.EXECUTE,
            company_id="CRTG",
            project_id="PSZ-2026",
            approved_by="USR-ADMIN",
        )
    )

    assert result.status == InfrastructureConnectorStatus.EXECUTED
    assert (tmp_path / "CRTG" / "PSZ-2026" / "websig").is_dir()
