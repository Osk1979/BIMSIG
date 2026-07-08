"""Validate permanent architecture guardrails for Corporate Control Tower REV12.

ADR references:
- ADR-0001: REV11 architecture baseline.
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0017: Project Provisioning Engine.
- ADR-0022: Permanent architecture governance rule.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "src/control_tower",
    "src/control_tower/api",
    "src/control_tower/application",
    "src/control_tower/domain",
    "src/control_tower/infrastructure",
    "src/control_tower/presentation",
    "src/control_tower/application/provisioning_service.py",
    "src/control_tower/application/provisioning_adapters.py",
    "src/control_tower/domain/nas/models.py",
    "src/control_tower/infrastructure/adapters/provisioning.py",
    "docs/adr/ADR-0001-record-rev11-as-architecture-baseline.md",
    "docs/adr/ADR-0015-tower-vs-websig-boundary.md",
    "docs/adr/ADR-0017-project-provisioning-engine.md",
    "docs/adr/ADR-0022-permanent-architecture-governance-rule.md",
]

REQUIRED_TRACEABILITY_TERMS = [
    "Corporate Control Tower",
    "WEB SIG",
    "WEB SIG Factory",
    "Project Provisioning Engine",
    "PostGIS",
    "GeoServer",
    "NAS",
    "Google Workspace",
    "BIMSIG Field",
]

FORBIDDEN_INDEPENDENT_APP_DIRS = [
    "websig",
    "websig_factory",
    "bimsig_field",
    "field_app",
    "geoserver_app",
]


def validate() -> list[str]:
    """Return architecture guardrail violations."""

    violations: list[str] = []
    for relative_path in REQUIRED_PATHS:
        if not (ROOT / relative_path).exists():
            violations.append(f"Missing required architecture artifact: {relative_path}")

    traceability_path = ROOT / "docs/traceability/rev11-to-rev12-traceability.md"
    traceability = traceability_path.read_text(encoding="utf-8")
    for term in REQUIRED_TRACEABILITY_TERMS:
        if term not in traceability:
            violations.append(f"Missing traceability term: {term}")

    for app_dir in FORBIDDEN_INDEPENDENT_APP_DIRS:
        if (ROOT / app_dir).exists() or (ROOT / "src" / app_dir).exists():
            violations.append(f"Independent application directory is not allowed: {app_dir}")

    return violations


def main() -> int:
    """Run architecture validation for CI/CD."""

    violations = validate()
    if violations:
        for violation in violations:
            print(violation)
        return 1
    print("Architecture guardrails passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
