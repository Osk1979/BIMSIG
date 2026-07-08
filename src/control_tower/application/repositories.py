"""Repository ports for durable Corporate Control Tower state.

ADR references:
- ADR-0002: Layered modular API scaffold.
- ADR-0005: Persistence strategy.
- ADR-0013: Database schema and migrations.
"""

from __future__ import annotations

from typing import Protocol

from control_tower.domain.audit import AuditEvent
from control_tower.domain.corporate_gis_intelligence import CorporateGisSource, CorporateLayer
from control_tower.domain.corporate_workflow import CorporateWorkflowInstance, CorporateWorkflowTransition
from control_tower.domain.enterprise import (
    AuthIdentity,
    Company,
    CompanyLicense,
    CompanyMembership,
    LicensePlan,
    ProjectMembership,
    RolePermission,
    Specialty,
    User,
    UserHistoryEvent,
    UserSpecialty,
)
from control_tower.domain.enterprise_wizard import EnterpriseWizardSession
from control_tower.domain.gis import (
    GeoServerDatastore,
    GeoServerLayer,
    GeoServerWorkspace,
    PostgisSchema,
    ProjectGisBinding,
)
from control_tower.domain.nas import InformationAsset, InformationBackup, InformationSnapshot, InformationVersion
from control_tower.domain.portfolio import PortfolioProject
from control_tower.domain.portfolio import CorporateCustomer, CorporateProgram
from control_tower.domain.provisioning import ProvisioningRequest


class CorporateCustomerRepository(Protocol):
    """Persistence port for portfolio customer records."""

    def save(self, customer: CorporateCustomer) -> CorporateCustomer:
        """Persist a corporate customer."""

    def list_by_company(self, company_id: str) -> list[CorporateCustomer]:
        """Return customers for one company."""

    def get(self, customer_id: str) -> CorporateCustomer | None:
        """Return one customer when it exists."""


class CorporateProgramRepository(Protocol):
    """Persistence port for portfolio program records."""

    def save(self, program: CorporateProgram) -> CorporateProgram:
        """Persist a corporate program."""

    def list_by_company(self, company_id: str) -> list[CorporateProgram]:
        """Return programs for one company."""

    def get(self, program_id: str) -> CorporateProgram | None:
        """Return one program when it exists."""


class PortfolioProjectRepository(Protocol):
    """Persistence port for portfolio projects."""

    def save(self, project: PortfolioProject) -> PortfolioProject:
        """Persist a portfolio project."""

    def list(self) -> list[PortfolioProject]:
        """Return all persisted portfolio projects."""

    def list_by_company(self, company_id: str) -> list[PortfolioProject]:
        """Return projects for one company."""

    def get(self, project_id: str) -> PortfolioProject | None:
        """Return one persisted project when it exists."""

    def get_by_company(self, company_id: str, project_id: str) -> PortfolioProject | None:
        """Return one project inside one company when it exists."""

    def exists(self, project_id: str) -> bool:
        """Return whether a project exists."""


class ProvisioningRequestRepository(Protocol):
    """Persistence port for WEB SIG provisioning requests."""

    def save(self, request: ProvisioningRequest) -> ProvisioningRequest:
        """Persist a provisioning request."""

    def list(self) -> list[ProvisioningRequest]:
        """Return all persisted provisioning requests."""

    def list_by_company(self, company_id: str) -> list[ProvisioningRequest]:
        """Return persisted provisioning requests for one company."""


class AuditEventRepository(Protocol):
    """Persistence port for audit events."""

    def save(self, event: AuditEvent) -> AuditEvent:
        """Persist an audit event."""

    def list(self, limit: int = 100) -> list[AuditEvent]:
        """Return recent audit events."""


class CompanyRepository(Protocol):
    """Persistence port for enterprise companies."""

    def save(self, company: Company) -> Company:
        """Persist a company."""

    def list(self) -> list[Company]:
        """Return all companies."""

    def get(self, company_id: str) -> Company | None:
        """Return one company when it exists."""


