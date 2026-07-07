"""Provisioning adapter ports.

ADR references:
- ADR-0003: Project provisioning as a port.
- ADR-0007: NAS integration.
- ADR-0008: PostGIS integration.
- ADR-0009: GeoServer integration.
- ADR-0017: Project Provisioning Engine.
"""

from typing import Protocol

from control_tower.domain.provisioning import ProvisioningResourceType, ProvisioningStep


class ProvisioningAdapter(Protocol):
    """Port implemented by infrastructure-specific provisioning adapters."""

    resource_type: ProvisioningResourceType

    def plan(self, context: "ProvisioningAdapterContext") -> ProvisioningStep:
        """Return the step that would be executed without side effects."""

    def execute(self, context: "ProvisioningAdapterContext") -> ProvisioningStep:
        """Execute the adapter action and return the resulting step."""


class ProvisioningAdapterContext(Protocol):
    """Context required by infrastructure adapters during provisioning."""

    company_id: str
    project_id: str
    websig_slug: str
    dashboard_id: str
    document_structure: list[str]
    catalogs: list[str]
