from pathlib import Path

from scripts.export_openapi import generate_openapi_text


OPENAPI_PATH = Path("docs/api/openapi.yaml")


def test_versioned_openapi_contract_is_current() -> None:
    expected = generate_openapi_text()

    assert OPENAPI_PATH.read_text(encoding="utf-8") == expected


def test_versioned_openapi_contract_lists_control_tower_routes() -> None:
    contract = OPENAPI_PATH.read_text(encoding="utf-8")

    assert '"/api/v1/projects"' in contract
    assert '"/api/v1/portfolio/summary"' in contract
    assert '"/api/v1/provisioning/websig"' in contract
    assert '"/api/v1/audit/events"' in contract
    assert '"/api/v1/operational/health"' in contract