class UserRepository(Protocol):
    """Persistence port for platform users."""

    def save(self, user: User) -> User:
        """Persist a user."""

    def list(self) -> list[User]:
        """Return all users."""

    def get(self, user_id: str) -> User | None:
        """Return one user when it exists."""


class CompanyMembershipRepository(Protocol):
    """Persistence port for company memberships."""

    def save(self, membership: CompanyMembership) -> CompanyMembership:
        """Persist a company membership."""

    def list_by_company(self, company_id: str) -> list[CompanyMembership]:
        """Return memberships for a company."""


class LicensePlanRepository(Protocol):
    """Persistence port for license plans."""

    def save(self, plan: LicensePlan) -> LicensePlan:
        """Persist a license plan."""

    def list(self) -> list[LicensePlan]:
        """Return license plans."""

    def get(self, plan_id: str) -> LicensePlan | None:
        """Return one license plan when it exists."""


class CompanyLicenseRepository(Protocol):
    """Persistence port for company license assignments."""

    def save(self, license_assignment: CompanyLicense) -> CompanyLicense:
        """Persist a company license assignment."""

    def list_by_company(self, company_id: str) -> list[CompanyLicense]:
        """Return license assignments for a company."""


class SpecialtyRepository(Protocol):
    """Persistence port for corporate specialties."""

    def save(self, specialty: Specialty) -> Specialty:
        """Persist a specialty."""

    def list(self) -> list[Specialty]:
        """Return all specialties."""

    def get(self, specialty_id: str) -> Specialty | None:
        """Return one specialty when it exists."""


class UserSpecialtyRepository(Protocol):
    """Persistence port for user specialty assignments."""

    def save(self, assignment: UserSpecialty) -> UserSpecialty:
        """Persist a user specialty assignment."""

    def list_by_user(self, user_id: str) -> list[UserSpecialty]:
        """Return specialties assigned to one user."""


class ProjectMembershipRepository(Protocol):
    """Persistence port for project memberships."""

    def save(self, membership: ProjectMembership) -> ProjectMembership:
        """Persist a project membership."""

    def list_by_project(self, company_id: str, project_id: str) -> list[ProjectMembership]:
        """Return project memberships."""

    def list_by_user(self, user_id: str) -> list[ProjectMembership]:
        """Return project memberships for one user."""


class RolePermissionRepository(Protocol):
    """Persistence port for role permissions."""

    def save(self, permission: RolePermission) -> RolePermission:
        """Persist a role permission."""

    def list_by_role(self, role: str) -> list[RolePermission]:
        """Return permissions for one role."""


class AuthIdentityRepository(Protocol):
    """Persistence port for authentication and SSO identities."""

    def save(self, identity: AuthIdentity) -> AuthIdentity:
        """Persist an authentication identity."""

    def list_by_user(self, user_id: str) -> list[AuthIdentity]:
        """Return identities for one user."""

    def get_by_provider_subject(self, provider: str, subject: str) -> AuthIdentity | None:
        """Return one identity for provider and subject."""


class UserHistoryRepository(Protocol):
    """Persistence port for user security history."""

    def save(self, event: UserHistoryEvent) -> UserHistoryEvent:
        """Persist a user history event."""

    def list_by_user(self, user_id: str) -> list[UserHistoryEvent]:
        """Return history events for one user."""


class InformationAssetRepository(Protocol):
    """Persistence port for Corporate Information Center assets."""

    def save_asset(self, asset: InformationAsset) -> InformationAsset:
        """Persist an information asset."""

    def list_assets_by_company(self, company_id: str) -> list[InformationAsset]:
        """Return information assets for one company."""

    def get_asset(self, asset_id: str) -> InformationAsset | None:
        """Return one information asset when it exists."""

    def save_version(self, version: InformationVersion) -> InformationVersion:
        """Persist an information asset version."""

    def list_versions(self, asset_id: str) -> list[InformationVersion]:
        """Return versions for one asset."""

    def save_snapshot(self, snapshot: InformationSnapshot) -> InformationSnapshot:
        """Persist an information snapshot."""

    def list_snapshots_by_company(self, company_id: str) -> list[InformationSnapshot]:
        """Return snapshots for one company."""

    def save_backup(self, backup: InformationBackup) -> InformationBackup:
        """Persist an information backup manifest."""

    def list_backups_by_company(self, company_id: str) -> list[InformationBackup]:
        """Return backup manifests for one company."""


