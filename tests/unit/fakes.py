from __future__ import annotations

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
    UserRole,
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
from control_tower.domain.portfolio import CorporateCustomer, CorporateProgram, PortfolioProject
from control_tower.domain.provisioning import ProvisioningRequest


class FakeCompanyRepository:
    def __init__(self) -> None:
        self.companies: dict[str, Company] = {}

    def save(self, company: Company) -> Company:
        self.companies[company.company_id] = company
        return company

    def list(self) -> list[Company]:
        return list(self.companies.values())

    def get(self, company_id: str) -> Company | None:
        return self.companies.get(company_id)


class FakeUserRepository:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}

    def save(self, user: User) -> User:
        self.users[user.user_id] = user
        return user

    def list(self) -> list[User]:
        return list(self.users.values())

    def get(self, user_id: str) -> User | None:
        return self.users.get(user_id)


class FakeMembershipRepository:
    def __init__(self) -> None:
        self.memberships: dict[str, CompanyMembership] = {}

    def save(self, membership: CompanyMembership) -> CompanyMembership:
        self.memberships[membership.membership_id] = membership
        return membership

    def list_by_company(self, company_id: str) -> list[CompanyMembership]:
        return [
            membership
            for membership in self.memberships.values()
            if membership.company_id == company_id
        ]


class FakeSpecialtyRepository:
    def __init__(self) -> None:
        self.specialties: dict[str, Specialty] = {}

    def save(self, specialty: Specialty) -> Specialty:
        self.specialties[specialty.specialty_id] = specialty
        return specialty

    def list(self) -> list[Specialty]:
        return list(self.specialties.values())

    def get(self, specialty_id: str) -> Specialty | None:
        return self.specialties.get(specialty_id)


class FakeUserSpecialtyRepository:
    def __init__(self) -> None:
        self.assignments: dict[str, UserSpecialty] = {}

    def save(self, assignment: UserSpecialty) -> UserSpecialty:
        self.assignments[assignment.user_specialty_id] = assignment
        return assignment

    def list_by_user(self, user_id: str) -> list[UserSpecialty]:
        return [
            assignment
            for assignment in self.assignments.values()
            if assignment.user_id == user_id
        ]


class FakeProjectMembershipRepository:
    def __init__(self) -> None:
        self.memberships: dict[str, ProjectMembership] = {}

    def save(self, membership: ProjectMembership) -> ProjectMembership:
        self.memberships[membership.project_membership_id] = membership
        return membership

    def list_by_project(self, company_id: str, project_id: str) -> list[ProjectMembership]:
        return [
            membership
            for membership in self.memberships.values()
            if membership.company_id == company_id and membership.project_id == project_id
        ]

    def list_by_user(self, user_id: str) -> list[ProjectMembership]:
        return [
            membership
            for membership in self.memberships.values()
            if membership.user_id == user_id
        ]


class FakeRolePermissionRepository:
    def __init__(self) -> None:
        self.permissions: dict[str, RolePermission] = {}

    def save(self, permission: RolePermission) -> RolePermission:
        self.permissions[permission.role_permission_id] = permission
        return permission

    def list_by_role(self, role: str | UserRole) -> list[RolePermission]:
        role_value = role.value if isinstance(role, UserRole) else role
        return [
            permission
            for permission in self.permissions.values()
            if permission.role.value == role_value
        ]


class FakeAuthIdentityRepository:
    def __init__(self) -> None:
        self.identities: dict[str, AuthIdentity] = {}

    def save(self, identity: AuthIdentity) -> AuthIdentity:
        self.identities[identity.identity_id] = identity
        return identity

    def list_by_user(self, user_id: str) -> list[AuthIdentity]:
        return [
            identity
            for identity in self.identities.values()
            if identity.user_id == user_id
        ]

    def get_by_provider_subject(self, provider: str, subject: str) -> AuthIdentity | None:
        for identity in self.identities.values():
            if identity.provider.value == provider and identity.subject == subject:
                return identity
        return None


class FakeUserHistoryRepository:
    def __init__(self) -> None:
        self.events: dict[str, UserHistoryEvent] = {}

    def save(self, event: UserHistoryEvent) -> UserHistoryEvent:
        self.events[event.history_id] = event
        return event

    def list_by_user(self, user_id: str) -> list[UserHistoryEvent]:
        return [event for event in self.events.values() if event.user_id == user_id]


class FakeLicensePlanRepository:
    def __init__(self) -> None:
        self.plans: dict[str, LicensePlan] = {}

    def save(self, plan: LicensePlan) -> LicensePlan:
        self.plans[plan.plan_id] = plan
        return plan

    def list(self) -> list[LicensePlan]:
        return list(self.plans.values())

    def get(self, plan_id: str) -> LicensePlan | None:
        return self.plans.get(plan_id)


