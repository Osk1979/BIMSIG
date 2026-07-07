"""Export the FastAPI OpenAPI contract to docs/api/openapi.yaml.

ADR references:
- ADR-0002: Layered modular API scaffold.
- ADR-0012: CI/CD strategy.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from control_tower.api.app import create_app


DEFAULT_OUTPUT = Path("docs/api/openapi.yaml")


def generate_openapi_text() -> str:
    """Generate a deterministic OpenAPI document."""

    app = create_app(database_url="sqlite:///:memory:")
    contract = app.openapi()
    return json.dumps(contract, indent=2, sort_keys=True) + "\n"


def export_openapi(output_path: Path = DEFAULT_OUTPUT) -> None:
    """Write the generated OpenAPI document to disk."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(generate_openapi_text(), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the OpenAPI contract.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output path for the versioned OpenAPI contract.",
    )
    args = parser.parse_args()
    export_openapi(args.output)


if __name__ == "__main__":
    main()