class CorporateGisRepository(Protocol):
    """Persistence port for corporate GIS administration."""

    def save_postgis_schema(self, schema: PostgisSchema) -> PostgisSchema:
        """Persist a PostGIS schema reference."""

    def get_postgis_schema(self, schema_id: str) -> PostgisSchema | None:
        """Return one PostGIS schema reference."""

    def list_postgis_schemas(self, company_id: str, project_id: str | None = None) -> list[PostgisSchema]:
        """Return PostGIS schemas by company and optional project."""

    def save_workspace(self, workspace: GeoServerWorkspace) -> GeoServerWorkspace:
        """Persist a GeoServer workspace reference."""

    def get_workspace(self, workspace_id: str) -> GeoServerWorkspace | None:
        """Return one GeoServer workspace reference."""

    def list_workspaces(self, company_id: str, project_id: str | None = None) -> list[GeoServerWorkspace]:
        """Return GeoServer workspaces by company and optional project."""

    def save_datastore(self, datastore: GeoServerDatastore) -> GeoServerDatastore:
        """Persist a GeoServer datastore reference."""

    def get_datastore(self, datastore_id: str) -> GeoServerDatastore | None:
        """Return one GeoServer datastore reference."""

    def list_datastores(self, company_id: str, project_id: str | None = None) -> list[GeoServerDatastore]:
        """Return GeoServer datastores by company and optional project."""

    def save_layer(self, layer: GeoServerLayer) -> GeoServerLayer:
        """Persist a GeoServer layer reference."""

    def list_layers(self, company_id: str, project_id: str | None = None) -> list[GeoServerLayer]:
        """Return GeoServer layers by company and optional project."""

    def save_binding(self, binding: ProjectGisBinding) -> ProjectGisBinding:
        """Persist a project GIS binding."""

    def get_binding(self, company_id: str, project_id: str) -> ProjectGisBinding | None:
        """Return the GIS binding for one project."""


class CorporateGisIntelligenceRepository(Protocol):
    """Persistence port for Corporate GIS Intelligence references."""

    def save_source(self, source: CorporateGisSource) -> CorporateGisSource:
        """Persist a published WEB SIG GIS source reference."""

    def get_source(self, source_id: str) -> CorporateGisSource | None:
        """Return one GIS source reference."""

    def list_sources(self, company_id: str, project_id: str | None = None) -> list[CorporateGisSource]:
        """Return GIS sources by company and optional project."""

    def save_layer(self, layer: CorporateLayer) -> CorporateLayer:
        """Persist a corporate GIS intelligence layer."""

    def list_layers(self, company_id: str, project_id: str | None = None) -> list[CorporateLayer]:
        """Return corporate layers by company and optional project."""


class CorporateWorkflowRepository(Protocol):
    """Persistence port for Corporate Workflow Engine state."""

    def save_workflow(self, workflow: CorporateWorkflowInstance) -> CorporateWorkflowInstance:
        """Persist a workflow instance."""

    def get_workflow(self, workflow_id: str) -> CorporateWorkflowInstance | None:
        """Return one workflow instance."""

    def list_workflows(self, company_id: str) -> list[CorporateWorkflowInstance]:
        """Return workflow instances for one company."""

    def save_transition(self, transition: CorporateWorkflowTransition) -> CorporateWorkflowTransition:
        """Persist a workflow transition."""

    def list_transitions(self, workflow_id: str) -> list[CorporateWorkflowTransition]:
        """Return transitions for one workflow."""


class EnterpriseWizardRepository(Protocol):
    """Persistence port for resumable Enterprise Wizard sessions."""

    def save(self, session: EnterpriseWizardSession) -> EnterpriseWizardSession:
        """Persist one wizard session."""

    def get(self, wizard_id: str) -> EnterpriseWizardSession | None:
        """Return one wizard session."""

    def list(self) -> list[EnterpriseWizardSession]:
        """Return wizard sessions."""