class FakeCompanyLicenseRepository:
    def __init__(self) -> None:
        self.licenses: dict[str, CompanyLicense] = {}

    def save(self, license_assignment: CompanyLicense) -> CompanyLicense:
        self.licenses[license_assignment.company_license_id] = license_assignment
        return license_assignment

    def list_by_company(self, company_id: str) -> list[CompanyLicense]:
        return [
            license_assignment
            for license_assignment in self.licenses.values()
            if license_assignment.company_id == company_id
        ]


class FakePortfolioProjectRepository:
    def __init__(self) -> None:
        self.projects: dict[str, PortfolioProject] = {}

    def save(self, project: PortfolioProject) -> PortfolioProject:
        self.projects[project.project_id] = project
        return project

    def list(self) -> list[PortfolioProject]:
        return list(self.projects.values())

    def list_by_company(self, company_id: str) -> list[PortfolioProject]:
        return [project for project in self.projects.values() if project.company_id == company_id]

    def get(self, project_id: str) -> PortfolioProject | None:
        return self.projects.get(project_id)

    def get_by_company(self, company_id: str, project_id: str) -> PortfolioProject | None:
        project = self.projects.get(project_id)
        if project is None or project.company_id != company_id:
            return None
        return project

    def exists(self, project_id: str) -> bool:
        return project_id in self.projects


class FakeCorporateCustomerRepository:
    def __init__(self) -> None:
        self.customers: dict[str, CorporateCustomer] = {}

    def save(self, customer: CorporateCustomer) -> CorporateCustomer:
        self.customers[customer.customer_id] = customer
        return customer

    def list_by_company(self, company_id: str) -> list[CorporateCustomer]:
        return [customer for customer in self.customers.values() if customer.company_id == company_id]

    def get(self, customer_id: str) -> CorporateCustomer | None:
        return self.customers.get(customer_id)


class FakeCorporateProgramRepository:
    def __init__(self) -> None:
        self.programs: dict[str, CorporateProgram] = {}

    def save(self, program: CorporateProgram) -> CorporateProgram:
        self.programs[program.program_id] = program
        return program

    def list_by_company(self, company_id: str) -> list[CorporateProgram]:
        return [program for program in self.programs.values() if program.company_id == company_id]

    def get(self, program_id: str) -> CorporateProgram | None:
        return self.programs.get(program_id)


class FakeProvisioningRequestRepository:
    def __init__(self) -> None:
        self.requests: dict[str, ProvisioningRequest] = {}

    def save(self, request: ProvisioningRequest) -> ProvisioningRequest:
        self.requests[request.request_id] = request
        return request

    def list(self) -> list[ProvisioningRequest]:
        return list(self.requests.values())

    def list_by_company(self, company_id: str) -> list[ProvisioningRequest]:
        return [request for request in self.requests.values() if request.company_id == company_id]


class FakeInformationAssetRepository:
    def __init__(self) -> None:
        self.assets: dict[str, InformationAsset] = {}
        self.versions: dict[str, InformationVersion] = {}
        self.snapshots: dict[str, InformationSnapshot] = {}
        self.backups: dict[str, InformationBackup] = {}

    def save_asset(self, asset: InformationAsset) -> InformationAsset:
        self.assets[asset.asset_id] = asset
        return asset

    def list_assets_by_company(self, company_id: str) -> list[InformationAsset]:
        return [asset for asset in self.assets.values() if asset.company_id == company_id]

    def get_asset(self, asset_id: str) -> InformationAsset | None:
        return self.assets.get(asset_id)

    def save_version(self, version: InformationVersion) -> InformationVersion:
        self.versions[version.version_id] = version
        return version

    def list_versions(self, asset_id: str) -> list[InformationVersion]:
        return [version for version in self.versions.values() if version.asset_id == asset_id]

    def save_snapshot(self, snapshot: InformationSnapshot) -> InformationSnapshot:
        self.snapshots[snapshot.snapshot_id] = snapshot
        return snapshot

    def list_snapshots_by_company(self, company_id: str) -> list[InformationSnapshot]:
        return [snapshot for snapshot in self.snapshots.values() if snapshot.company_id == company_id]

    def save_backup(self, backup: InformationBackup) -> InformationBackup:
        self.backups[backup.backup_id] = backup
        return backup

    def list_backups_by_company(self, company_id: str) -> list[InformationBackup]:
        return [backup for backup in self.backups.values() if backup.company_id == company_id]


class FakeCorporateGisRepository:
    def __init__(self) -> None:
        self.schemas: dict[str, PostgisSchema] = {}
        self.workspaces: dict[str, GeoServerWorkspace] = {}
        self.datastores: dict[str, GeoServerDatastore] = {}
        self.layers: dict[str, GeoServerLayer] = {}
        self.bindings: dict[str, ProjectGisBinding] = {}

    def save_postgis_schema(self, schema: PostgisSchema) -> PostgisSchema:
        self.schemas[schema.schema_id] = schema
        return schema

    def get_postgis_schema(self, schema_id: str) -> PostgisSchema | None:
        return self.schemas.get(schema_id)

    def list_postgis_schemas(self, company_id: str, project_id: str | None = None) -> list[PostgisSchema]:
        return [
            schema
            for schema in self.schemas.values()
            if schema.company_id == company_id and (project_id is None or schema.project_id == project_id)
        ]

    def save_workspace(self, workspace: GeoServerWorkspace) -> GeoServerWorkspace:
        self.workspaces[workspace.workspace_id] = workspace
        return workspace

    def get_workspace(self, workspace_id: str) -> GeoServerWorkspace | None:
        return self.workspaces.get(workspace_id)

    def list_workspaces(self, company_id: str, project_id: str | None = None) -> list[GeoServerWorkspace]:
        return [
            workspace
            for workspace in self.workspaces.values()
            if workspace.company_id == company_id and (project_id is None or workspace.project_id == project_id)
        ]

    def save_datastore(self, datastore: GeoServerDatastore) -> GeoServerDatastore:
        self.datastores[datastore.datastore_id] = datastore
        return datastore

    def get_datastore(self, datastore_id: str) -> GeoServerDatastore | None:
        return self.datastores.get(datastore_id)

    def list_datastores(self, company_id: str, project_id: str | None = None) -> list[GeoServerDatastore]:
        return [
            datastore
            for datastore in self.datastores.values()
            if datastore.company_id == company_id and (project_id is None or datastore.project_id == project_id)
        ]

    def save_layer(self, layer: GeoServerLayer) -> GeoServerLayer:
        self.layers[layer.layer_id] = layer
        return layer

    def list_layers(self, company_id: str, project_id: str | None = None) -> list[GeoServerLayer]:
        return [
            layer
            for layer in self.layers.values()
            if layer.company_id == company_id and (project_id is None or layer.project_id == project_id)
        ]

    def save_binding(self, binding: ProjectGisBinding) -> ProjectGisBinding:
        self.bindings[f"{binding.company_id}:{binding.project_id}"] = binding
        return binding

    def get_binding(self, company_id: str, project_id: str) -> ProjectGisBinding | None:
        return self.bindings.get(f"{company_id}:{project_id}")


class FakeCorporateGisIntelligenceRepository:
    def __init__(self) -> None:
        self.sources: dict[str, CorporateGisSource] = {}
        self.layers: dict[str, CorporateLayer] = {}

    def save_source(self, source: CorporateGisSource) -> CorporateGisSource:
        self.sources[source.source_id] = source
        return source

    def get_source(self, source_id: str) -> CorporateGisSource | None:
        return self.sources.get(source_id)

    def list_sources(self, company_id: str, project_id: str | None = None) -> list[CorporateGisSource]:
        return [
            source
            for source in self.sources.values()
            if source.company_id == company_id and (project_id is None or source.project_id == project_id)
        ]

    def save_layer(self, layer: CorporateLayer) -> CorporateLayer:
        self.layers[layer.layer_id] = layer
        return layer

    def list_layers(self, company_id: str, project_id: str | None = None) -> list[CorporateLayer]:
        return [
            layer
            for layer in self.layers.values()
            if layer.company_id == company_id and (project_id is None or layer.project_id == project_id)
        ]


class FakeCorporateWorkflowRepository:
    def __init__(self) -> None:
        self.workflows: dict[str, CorporateWorkflowInstance] = {}
        self.transitions: list[CorporateWorkflowTransition] = []

    def save_workflow(self, workflow: CorporateWorkflowInstance) -> CorporateWorkflowInstance:
        self.workflows[workflow.workflow_id] = workflow
        return workflow

    def get_workflow(self, workflow_id: str) -> CorporateWorkflowInstance | None:
        return self.workflows.get(workflow_id)

    def list_workflows(self, company_id: str) -> list[CorporateWorkflowInstance]:
        return [
            workflow
            for workflow in self.workflows.values()
            if workflow.company_id == company_id
        ]

    def save_transition(self, transition: CorporateWorkflowTransition) -> CorporateWorkflowTransition:
        self.transitions.append(transition)
        return transition

    def list_transitions(self, workflow_id: str) -> list[CorporateWorkflowTransition]:
        return [
            transition
            for transition in self.transitions
            if transition.workflow_id == workflow_id
        ]


class FakeEnterpriseWizardRepository:
    def __init__(self) -> None:
        self.sessions: dict[str, EnterpriseWizardSession] = {}

    def save(self, session: EnterpriseWizardSession) -> EnterpriseWizardSession:
        self.sessions[session.wizard_id] = session
        return session

    def get(self, wizard_id: str) -> EnterpriseWizardSession | None:
        return self.sessions.get(wizard_id)

    def list(self) -> list[EnterpriseWizardSession]:
        return list(self.sessions.values())


class FakeAuditEventRepository:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def save(self, event: AuditEvent) -> AuditEvent:
        self.events.append(event)
        return event

    def list(self, limit: int = 100) -> list[AuditEvent]:
        return self.events[-limit:]
