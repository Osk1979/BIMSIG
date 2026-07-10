"""FastAPI application factory for Corporate Control Tower REV12.

ADR references:
- ADR-0001: REV11 architecture baseline.
- ADR-0002: Layered modular API scaffold.
- ADR-0003: Project provisioning as a port.
- ADR-0005: Persistence strategy.
"""

import logging
import os
import re
import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from pydantic import BaseModel, Field

from control_tower import __version__
from control_tower.application.auth_service import EnterpriseAuthService
from control_tower.application.connection_center_service import ConnectionCenterService
from control_tower.application.corporate_gis_intelligence_service import CorporateGisIntelligenceService
from control_tower.application.corporate_workflow_service import CorporateWorkflowEngine
from control_tower.application.dashboard_service import DashboardService
from control_tower.application.deployment_target_service import DeploymentTargetService
from control_tower.application.enterprise_service import (
    CompanyService,
    CorporateUserSecurityService,
    LicensingService,
    UserService,
)
from control_tower.application.enterprise_scale_service import (
    EnterpriseScaleIsolationReport,
    EnterpriseScaleProjectPage,
    EnterpriseScaleSearchResult,
    EnterpriseScaleSeedRequest,
    EnterpriseScaleSeedResult,
    EnterpriseScaleService,
    EnterpriseScaleSummary,
)
from control_tower.application.enterprise_wizard_service import EnterpriseWizardService
from control_tower.application.gis_service import CorporateGisService
from control_tower.application.infrastructure_connectors import (
    InfrastructureConnectorAction,
    InfrastructureConnectorKind,
    InfrastructureConnectorRequest,
    InfrastructureConnectorResult,
    InfrastructureConnectorService,
)
from control_tower.application.nas_service import NasInformationCenterService
from control_tower.application.observability_service import (
    ObservabilityDashboard,
    ObservabilityHealth,
    ObservabilityMetrics,
    ObservabilityOtelExport,
    ObservabilityService,
)
from control_tower.application.operational_flow_service import OperationalFlowService
from control_tower.application.portfolio_service import CorporatePortfolioDomainService, PortfolioService
from control_tower.application.portal_gateway_service import PortalGatewayService
from control_tower.application.provisioning_service import (
    ProjectProvisioningEngine,
    ProjectProvisioningSpec,
    ProvisioningService,
)
from control_tower.application.rbac_policy import RbacPolicy, infer_permission
from control_tower.application.reporting_service import CorporateReportingService
from control_tower.domain.audit import AuditEvent
from control_tower.domain.corporate_gis_intelligence import (
    CorporateGisIntelligenceMap,
    CorporateGisLayerPanel,
    CorporateGisServiceValidation,
    CorporateGisSource,
    CorporateGisSummary,
    CorporateLayer,
    ProjectSpatialIndicator,
)
from control_tower.domain.corporate_workflow import (
    CorporateWorkflowAdvance,
    CorporateWorkflowInstance,
    CorporateWorkflowRollback,
    CorporateWorkflowTransition,
)
from control_tower.domain.connection_center import (
    ConnectionCenterHealth,
    ConnectionCenterReadiness,
    ConnectionCenterTopology,
)
from control_tower.domain.dashboard import CorporateDashboard
from control_tower.domain.deployment_targets import (
    DeploymentTarget,
    DeploymentTargetActivation,
    DeploymentTargetCatalog,
    DeploymentTargetValidation,
)
from control_tower.domain.enterprise import (
    AuthIdentity,
    AuthSession,
    AuthenticatedPrincipal,
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
from control_tower.domain.enterprise_wizard import (
    EnterpriseWizardActivation,
    EnterpriseWizardSession,
    EnterpriseWizardStep,
    EnterpriseWizardStepState,
    EnterpriseWizardStepSubmission,
)
from control_tower.domain.gis import (
    GeoServerDatastore,
    GeoServerLayer,
    GeoServerWorkspace,
    GisResourceValidation,
    PostgisSchema,
    ProjectGisBinding,
    ProjectGisResources,
)
from control_tower.domain.nas import (
    InformationAsset,
    InformationBackup,
    InformationPermission,
    InformationSnapshot,
    InformationVersion,
)
from control_tower.domain.operations import CompanyOperationalFlow
from control_tower.domain.operations import CorporateOperatingModel
from control_tower.domain.portfolio import PortfolioProject, ProjectStatus
from control_tower.domain.portfolio import (
    CorporateCustomer,
    CorporatePortfolioProjectView,
    CorporateProgram,
    PortfolioLifecycleTransition,
    ProjectLifecycleStage,
)
from control_tower.domain.portal_gateway import (
    PortalGatewayConfig,
    PortalGatewayHealth,
    PortalGatewaySnapshot,
)
from control_tower.domain.provisioning import ProvisioningRequest
from control_tower.domain.reports import (
    CorporatePrintReport,
    ReportRequest,
    ReportTemplate,
    ReportTemplateDescriptor,
)
from control_tower.infrastructure.database import (
    SqlAlchemyAuditEventRepository,
    SqlAlchemyAuthIdentityRepository,
    SqlAlchemyCompanyLicenseRepository,
    SqlAlchemyCompanyMembershipRepository,
    SqlAlchemyCorporateGisIntelligenceRepository,
    SqlAlchemyCorporateGisRepository,
    SqlAlchemyCorporateCustomerRepository,
    SqlAlchemyCorporateProgramRepository,
    SqlAlchemyCorporateWorkflowRepository,
    SqlAlchemyCompanyRepository,
    SqlAlchemyEnterpriseWizardRepository,
    SqlAlchemyInformationAssetRepository,
    SqlAlchemyLicensePlanRepository,
    SqlAlchemyPortfolioProjectRepository,
    SqlAlchemyProjectMembershipRepository,
    SqlAlchemyProvisioningRequestRepository,
    SqlAlchemyRolePermissionRepository,
    SqlAlchemySessionProvider,
    SqlAlchemySpecialtyRepository,
    SqlAlchemyUserHistoryRepository,
    SqlAlchemyUserRepository,
    SqlAlchemyUserSpecialtyRepository,
    check_database,
    create_database_engine,
    initialize_database,
)
from control_tower.infrastructure.adapters.provisioning import default_project_stack_adapters
from control_tower.infrastructure.adapters.connectors import default_infrastructure_connectors
from control_tower.presentation.dashboard_ui import render_dashboard_html


logger = logging.getLogger("control_tower.api")

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}

PORTAL_CORS_DEFAULT_ORIGINS = (
    "https://bimsig-enterprise.oscarsalas1979.chatgpt.site",
    "https://bim-digital-hub.oscarsalas1979.chatgpt.site",
    "https://websig-enterprise.oscarsalas1979.chatgpt.site",
)


def _csv_env(name: str, default: tuple[str, ...]) -> list[str]:
    """Parse comma-separated environment values while preserving sane defaults."""

    raw_value = os.getenv(name)
    if raw_value is None:
        return list(default)
    return [item.strip().rstrip("/") for item in raw_value.split(",") if item.strip()]


class ProvisionWebSigPayload(BaseModel):
    """API payload to request a dedicated WEB SIG for a project."""

    project_id: str = Field(min_length=3)


class GovernanceStatusPayload(BaseModel):
    """API payload to change project governance status."""

    status: ProjectStatus


class AssetVersionPayload(BaseModel):
    """API payload to register an information asset version."""

    version: str = Field(min_length=1)
    logical_uri: str = Field(min_length=6)
    checksum_sha256: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class AssetMetadataPayload(BaseModel):
    """API payload to merge information asset metadata."""

    metadata: dict[str, str]


class AssetPermissionPayload(BaseModel):
    """API payload to set one information asset permission."""

    principal: str = Field(min_length=3)
    permission: InformationPermission


class SnapshotPayload(BaseModel):
    """API payload to create an information snapshot."""

    name: str = Field(min_length=3)
    asset_ids: list[str] = Field(default_factory=list)
    project_id: str | None = Field(default=None, min_length=3)
    metadata: dict[str, str] = Field(default_factory=dict)


class BackupPayload(BaseModel):
    """API payload to register an information backup."""

    logical_uri: str = Field(min_length=6)
    project_id: str | None = Field(default=None, min_length=3)
    snapshot_id: str | None = Field(default=None, min_length=3)
    checksum_sha256: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class SsoAuthenticatePayload(BaseModel):
    """API payload to resolve an SSO identity."""

    provider: str = Field(min_length=3)
    subject: str = Field(min_length=3)


class AuthLoginPayload(BaseModel):
    """API payload for Enterprise login through a linked identity."""

    provider: str = Field(min_length=3)
    subject: str = Field(min_length=3)


class AuthLogoutResponse(BaseModel):
    """API response for logout."""

    status: str = "logged_out"


class StartCorporateWorkflowPayload(BaseModel):
    """API payload to start an official Corporate Workflow Engine instance."""

    workflow_id: str | None = Field(default=None, min_length=3)
    project_id: str | None = Field(default=None, min_length=3)
    program_id: str | None = Field(default=None, min_length=3)
    actor: str = Field(default="system", min_length=1)
    reason: str = Field(default="Corporate workflow started", min_length=3)


class StartEnterpriseWizardPayload(BaseModel):
    """API payload to start an Enterprise Wizard session."""

    wizard_id: str | None = Field(default=None, min_length=3)
    actor: str = Field(default="system", min_length=1)


def create_app(database_url: str | None = None, initialize_schema: bool = True) -> FastAPI:
    """Create the Corporate Control Tower API application."""

    app = FastAPI(
        title="Corporate Control Tower REV12",
        version=__version__,
        description="Portfolio governance and WEB SIG provisioning API for BIMSIG Enterprise.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_csv_env("CONTROL_TOWER_CORS_ORIGINS", PORTAL_CORS_DEFAULT_ORIGINS),
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    resolved_database_url = database_url or os.getenv(
        "CONTROL_TOWER_DATABASE_URL",
        "sqlite:///./control_tower.db",
    )
    engine = create_database_engine(resolved_database_url)
    if initialize_schema:
        initialize_database(engine)
    sessions = SqlAlchemySessionProvider(engine)
    audit_repository = SqlAlchemyAuditEventRepository(sessions)
    company_repository = SqlAlchemyCompanyRepository(sessions)
    user_repository = SqlAlchemyUserRepository(sessions)
    membership_repository = SqlAlchemyCompanyMembershipRepository(sessions)
    license_plan_repository = SqlAlchemyLicensePlanRepository(sessions)
    company_license_repository = SqlAlchemyCompanyLicenseRepository(sessions)
    information_repository = SqlAlchemyInformationAssetRepository(sessions)
    gis_repository = SqlAlchemyCorporateGisRepository(sessions)
    gis_intelligence_repository = SqlAlchemyCorporateGisIntelligenceRepository(sessions)
    workflow_repository = SqlAlchemyCorporateWorkflowRepository(sessions)
    wizard_repository = SqlAlchemyEnterpriseWizardRepository(sessions)
    customer_repository = SqlAlchemyCorporateCustomerRepository(sessions)
    program_repository = SqlAlchemyCorporateProgramRepository(sessions)
    portfolio_repository = SqlAlchemyPortfolioProjectRepository(sessions)
    provisioning_repository = SqlAlchemyProvisioningRequestRepository(sessions)
    specialty_repository = SqlAlchemySpecialtyRepository(sessions)
    user_specialty_repository = SqlAlchemyUserSpecialtyRepository(sessions)
    project_membership_repository = SqlAlchemyProjectMembershipRepository(sessions)
    role_permission_repository = SqlAlchemyRolePermissionRepository(sessions)
    auth_identity_repository = SqlAlchemyAuthIdentityRepository(sessions)
    user_history_repository = SqlAlchemyUserHistoryRepository(sessions)
    companies = CompanyService(company_repository, audit_repository)
    users = UserService(user_repository, membership_repository, companies, audit_repository)
    licensing = LicensingService(
        license_plan_repository,
        company_license_repository,
        companies,
        audit_repository,
    )
    portfolio = PortfolioService(portfolio_repository, audit_repository)
    corporate_portfolio = CorporatePortfolioDomainService(
        customer_repository,
        program_repository,
        portfolio,
        provisioning_repository,
        information_repository,
        gis_repository,
        audit_repository,
    )
    provisioning = ProvisioningService(portfolio, provisioning_repository, audit_repository)
    operational_flow = OperationalFlowService(
        companies,
        portfolio,
        corporate_portfolio,
        provisioning_repository,
        workflow_repository,
        wizard_repository,
        information_repository,
        gis_repository,
        audit_repository,
    )
    project_stack_adapters = default_project_stack_adapters(
        nas_root=os.getenv("CONTROL_TOWER_NAS_ROOT"),
        postgis_database_url=os.getenv("CONTROL_TOWER_POSTGIS_DATABASE_URL"),
        geoserver_url=os.getenv("CONTROL_TOWER_GEOSERVER_URL"),
        geoserver_user=os.getenv("CONTROL_TOWER_GEOSERVER_USER"),
        geoserver_password=os.getenv("CONTROL_TOWER_GEOSERVER_PASSWORD"),
        websig_factory_template_path=os.getenv("CONTROL_TOWER_WEBSIG_FACTORY_TEMPLATE_PATH"),
        websig_factory_output_root=os.getenv("CONTROL_TOWER_WEBSIG_FACTORY_OUTPUT_ROOT"),
    )
    infrastructure_connectors = InfrastructureConnectorService(
        default_infrastructure_connectors(
            postgis_database_url=os.getenv("CONTROL_TOWER_POSTGIS_DATABASE_URL"),
            geoserver_url=os.getenv("CONTROL_TOWER_GEOSERVER_URL"),
            geoserver_user=os.getenv("CONTROL_TOWER_GEOSERVER_USER"),
            geoserver_password=os.getenv("CONTROL_TOWER_GEOSERVER_PASSWORD"),
            nas_root=os.getenv("CONTROL_TOWER_NAS_ROOT"),
            google_drive_root_id=os.getenv("CONTROL_TOWER_GOOGLE_DRIVE_ROOT_ID"),
            google_drive_access_token=os.getenv("CONTROL_TOWER_GOOGLE_DRIVE_ACCESS_TOKEN"),
            google_credentials_file=os.getenv("CONTROL_TOWER_GOOGLE_APPLICATION_CREDENTIALS")
            or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        ),
        audit_repository,
    )
    provisioning_engine = ProjectProvisioningEngine(
        companies,
        users,
        portfolio,
        provisioning_repository,
        project_stack_adapters,
        audit_repository,
    )
    nas = NasInformationCenterService(information_repository, companies, portfolio, audit_repository)
    gis = CorporateGisService(gis_repository, companies, portfolio, audit_repository)
    gis_intelligence = CorporateGisIntelligenceService(
        gis_intelligence_repository,
        companies,
        portfolio,
        audit_repository,
    )
    workflow_engine = CorporateWorkflowEngine(
        workflow_repository,
        companies,
        portfolio,
        audit_repository,
    )
    dashboard = DashboardService(
        companies,
        users,
        licensing,
        portfolio,
        provisioning,
        corporate_portfolio,
        operational_flow,
        gis_intelligence,
    )
    enterprise_scale = EnterpriseScaleService(companies, portfolio, corporate_portfolio)
    reporting = CorporateReportingService(
        dashboard,
        audit_repository,
        nas,
        output_dir=os.getenv("CONTROL_TOWER_REPORT_OUTPUT_DIR", "output/pdf"),
    )
    portal_gateway = PortalGatewayService(
        dashboard,
        reporting,
        portal_origin=os.getenv(
            "BIMSIG_PORTAL_ORIGIN",
            "https://bimsig-enterprise.oscarsalas1979.chatgpt.site",
        ),
        tower_base_url=os.getenv(
            "BIMSIG_TOWER_URL",
            "https://bim-digital-hub.oscarsalas1979.chatgpt.site",
        ),
        websig_base_url=os.getenv(
            "BIMSIG_WEBSIG_URL",
            "https://websig-enterprise.oscarsalas1979.chatgpt.site",
        ),
        default_company_id=os.getenv("BIMSIG_DEFAULT_COMPANY_ID", "CRTG"),
    )
    connection_center = ConnectionCenterService(
        portal_gateway,
        infrastructure_connectors,
        portal_origin=os.getenv(
            "BIMSIG_PORTAL_ORIGIN",
            "https://bimsig-enterprise.oscarsalas1979.chatgpt.site",
        ),
        tower_base_url=os.getenv(
            "BIMSIG_TOWER_URL",
            "https://bim-digital-hub.oscarsalas1979.chatgpt.site",
        ),
        websig_base_url=os.getenv(
            "BIMSIG_WEBSIG_URL",
            "https://websig-enterprise.oscarsalas1979.chatgpt.site",
        ),
        default_company_id=os.getenv("BIMSIG_DEFAULT_COMPANY_ID", "CRTG"),
    )
    deployment_targets = DeploymentTargetService(
        local_backend_url=os.getenv("CONTROL_TOWER_LOCAL_API_URL", "http://127.0.0.1:8000"),
        public_backend_url=os.getenv("CONTROL_TOWER_PUBLIC_API_URL"),
        cloud_backend_url=os.getenv("CONTROL_TOWER_CLOUD_API_URL"),
        tunnel_backend_url=os.getenv("CONTROL_TOWER_TUNNEL_API_URL"),
        active_target_id=os.getenv("CONTROL_TOWER_ACTIVE_TARGET", "local-docker"),
        cors_origin=os.getenv(
            "BIMSIG_PORTAL_ORIGIN",
            "https://bimsig-enterprise.oscarsalas1979.chatgpt.site",
        ),
    )
    user_security = CorporateUserSecurityService(
        user_repository,
        companies,
        portfolio,
        specialty_repository,
        user_specialty_repository,
        project_membership_repository,
        role_permission_repository,
        auth_identity_repository,
        user_history_repository,
        audit_repository,
    )
    enterprise_wizard = EnterpriseWizardService(
        wizard_repository,
        companies,
        users,
        corporate_portfolio,
        workflow_engine,
        audit_repository,
    )
    auth_service = EnterpriseAuthService(
        user_security,
        users,
        companies,
        signing_secret=os.getenv("CONTROL_TOWER_AUTH_SECRET", "dev-only-control-tower-auth-secret"),
        audit=audit_repository,
        ttl_minutes=int(os.getenv("CONTROL_TOWER_AUTH_TTL_MINUTES", "480")),
    )
    auth_required = os.getenv("CONTROL_TOWER_AUTH_REQUIRED", "false").lower() == "true"
    rbac_policy = RbacPolicy()
    slow_request_ms = float(os.getenv("CONTROL_TOWER_SLOW_REQUEST_MS", "1000"))
    observability = ObservabilityService(
        service="corporate-control-tower",
        revision="REV12",
        slow_request_ms=slow_request_ms,
    )

    def bearer_token(request: Request) -> str | None:
        authorization = request.headers.get("Authorization", "")
        if not authorization.lower().startswith("bearer "):
            return None
        return authorization.split(" ", 1)[1].strip()

    def is_public_path(path: str) -> bool:
        public_prefixes = (
            "/api/v1/auth/login",
            "/api/v1/auth/logout",
            "/api/v1/auth/me",
            "/api/v1/auth/permissions/matrix",
            "/api/v1/auth/sso/resolve",
            "/api/v1/connection-center",
            "/api/v1/deployment-targets",
            "/api/v1/operational",
            "/api/v1/portal-gateway",
            "/health",
            "/metrics",
            "/dashboard",
            "/docs",
            "/openapi.json",
            "/redoc",
        )
        return path == "/" or any(path.startswith(prefix) for prefix in public_prefixes)

    def request_scope_ids(path: str) -> tuple[str | None, str | None]:
        company_match = re.search(r"/companies/([^/]+)", path)
        project_match = re.search(r"/projects/([^/]+)", path)
        return (
            company_match.group(1) if company_match else None,
            project_match.group(1) if project_match else None,
        )

    @app.middleware("http")
    async def devsecops_request_controls(request: Request, call_next) -> Response:
        """Add request traceability, auth context, security headers, and HTTP access logs."""

        request_id = request.headers.get("X-Request-ID", uuid4().hex)
        correlation_id = request.headers.get("X-Correlation-ID", request_id)
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        started = time.perf_counter()
        token = bearer_token(request)
        if token is not None:
            try:
                request.state.principal = auth_service.verify(token)
            except ValueError:
                if auth_required:
                    return Response(
                        content='{"detail":"Invalid authentication token"}',
                        media_type="application/json",
                        status_code=status.HTTP_401_UNAUTHORIZED,
                    )
        elif auth_required and request.method != "OPTIONS" and not is_public_path(request.url.path):
            return Response(
                content='{"detail":"Authentication required"}',
                media_type="application/json",
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            )
        principal = getattr(request.state, "principal", None)
        if auth_required and principal is not None and not is_public_path(request.url.path):
            permission_scope, permission_action = infer_permission(request.url.path, request.method)
            company_id, project_id = request_scope_ids(request.url.path)
            if not rbac_policy.is_allowed(
                principal,
                permission_scope,
                permission_action,
                company_id=company_id,
                project_id=project_id,
            ):
                audit_repository.save(
                    AuditEvent(
                        actor=principal.user_id,
                        action="auth.permission.denied",
                        entity_type="api_request",
                        entity_id=request.url.path,
                        detail=f"{request.method} denied for {permission_scope.value}:{permission_action.value}",
                    )
                )
                return Response(
                    content='{"detail":"Permission denied"}',
                    media_type="application/json",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        route = request.scope.get("route")
        metric_path = getattr(route, "path", request.url.path)
        observability.record_request(request.method, metric_path, response.status_code, duration_ms)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Response-Time-Ms"] = str(duration_ms)
        principal = getattr(request.state, "principal", None)
        actor = principal.user_id if principal is not None else "anonymous"
        if principal is not None:
            response.headers["X-Authenticated-User"] = principal.user_id
        for header, value in SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        if response.status_code >= 500 or duration_ms >= slow_request_ms:
            audit_repository.save(
                AuditEvent(
                    actor=actor,
                    action="observability.request_alert",
                    entity_type="api_request",
                    entity_id=request_id,
                    detail=f"{request.method} {metric_path} {response.status_code} in {duration_ms} ms",
                )
            )
        logger.info(
            observability.structured_log(
                request_id=request_id,
                correlation_id=correlation_id,
                method=request.method,
                path=metric_path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                actor=actor,
            )
        )
        return response

    def require_principal(request: Request) -> AuthenticatedPrincipal:
        principal = getattr(request.state, "principal", None)
        if principal is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return principal

    @app.get("/api/v1/auth/permissions/matrix")
    def permission_matrix() -> list[dict[str, str]]:
        """Return the Enterprise RBAC role matrix used by API and UI."""

        return rbac_policy.matrix()

    @app.get("/health")
    def health() -> dict[str, str]:
        """Return service health metadata."""

        return {"status": "ok", "revision": "REV12", "service": "corporate-control-tower"}

    @app.get("/api/v1/operational/health")
    def operational_health() -> dict[str, str]:
        """Return operational health including database connectivity."""

        check_database(engine)
        return {
            "status": "ok",
            "revision": "REV12",
            "service": "corporate-control-tower",
            "database": "ok",
        }

    @app.get("/api/v1/operational/readiness")
    def operational_readiness() -> dict[str, str]:
        """Return readiness checks required by CI/CD and container orchestration."""

        check_database(engine)
        return {
            "status": "ready",
            "database": "ready",
            "revision": "REV12",
        }

    @app.get("/api/v1/portal-gateway/config", response_model=PortalGatewayConfig)
    def portal_gateway_config() -> PortalGatewayConfig:
        """Return the public configuration used by the BIM-SIG enterprise portal."""

        return portal_gateway.config()

    @app.get("/api/v1/portal-gateway/health", response_model=PortalGatewayHealth)
    def portal_gateway_health() -> PortalGatewayHealth:
        """Return portal gateway readiness for browser and deployment checks."""

        return portal_gateway.health()

    @app.get(
        "/api/v1/portal-gateway/companies/{company_id}/snapshot",
        response_model=PortalGatewaySnapshot,
    )
    def portal_gateway_snapshot(company_id: str) -> PortalGatewaySnapshot:
        """Return the consolidated portal payload backed by Tower services."""

        try:
            return portal_gateway.snapshot(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get("/api/v1/connection-center/topology", response_model=ConnectionCenterTopology)
    def connection_center_topology(company_id: str | None = None) -> ConnectionCenterTopology:
        """Return the governed Portal, Tower, WEB SIG, and connector topology."""

        return connection_center.topology(company_id)

    @app.get("/api/v1/connection-center/health", response_model=ConnectionCenterHealth)
    def connection_center_health() -> ConnectionCenterHealth:
        """Return normalized health for the enterprise connection fabric."""

        return connection_center.health()

    @app.get(
        "/api/v1/connection-center/companies/{company_id}/readiness",
        response_model=ConnectionCenterReadiness,
    )
    def connection_center_readiness(company_id: str) -> ConnectionCenterReadiness:
        """Return company-scoped Connection Center readiness."""

        return connection_center.readiness(company_id)

    @app.get("/api/v1/deployment-targets", response_model=DeploymentTargetCatalog)
    def deployment_target_catalog() -> DeploymentTargetCatalog:
        """Return selectable backend deployment targets."""

        return deployment_targets.catalog()

    @app.get("/api/v1/deployment-targets/active", response_model=DeploymentTarget)
    def active_deployment_target() -> DeploymentTarget:
        """Return active backend deployment target."""

        return deployment_targets.active()

    @app.post(
        "/api/v1/deployment-targets/{target_id}/activate",
        response_model=DeploymentTarget,
    )
    def activate_deployment_target(
        target_id: str,
        payload: DeploymentTargetActivation,
    ) -> DeploymentTarget:
        """Activate one known backend target."""

        _ = payload
        try:
            return deployment_targets.activate(target_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/deployment-targets/{target_id}/validate",
        response_model=DeploymentTargetValidation,
    )
    def validate_deployment_target(target_id: str) -> DeploymentTargetValidation:
        """Validate target health endpoints."""

        try:
            return deployment_targets.validate(target_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/api/v1/infrastructure/connectors/health",
        response_model=list[InfrastructureConnectorResult],
    )
    def infrastructure_connectors_health() -> list[InfrastructureConnectorResult]:
        """Return health for PostGIS, GeoServer, NAS, and Google Drive connectors."""

        return infrastructure_connectors.health()

    @app.get(
        "/api/v1/infrastructure/connectors/{connector}/health",
        response_model=InfrastructureConnectorResult,
    )
    def infrastructure_connector_health(connector: InfrastructureConnectorKind) -> InfrastructureConnectorResult:
        """Return health for one controlled infrastructure connector."""

        return infrastructure_connectors.run(
            connector,
            InfrastructureConnectorRequest(action=InfrastructureConnectorAction.HEALTH),
        )

    @app.post(
        "/api/v1/infrastructure/connectors/{connector}/validate",
        response_model=InfrastructureConnectorResult,
    )
    def validate_infrastructure_connector(
        connector: InfrastructureConnectorKind,
        payload: InfrastructureConnectorRequest,
        request: Request,
    ) -> InfrastructureConnectorResult:
        """Validate connector credentials and configuration without side effects."""

        principal = getattr(request.state, "principal", None)
        return infrastructure_connectors.run(
            connector,
            payload.model_copy(update={"action": InfrastructureConnectorAction.VALIDATE}),
            actor=principal.user_id if principal is not None else "system",
        )

    @app.post(
        "/api/v1/infrastructure/connectors/{connector}/dry-run",
        response_model=InfrastructureConnectorResult,
    )
    def dry_run_infrastructure_connector(
        connector: InfrastructureConnectorKind,
        payload: InfrastructureConnectorRequest,
        request: Request,
    ) -> InfrastructureConnectorResult:
        """Plan a controlled infrastructure connector operation without side effects."""

        principal = getattr(request.state, "principal", None)
        return infrastructure_connectors.run(
            connector,
            payload.model_copy(update={"action": InfrastructureConnectorAction.DRY_RUN}),
            actor=principal.user_id if principal is not None else "system",
        )

    @app.post(
        "/api/v1/infrastructure/connectors/{connector}/execute",
        response_model=InfrastructureConnectorResult,
        status_code=status.HTTP_202_ACCEPTED,
    )
    def execute_infrastructure_connector(
        connector: InfrastructureConnectorKind,
        payload: InfrastructureConnectorRequest,
        request: Request,
    ) -> InfrastructureConnectorResult:
        """Execute a controlled infrastructure connector operation after approval."""

        principal = getattr(request.state, "principal", None)
        result = infrastructure_connectors.run(
            connector,
            payload.model_copy(update={"action": InfrastructureConnectorAction.EXECUTE}),
            actor=principal.user_id if principal is not None else "system",
        )
        if result.status.value in {"failed", "misconfigured"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.model_dump(mode="json"))
        return result

    @app.get("/api/v1/operational/version")
    def operational_version() -> dict[str, str]:
        """Return deployable version metadata."""

        return {
            "service": "corporate-control-tower",
            "version": __version__,
            "revision": "REV12",
        }

    def observability_database_status() -> str:
        try:
            check_database(engine)
        except Exception:
            logger.exception("observability_database_check_failed")
            return "error"
        return "ok"

    @app.get("/api/v1/observability/metrics", response_model=ObservabilityMetrics)
    def observability_metrics() -> ObservabilityMetrics:
        """Return in-process API metrics for production operations."""

        return observability.metrics()

    @app.get("/metrics", response_class=PlainTextResponse)
    def prometheus_metrics() -> PlainTextResponse:
        """Return Prometheus text metrics without requiring an external service."""

        return PlainTextResponse(observability.prometheus(), media_type="text/plain; version=0.0.4")

    @app.get("/api/v1/observability/connectors", response_model=list[InfrastructureConnectorResult])
    def observability_connectors() -> list[InfrastructureConnectorResult]:
        """Return connector status for the observability dashboard."""

        return infrastructure_connectors.health()

    @app.get("/api/v1/observability/health/deep", response_model=ObservabilityHealth)
    def observability_deep_health() -> ObservabilityHealth:
        """Return deep health for database and governed infrastructure connectors."""

        return observability.health(
            observability_database_status(),
            infrastructure_connectors.health(),
        )

    @app.get("/api/v1/observability/dashboard", response_model=ObservabilityDashboard)
    def observability_dashboard(request: Request) -> ObservabilityDashboard:
        """Return the operational observability dashboard payload."""

        return observability.dashboard(
            observability_database_status(),
            infrastructure_connectors.health(),
            correlation_id=getattr(request.state, "correlation_id", None),
        )

    @app.get("/api/v1/observability/otel", response_model=ObservabilityOtelExport)
    def observability_otel_export() -> ObservabilityOtelExport:
        """Return an OpenTelemetry-ready export payload for future collectors."""

        return observability.otel_export(infrastructure_connectors.health())

    @app.post(
        "/api/v1/enterprise-scale/seed",
        response_model=EnterpriseScaleSeedResult,
        status_code=status.HTTP_201_CREATED,
    )
    def seed_enterprise_scale_dataset(payload: EnterpriseScaleSeedRequest) -> EnterpriseScaleSeedResult:
        """Create a deterministic Enterprise demo dataset for scale validation."""

        return enterprise_scale.seed(payload)

    @app.get("/api/v1/enterprise-scale/projects", response_model=EnterpriseScaleProjectPage)
    def enterprise_scale_projects(
        page: int = 1,
        page_size: int = 50,
        company_id: str | None = None,
        program_id: str | None = None,
        customer_id: str | None = None,
        project_status: ProjectStatus | None = None,
        lifecycle_stage: ProjectLifecycleStage | None = None,
        region: str | None = None,
        query: str | None = None,
    ) -> EnterpriseScaleProjectPage:
        """Return paginated, filtered projects for Enterprise-scale portfolios."""

        return enterprise_scale.project_page(
            page=page,
            page_size=page_size,
            company_id=company_id,
            program_id=program_id,
            customer_id=customer_id,
            status=project_status,
            lifecycle_stage=lifecycle_stage,
            region=region,
            query=query,
        )

    @app.get("/api/v1/enterprise-scale/search", response_model=EnterpriseScaleSearchResult)
    def enterprise_scale_search(query: str, limit: int = 25) -> EnterpriseScaleSearchResult:
        """Search companies, programs, and projects across the governed portfolio."""

        return enterprise_scale.search(query, limit=limit)

    @app.get("/api/v1/enterprise-scale/summary", response_model=EnterpriseScaleSummary)
    def enterprise_scale_summary() -> EnterpriseScaleSummary:
        """Return Enterprise-scale aggregate metrics."""

        return enterprise_scale.summary()

    @app.get("/api/v1/enterprise-scale/isolation", response_model=EnterpriseScaleIsolationReport)
    def enterprise_scale_isolation() -> EnterpriseScaleIsolationReport:
        """Validate multi-company project, program, and customer isolation."""

        return enterprise_scale.validate_isolation()

    @app.get("/api/v1/companies/{company_id}/operations/flow", response_model=CompanyOperationalFlow)
    def company_operational_flow(company_id: str) -> CompanyOperationalFlow:
        """Return the governed operational flow for one company."""

        try:
            return operational_flow.company_flow(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get("/api/v1/companies/{company_id}/operations/model", response_model=CorporateOperatingModel)
    def company_operating_model(company_id: str) -> CorporateOperatingModel:
        """Return the Corporate Operating Model for Fase 3 operations."""

        try:
            return operational_flow.company_operating_model(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/workflows/corporate/start",
        response_model=CorporateWorkflowInstance,
        status_code=status.HTTP_201_CREATED,
    )
    def start_corporate_workflow(
        company_id: str,
        payload: StartCorporateWorkflowPayload,
    ) -> CorporateWorkflowInstance:
        """Start the official auditable corporate workflow."""

        try:
            return workflow_engine.start_workflow(
                company_id,
                workflow_id=payload.workflow_id,
                project_id=payload.project_id,
                program_id=payload.program_id,
                actor=payload.actor,
                reason=payload.reason,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/workflows/corporate",
        response_model=list[CorporateWorkflowInstance],
    )
    def list_corporate_workflows(company_id: str) -> list[CorporateWorkflowInstance]:
        """List company-scoped Corporate Workflow Engine instances."""

        try:
            return workflow_engine.list_workflows(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/workflows/corporate/{workflow_id}",
        response_model=CorporateWorkflowInstance,
    )
    def get_corporate_workflow(company_id: str, workflow_id: str) -> CorporateWorkflowInstance:
        """Return one Corporate Workflow Engine instance."""

        try:
            return workflow_engine.get_workflow(company_id, workflow_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/workflows/corporate/{workflow_id}/advance",
        response_model=CorporateWorkflowInstance,
    )
    def advance_corporate_workflow(
        company_id: str,
        workflow_id: str,
        payload: CorporateWorkflowAdvance,
    ) -> CorporateWorkflowInstance:
        """Advance one Corporate Workflow Engine instance one official stage."""

        try:
            return workflow_engine.advance(company_id, workflow_id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/workflows/corporate/{workflow_id}/rollback",
        response_model=CorporateWorkflowInstance,
    )
    def rollback_corporate_workflow(
        company_id: str,
        workflow_id: str,
        payload: CorporateWorkflowRollback,
    ) -> CorporateWorkflowInstance:
        """Rollback one Corporate Workflow Engine instance to the prior stage."""

        try:
            return workflow_engine.rollback(company_id, workflow_id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/workflows/corporate/{workflow_id}/transitions",
        response_model=list[CorporateWorkflowTransition],
    )
    def list_corporate_workflow_transitions(
        company_id: str,
        workflow_id: str,
    ) -> list[CorporateWorkflowTransition]:
        """List auditable transitions for one Corporate Workflow Engine instance."""

        try:
            return workflow_engine.list_transitions(company_id, workflow_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/enterprise-wizard",
        response_model=EnterpriseWizardSession,
        status_code=status.HTTP_201_CREATED,
    )
    def start_enterprise_wizard(payload: StartEnterpriseWizardPayload) -> EnterpriseWizardSession:
        """Start a resumable Enterprise Wizard session."""

        return enterprise_wizard.start(wizard_id=payload.wizard_id, actor=payload.actor)

    @app.get("/api/v1/enterprise-wizard", response_model=list[EnterpriseWizardSession])
    def list_enterprise_wizard_sessions() -> list[EnterpriseWizardSession]:
        """List Enterprise Wizard sessions."""

        return enterprise_wizard.list_sessions()

    @app.get("/api/v1/enterprise-wizard/{wizard_id}", response_model=EnterpriseWizardSession)
    def get_enterprise_wizard(wizard_id: str) -> EnterpriseWizardSession:
        """Resume one Enterprise Wizard session."""

        try:
            return enterprise_wizard.get(wizard_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/enterprise-wizard/{wizard_id}/steps/{step}/validate",
        response_model=EnterpriseWizardStepState,
    )
    def validate_enterprise_wizard_step(
        wizard_id: str,
        step: EnterpriseWizardStep,
        payload: EnterpriseWizardStepSubmission,
    ) -> EnterpriseWizardStepState:
        """Validate one Enterprise Wizard step without saving it."""

        try:
            enterprise_wizard.get(wizard_id)
            return enterprise_wizard.validate_step(step, payload.data)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.put(
        "/api/v1/enterprise-wizard/{wizard_id}/steps/{step}",
        response_model=EnterpriseWizardSession,
    )
    def save_enterprise_wizard_step(
        wizard_id: str,
        step: EnterpriseWizardStep,
        payload: EnterpriseWizardStepSubmission,
    ) -> EnterpriseWizardSession:
        """Save one Enterprise Wizard step and persist partial progress."""

        try:
            return enterprise_wizard.save_step(wizard_id, step, payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/enterprise-wizard/{wizard_id}/activate",
        response_model=EnterpriseWizardSession,
    )
    def activate_enterprise_wizard(
        wizard_id: str,
        payload: EnterpriseWizardActivation,
    ) -> EnterpriseWizardSession:
        """Activate a ready Enterprise Wizard session into governed records."""

        try:
            return enterprise_wizard.activate(wizard_id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/gis-intelligence/sources",
        response_model=list[CorporateGisSource],
    )
    def list_corporate_gis_sources(company_id: str) -> list[CorporateGisSource]:
        """List WEB SIG GIS sources consolidated by Corporate GIS Intelligence."""

        try:
            return gis_intelligence.list_sources(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/gis-intelligence/sources",
        response_model=CorporateGisSource,
        status_code=status.HTTP_201_CREATED,
    )
    def register_corporate_gis_source(
        company_id: str,
        source: CorporateGisSource,
    ) -> CorporateGisSource:
        """Register one published project WEB SIG GIS source."""

        if source.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GIS source company_id must match path company_id",
            )
        try:
            return gis_intelligence.register_source(source)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/gis-intelligence/real-services",
        response_model=CorporateGisSource,
        status_code=status.HTTP_201_CREATED,
    )
    def register_real_corporate_gis_service(
        company_id: str,
        source: CorporateGisSource,
        validate: bool = True,
    ) -> CorporateGisSource:
        """Register and optionally validate one real GIS service published by WEB SIG."""

        if source.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GIS source company_id must match path company_id",
            )
        try:
            return gis_intelligence.register_real_service(source, validate=validate)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/gis-intelligence/sources/{source_id}/validate",
        response_model=CorporateGisServiceValidation,
    )
    def validate_corporate_gis_source(company_id: str, source_id: str) -> CorporateGisServiceValidation:
        """Validate one published WMS, WFS, WMTS, or Vector Tiles source."""

        try:
            source = next(
                item for item in gis_intelligence.list_sources(company_id) if item.source_id == source_id
            )
        except StopIteration as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GIS source not found") from exc
        return gis_intelligence.validate_source(source)

    @app.post(
        "/api/v1/companies/{company_id}/gis-intelligence/sources/validate",
        response_model=list[CorporateGisServiceValidation],
    )
    def validate_corporate_gis_sources(
        company_id: str,
        project_id: str | None = None,
    ) -> list[CorporateGisServiceValidation]:
        """Validate published GIS services for a company or project."""

        try:
            return gis_intelligence.validate_sources(company_id, project_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/projects/{project_id}/gis-intelligence/sources",
        response_model=list[CorporateGisSource],
    )
    def list_project_corporate_gis_sources(
        company_id: str,
        project_id: str,
    ) -> list[CorporateGisSource]:
        """List WEB SIG GIS sources for one project."""

        try:
            return gis_intelligence.list_sources(company_id, project_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/gis-intelligence/layers",
        response_model=list[CorporateLayer],
    )
    def list_corporate_layers(company_id: str) -> list[CorporateLayer]:
        """List corporate GIS intelligence layers for one company."""

        try:
            return gis_intelligence.list_layers(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/gis-intelligence/layer-panel",
        response_model=CorporateGisLayerPanel,
    )
    def corporate_gis_layer_panel(
        company_id: str,
        project_id: str | None = None,
        discipline: str | None = None,
        estado: str | None = None,
        riesgo: str | None = None,
    ) -> CorporateGisLayerPanel:
        """Return read-only layer panel, legend, availability, and filters."""

        try:
            return gis_intelligence.layer_panel(
                company_id,
                project_id,
                discipline=discipline,
                estado=estado,
                riesgo=riesgo,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/gis-intelligence/layers",
        response_model=CorporateLayer,
        status_code=status.HTTP_201_CREATED,
    )
    def register_corporate_layer(company_id: str, layer: CorporateLayer) -> CorporateLayer:
        """Register one corporate GIS intelligence layer."""

        if layer.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Corporate layer company_id must match path company_id",
            )
        try:
            return gis_intelligence.register_layer(layer)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/projects/{project_id}/gis-intelligence/layers/status",
        response_model=list[CorporateLayer],
    )
    def project_corporate_layer_status(company_id: str, project_id: str) -> list[CorporateLayer]:
        """Return corporate layer status for one project."""

        try:
            return gis_intelligence.layer_status(company_id, project_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/gis-intelligence/maps/corporate",
        response_model=CorporateGisIntelligenceMap,
    )
    def corporate_gis_intelligence_map(company_id: str) -> CorporateGisIntelligenceMap:
        """Return corporate spatial map references for one company."""

        try:
            return gis_intelligence.corporate_map(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/gis-intelligence/maps/company",
        response_model=CorporateGisIntelligenceMap,
    )
    def company_gis_intelligence_map(company_id: str) -> CorporateGisIntelligenceMap:
        """Return company-scoped corporate GIS map."""

        try:
            return gis_intelligence.company_map(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/gis-intelligence/maps/regional/{region}",
        response_model=CorporateGisIntelligenceMap,
    )
    def regional_gis_intelligence_map(company_id: str, region: str) -> CorporateGisIntelligenceMap:
        """Return regional corporate GIS map."""

        try:
            return gis_intelligence.regional_map(company_id, region)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/programs/{program_id}/gis-intelligence/maps",
        response_model=CorporateGisIntelligenceMap,
    )
    def program_gis_intelligence_map(company_id: str, program_id: str) -> CorporateGisIntelligenceMap:
        """Return program-scoped corporate GIS map."""

        try:
            return gis_intelligence.program_map(company_id, program_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/projects/{project_id}/gis-intelligence/maps",
        response_model=CorporateGisIntelligenceMap,
    )
    def project_gis_intelligence_map(company_id: str, project_id: str) -> CorporateGisIntelligenceMap:
        """Return project-scoped corporate GIS map."""

        try:
            return gis_intelligence.project_map(company_id, project_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/gis-intelligence/maps/thematic/{theme}",
        response_model=CorporateGisIntelligenceMap,
    )
    def thematic_gis_intelligence_map(company_id: str, theme: str) -> CorporateGisIntelligenceMap:
        """Return thematic corporate GIS map."""

        try:
            return gis_intelligence.thematic_map(company_id, theme)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/gis-intelligence/maps/filter",
        response_model=CorporateGisIntelligenceMap,
    )
    def filtered_gis_intelligence_map(
        company_id: str,
        estado: str | None = None,
        riesgo: str | None = None,
        calidad: str | None = None,
        ssoma: str | None = None,
        ambiental: str | None = None,
        produccion: str | None = None,
        cronograma: str | None = None,
        predios: str | None = None,
        interferencias: str | None = None,
    ) -> CorporateGisIntelligenceMap:
        """Return corporate GIS map filtered by business dimensions."""

        try:
            return gis_intelligence.filtered_map(
                company_id,
                estado=estado,
                riesgo=riesgo,
                calidad=calidad,
                ssoma=ssoma,
                ambiental=ambiental,
                produccion=produccion,
                cronograma=cronograma,
                predios=predios,
                interferencias=interferencias,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/gis-intelligence/projects/filter",
        response_model=list[ProjectSpatialIndicator],
    )
    def filter_projects_by_spatial_indicator(
        company_id: str,
        indicator: str,
        minimum_value: float = 0,
        risk_level: str | None = None,
    ) -> list[ProjectSpatialIndicator]:
        """Filter projects by corporate spatial indicator."""

        try:
            return gis_intelligence.filter_projects_by_indicator(
                company_id,
                indicator,
                minimum_value,
                risk_level,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/gis-intelligence/summary",
        response_model=CorporateGisSummary,
    )
    def corporate_gis_intelligence_summary(company_id: str) -> CorporateGisSummary:
        """Return portfolio-level spatial intelligence summary."""

        try:
            return gis_intelligence.summary(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get("/api/v1/portfolio/summary")
    def portfolio_summary() -> dict[str, int]:
        """Return portfolio status counts."""

        return portfolio.summary()

    @app.get("/api/v1/companies/{company_id}/portfolio/summary")
    def company_portfolio_summary(company_id: str) -> dict[str, int]:
        """Return portfolio status counts for one company."""

        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return portfolio.summary_for_company(company_id)

    @app.get("/dashboard", response_class=HTMLResponse)
    def dashboard_ui() -> HTMLResponse:
        """Return the integrated corporate executive dashboard UI."""

        return HTMLResponse(render_dashboard_html())

    @app.get("/api/v1/companies/{company_id}/dashboard/executive", response_model=CorporateDashboard)
    def executive_dashboard(company_id: str) -> CorporateDashboard:
        """Return the company-scoped executive dashboard read model."""

        try:
            return dashboard.executive_dashboard(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get("/api/v1/reports/templates", response_model=list[ReportTemplate])
    def report_templates() -> list[ReportTemplate]:
        """List official Corporate Control Tower report templates."""

        return list(ReportTemplate)

    @app.get(
        "/api/v1/reports/template-catalog",
        response_model=list[ReportTemplateDescriptor],
    )
    def report_template_catalog() -> list[ReportTemplateDescriptor]:
        """List report templates with governed scope, sources, and output formats."""

        return reporting.list_templates()

    @app.post("/api/v1/reports/preview", response_model=CorporatePrintReport)
    def preview_report(payload: ReportRequest) -> CorporatePrintReport:
        """Prepare a print-ready corporate report without recording emission."""

        try:
            return reporting.preview(payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post("/api/v1/reports/issue", response_model=CorporatePrintReport)
    def issue_report(payload: ReportRequest) -> CorporatePrintReport:
        """Issue an auditable corporate report manifest and print document."""

        try:
            return reporting.issue(payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post("/api/v1/reports/issue/html", response_class=HTMLResponse)
    def issue_report_html(payload: ReportRequest) -> HTMLResponse:
        """Issue a corporate report and return the print-ready HTML document."""

        try:
            report = reporting.issue(payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return HTMLResponse(report.html)

    @app.get("/api/v1/reports/{report_id}/html", response_class=HTMLResponse)
    def printable_report_html(report_id: str) -> HTMLResponse:
        """Return print-ready HTML for a report issued in this process."""

        try:
            return HTMLResponse(reporting.printable_html(report_id))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post("/api/v1/reports/issue/pdf", response_model=CorporatePrintReport)
    def issue_report_pdf(payload: ReportRequest) -> CorporatePrintReport:
        """Issue a corporate PDF report and register its NAS reference."""

        try:
            return reporting.export_pdf(payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post("/api/v1/reports/issue/pdf/download", response_class=FileResponse)
    def download_report_pdf(payload: ReportRequest) -> FileResponse:
        """Issue a corporate PDF report and return the generated PDF file."""

        try:
            report = reporting.export_pdf(payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        if report.pdf_path is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="PDF file was not generated")
        return FileResponse(
            report.pdf_path,
            media_type="application/pdf",
            filename=f"{report.manifest.report_id}.pdf",
        )

    @app.get("/api/v1/companies", response_model=list[Company])
    def list_companies() -> list[Company]:
        """List enterprise companies."""

        return companies.list_companies()

    @app.post("/api/v1/companies", response_model=Company, status_code=status.HTTP_201_CREATED)
    def register_company(company: Company) -> Company:
        """Register an enterprise company."""

        return companies.register(company)

    @app.get("/api/v1/companies/{company_id}", response_model=Company)
    def get_company(company_id: str) -> Company:
        """Return one enterprise company."""

        company = companies.get_company(company_id)
        if company is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return company

    @app.get("/api/v1/users", response_model=list[User])
    def list_users() -> list[User]:
        """List platform users."""

        return users.list_users()

    @app.post("/api/v1/users", response_model=User, status_code=status.HTTP_201_CREATED)
    def register_user(user: User) -> User:
        """Register a platform user."""

        return users.register_user(user)

    @app.get("/api/v1/companies/{company_id}/memberships", response_model=list[CompanyMembership])
    def list_company_memberships(company_id: str) -> list[CompanyMembership]:
        """List memberships for a company."""

        try:
            return users.list_memberships(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/memberships",
        response_model=CompanyMembership,
        status_code=status.HTTP_201_CREATED,
    )
    def add_company_membership(
        company_id: str,
        membership: CompanyMembership,
    ) -> CompanyMembership:
        """Assign a user role inside a company."""

        if membership.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Membership company_id must match path company_id",
            )
        try:
            return users.add_membership(membership)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get("/api/v1/specialties", response_model=list[Specialty])
    def list_specialties() -> list[Specialty]:
        """List enterprise user specialties."""

        return user_security.list_specialties()

    @app.post("/api/v1/specialties", response_model=Specialty, status_code=status.HTTP_201_CREATED)
    def create_specialty(specialty: Specialty) -> Specialty:
        """Create an enterprise user specialty."""

        return user_security.create_specialty(specialty)

    @app.get("/api/v1/users/{user_id}/specialties", response_model=list[UserSpecialty])
    def list_user_specialties(user_id: str) -> list[UserSpecialty]:
        """List specialties assigned to one user."""

        try:
            return user_security.list_user_specialties(user_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/users/{user_id}/specialties",
        response_model=UserSpecialty,
        status_code=status.HTTP_201_CREATED,
    )
    def assign_user_specialty(user_id: str, assignment: UserSpecialty) -> UserSpecialty:
        """Assign a specialty to one user."""

        if assignment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specialty assignment user_id must match path user_id",
            )
        try:
            return user_security.assign_specialty(assignment)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/projects/{project_id}/memberships",
        response_model=list[ProjectMembership],
    )
    def list_project_memberships(company_id: str, project_id: str) -> list[ProjectMembership]:
        """List user memberships scoped to one project."""

        try:
            return user_security.list_project_memberships(company_id, project_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/projects/{project_id}/memberships",
        response_model=ProjectMembership,
        status_code=status.HTTP_201_CREATED,
    )
    def assign_project_membership(
        company_id: str,
        project_id: str,
        membership: ProjectMembership,
    ) -> ProjectMembership:
        """Assign a user role inside a project."""

        if membership.company_id != company_id or membership.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project membership scope must match path company_id and project_id",
            )
        try:
            return user_security.assign_project_membership(membership)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get("/api/v1/roles/{role}/permissions", response_model=list[RolePermission])
    def list_role_permissions(role: UserRole) -> list[RolePermission]:
        """List permissions granted to one enterprise role."""

        return user_security.list_role_permissions(role)

    @app.post(
        "/api/v1/roles/{role}/permissions",
        response_model=RolePermission,
        status_code=status.HTTP_201_CREATED,
    )
    def grant_role_permission(role: UserRole, permission: RolePermission) -> RolePermission:
        """Grant a permission to one enterprise role."""

        if permission.role != role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role permission role must match path role",
            )
        return user_security.grant_role_permission(permission)

    @app.get("/api/v1/users/{user_id}/auth-identities", response_model=list[AuthIdentity])
    def list_auth_identities(user_id: str) -> list[AuthIdentity]:
        """List authentication identities linked to one user."""

        try:
            return user_security.list_auth_identities(user_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/users/{user_id}/auth-identities",
        response_model=AuthIdentity,
        status_code=status.HTTP_201_CREATED,
    )
    def register_auth_identity(user_id: str, identity: AuthIdentity) -> AuthIdentity:
        """Link an authentication identity to one user."""

        if identity.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Auth identity user_id must match path user_id",
            )
        try:
            return user_security.register_auth_identity(identity)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.post("/api/v1/auth/sso/resolve", response_model=AuthIdentity)
    def resolve_sso_identity(payload: SsoAuthenticatePayload) -> AuthIdentity:
        """Resolve an SSO identity into a registered platform user."""

        try:
            return user_security.authenticate_sso(payload.provider, payload.subject)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SSO identity not found") from exc

    @app.post("/api/v1/auth/login", response_model=AuthSession)
    def login(payload: AuthLoginPayload) -> AuthSession:
        """Issue an Enterprise bearer session for a linked local/OIDC/SAML identity."""

        try:
            return auth_service.login(payload.provider, payload.subject)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    @app.get("/api/v1/auth/me", response_model=AuthenticatedPrincipal)
    def current_identity(request: Request) -> AuthenticatedPrincipal:
        """Return the authenticated Enterprise principal."""

        return require_principal(request)

    @app.post("/api/v1/auth/logout", response_model=AuthLogoutResponse)
    def logout(request: Request) -> AuthLogoutResponse:
        """Revoke the current Enterprise bearer session."""

        token = bearer_token(request)
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        try:
            auth_service.logout(token)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        return AuthLogoutResponse()

    @app.get("/api/v1/users/{user_id}/history", response_model=list[UserHistoryEvent])
    def list_user_history(user_id: str) -> list[UserHistoryEvent]:
        """List security-relevant user history events."""

        try:
            return user_security.list_user_history(user_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get("/api/v1/license-plans", response_model=list[LicensePlan])
    def list_license_plans() -> list[LicensePlan]:
        """List enterprise license plans."""

        return licensing.list_plans()

    @app.post("/api/v1/license-plans", response_model=LicensePlan, status_code=status.HTTP_201_CREATED)
    def create_license_plan(plan: LicensePlan) -> LicensePlan:
        """Create an enterprise license plan."""

        return licensing.create_plan(plan)

    @app.get("/api/v1/companies/{company_id}/licenses", response_model=list[CompanyLicense])
    def list_company_licenses(company_id: str) -> list[CompanyLicense]:
        """List licenses assigned to a company."""

        try:
            return licensing.list_company_licenses(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get("/api/v1/companies/{company_id}/nas/assets", response_model=list[InformationAsset])
    def list_information_assets(company_id: str) -> list[InformationAsset]:
        """List Corporate Information Center assets for one company."""

        try:
            return nas.list_assets(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/nas/assets",
        response_model=InformationAsset,
        status_code=status.HTTP_201_CREATED,
    )
    def register_information_asset(company_id: str, asset: InformationAsset) -> InformationAsset:
        """Register a Corporate Information Center asset."""

        if asset.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Asset company_id must match path company_id",
            )
        try:
            return nas.register_asset(asset)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get("/api/v1/nas/assets/{asset_id}", response_model=InformationAsset)
    def get_information_asset(asset_id: str) -> InformationAsset:
        """Return one Corporate Information Center asset."""

        asset = nas.get_asset(asset_id)
        if asset is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Information asset not found")
        return asset

    @app.post("/api/v1/nas/assets/{asset_id}/versions", response_model=InformationVersion)
    def register_information_version(asset_id: str, payload: AssetVersionPayload) -> InformationVersion:
        """Register an immutable version for an information asset."""

        try:
            return nas.register_version(
                asset_id=asset_id,
                version=payload.version,
                logical_uri=payload.logical_uri,
                checksum_sha256=payload.checksum_sha256,
                metadata=payload.metadata,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get("/api/v1/nas/assets/{asset_id}/versions", response_model=list[InformationVersion])
    def list_information_versions(asset_id: str) -> list[InformationVersion]:
        """List versions for an information asset."""

        try:
            return nas.list_versions(asset_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.patch("/api/v1/nas/assets/{asset_id}/metadata", response_model=InformationAsset)
    def update_information_metadata(asset_id: str, payload: AssetMetadataPayload) -> InformationAsset:
        """Merge metadata into an information asset."""

        try:
            return nas.update_metadata(asset_id, payload.metadata)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.patch("/api/v1/nas/assets/{asset_id}/permissions", response_model=InformationAsset)
    def set_information_permission(asset_id: str, payload: AssetPermissionPayload) -> InformationAsset:
        """Set a permission on an information asset."""

        try:
            return nas.set_permission(asset_id, payload.principal, payload.permission)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.patch("/api/v1/nas/assets/{asset_id}/archive", response_model=InformationAsset)
    def archive_information_asset(asset_id: str) -> InformationAsset:
        """Archive an information asset registry entry."""

        try:
            return nas.archive_asset(asset_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get("/api/v1/companies/{company_id}/nas/snapshots", response_model=list[InformationSnapshot])
    def list_information_snapshots(company_id: str) -> list[InformationSnapshot]:
        """List information snapshots for one company."""

        try:
            return nas.list_snapshots(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post("/api/v1/companies/{company_id}/nas/snapshots", response_model=InformationSnapshot)
    def create_information_snapshot(company_id: str, payload: SnapshotPayload) -> InformationSnapshot:
        """Create an information snapshot manifest."""

        try:
            return nas.create_snapshot(
                company_id=company_id,
                name=payload.name,
                asset_ids=payload.asset_ids,
                project_id=payload.project_id,
                metadata=payload.metadata,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get("/api/v1/companies/{company_id}/nas/backups", response_model=list[InformationBackup])
    def list_information_backups(company_id: str) -> list[InformationBackup]:
        """List information backup manifests for one company."""

        try:
            return nas.list_backups(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post("/api/v1/companies/{company_id}/nas/backups", response_model=InformationBackup)
    def register_information_backup(company_id: str, payload: BackupPayload) -> InformationBackup:
        """Register an information backup manifest."""

        try:
            return nas.register_backup(
                company_id=company_id,
                logical_uri=payload.logical_uri,
                project_id=payload.project_id,
                snapshot_id=payload.snapshot_id,
                checksum_sha256=payload.checksum_sha256,
                metadata=payload.metadata,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get("/api/v1/companies/{company_id}/gis/postgis-schemas", response_model=list[PostgisSchema])
    def list_postgis_schemas(company_id: str) -> list[PostgisSchema]:
        """List corporate PostGIS schema references for one company."""

        try:
            return gis.list_postgis_schemas(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/gis/postgis-schemas",
        response_model=PostgisSchema,
        status_code=status.HTTP_201_CREATED,
    )
    def register_postgis_schema(company_id: str, schema: PostgisSchema) -> PostgisSchema:
        """Register a corporate PostGIS schema reference."""

        if schema.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PostGIS schema company_id must match path company_id",
            )
        try:
            return gis.register_postgis_schema(schema)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get("/api/v1/companies/{company_id}/gis/geoserver/workspaces", response_model=list[GeoServerWorkspace])
    def list_geoserver_workspaces(company_id: str) -> list[GeoServerWorkspace]:
        """List corporate GeoServer workspace references for one company."""

        try:
            return gis.list_workspaces(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/gis/geoserver/workspaces",
        response_model=GeoServerWorkspace,
        status_code=status.HTTP_201_CREATED,
    )
    def register_geoserver_workspace(company_id: str, workspace: GeoServerWorkspace) -> GeoServerWorkspace:
        """Register a corporate GeoServer workspace reference."""

        if workspace.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GeoServer workspace company_id must match path company_id",
            )
        try:
            return gis.register_workspace(workspace)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get("/api/v1/companies/{company_id}/gis/geoserver/datastores", response_model=list[GeoServerDatastore])
    def list_geoserver_datastores(company_id: str) -> list[GeoServerDatastore]:
        """List corporate GeoServer datastore references for one company."""

        try:
            return gis.list_datastores(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/gis/geoserver/datastores",
        response_model=GeoServerDatastore,
        status_code=status.HTTP_201_CREATED,
    )
    def register_geoserver_datastore(company_id: str, datastore: GeoServerDatastore) -> GeoServerDatastore:
        """Register a corporate GeoServer datastore reference."""

        if datastore.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GeoServer datastore company_id must match path company_id",
            )
        try:
            return gis.register_datastore(datastore)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get("/api/v1/companies/{company_id}/gis/geoserver/layers", response_model=list[GeoServerLayer])
    def list_geoserver_layers(company_id: str) -> list[GeoServerLayer]:
        """List corporate GeoServer layer references for one company."""

        try:
            return gis.list_layers(company_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/gis/geoserver/layers",
        response_model=GeoServerLayer,
        status_code=status.HTTP_201_CREATED,
    )
    def register_geoserver_layer(company_id: str, layer: GeoServerLayer) -> GeoServerLayer:
        """Register a corporate GeoServer layer reference."""

        if layer.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GeoServer layer company_id must match path company_id",
            )
        try:
            return gis.register_layer(layer)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/projects/{project_id}/gis/resources",
        response_model=ProjectGisResources,
    )
    def project_gis_resources(company_id: str, project_id: str) -> ProjectGisResources:
        """Return corporate GIS resources scoped to one project."""

        try:
            return gis.project_resources(company_id, project_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/projects/{project_id}/gis/binding",
        response_model=ProjectGisBinding,
        status_code=status.HTTP_201_CREATED,
    )
    def bind_project_gis_resources(
        company_id: str,
        project_id: str,
        binding: ProjectGisBinding,
    ) -> ProjectGisBinding:
        """Bind one project to corporate PostGIS and GeoServer references."""

        if binding.company_id != company_id or binding.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GIS binding scope must match path company_id and project_id",
            )
        try:
            return gis.bind_project_resources(binding)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/projects/{project_id}/gis/validate",
        response_model=list[GisResourceValidation],
    )
    def validate_project_gis_resources(company_id: str, project_id: str) -> list[GisResourceValidation]:
        """Validate corporate GIS registry consistency for one project."""

        try:
            return gis.validate_project_resources(company_id, project_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/projects/{project_id}/gis/mark-validated",
        response_model=ProjectGisResources,
    )
    def mark_project_gis_resources_validated(company_id: str, project_id: str) -> ProjectGisResources:
        """Mark corporate GIS resources validated after passing basic checks."""

        try:
            return gis.mark_validated(company_id, project_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/licenses",
        response_model=CompanyLicense,
        status_code=status.HTTP_201_CREATED,
    )
    def assign_company_license(
        company_id: str,
        license_assignment: CompanyLicense,
    ) -> CompanyLicense:
        """Assign a license plan to a company."""

        if license_assignment.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="License company_id must match path company_id",
            )
        try:
            return licensing.assign_license(license_assignment)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get("/api/v1/companies/{company_id}/portfolio/customers", response_model=list[CorporateCustomer])
    def list_portfolio_customers(company_id: str) -> list[CorporateCustomer]:
        """List customers governed by one corporate portfolio."""

        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return corporate_portfolio.list_customers(company_id)

    @app.post(
        "/api/v1/companies/{company_id}/portfolio/customers",
        response_model=CorporateCustomer,
        status_code=status.HTTP_201_CREATED,
    )
    def register_portfolio_customer(
        company_id: str,
        customer: CorporateCustomer,
    ) -> CorporateCustomer:
        """Register a customer for corporate portfolio governance."""

        if customer.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer company_id must match path company_id",
            )
        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return corporate_portfolio.register_customer(customer)

    @app.get("/api/v1/companies/{company_id}/portfolio/programs", response_model=list[CorporateProgram])
    def list_portfolio_programs(company_id: str) -> list[CorporateProgram]:
        """List programs governed by one corporate portfolio."""

        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return corporate_portfolio.list_programs(company_id)

    @app.post(
        "/api/v1/companies/{company_id}/portfolio/programs",
        response_model=CorporateProgram,
        status_code=status.HTTP_201_CREATED,
    )
    def register_portfolio_program(company_id: str, program: CorporateProgram) -> CorporateProgram:
        """Register a program for corporate portfolio governance."""

        if program.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Program company_id must match path company_id",
            )
        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        try:
            return corporate_portfolio.register_program(program)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get("/api/v1/projects", response_model=list[PortfolioProject])
    def list_projects() -> list[PortfolioProject]:
        """List projects registered in the Corporate Control Tower portfolio."""

        return portfolio.list_projects()

    @app.get("/api/v1/companies/{company_id}/projects", response_model=list[PortfolioProject])
    def list_company_projects(company_id: str) -> list[PortfolioProject]:
        """List projects registered for one company."""

        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return portfolio.list_projects_for_company(company_id)

    @app.get("/api/v1/projects/{project_id}", response_model=PortfolioProject)
    def get_project(project_id: str) -> PortfolioProject:
        """Return one portfolio project."""

        project = portfolio.get_project(project_id)
        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return project

    @app.get("/api/v1/companies/{company_id}/projects/{project_id}", response_model=PortfolioProject)
    def get_company_project(company_id: str, project_id: str) -> PortfolioProject:
        """Return one project inside one company."""

        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        project = portfolio.get_project_for_company(company_id, project_id)
        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return project

    @app.post(
        "/api/v1/projects",
        response_model=PortfolioProject,
        status_code=status.HTTP_201_CREATED,
    )
    def register_project(project: PortfolioProject) -> PortfolioProject:
        """Register a project in the Corporate Control Tower portfolio."""

        try:
            return corporate_portfolio.register_project(project)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/projects",
        response_model=PortfolioProject,
        status_code=status.HTTP_201_CREATED,
    )
    def register_company_project(company_id: str, project: PortfolioProject) -> PortfolioProject:
        """Register a project inside one company."""

        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        try:
            return corporate_portfolio.register_project_for_company(company_id, project)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.patch("/api/v1/projects/{project_id}/governance-status", response_model=PortfolioProject)
    def change_governance_status(
        project_id: str,
        payload: GovernanceStatusPayload,
    ) -> PortfolioProject:
        """Change project governance status."""

        try:
            return portfolio.change_status(project_id, payload.status)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.patch(
        "/api/v1/companies/{company_id}/projects/{project_id}/governance-status",
        response_model=PortfolioProject,
    )
    def change_company_governance_status(
        company_id: str,
        project_id: str,
        payload: GovernanceStatusPayload,
    ) -> PortfolioProject:
        """Change project governance status inside one company."""

        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        try:
            return portfolio.change_status_for_company(company_id, project_id, payload.status)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.patch(
        "/api/v1/companies/{company_id}/projects/{project_id}/lifecycle",
        response_model=PortfolioProject,
    )
    def transition_project_lifecycle(
        company_id: str,
        project_id: str,
        payload: PortfolioLifecycleTransition,
    ) -> PortfolioProject:
        """Transition a project through the corporate portfolio lifecycle."""

        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        try:
            return portfolio.transition_lifecycle_for_company(company_id, project_id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/api/v1/companies/{company_id}/projects/{project_id}/portfolio-governance",
        response_model=CorporatePortfolioProjectView,
    )
    def project_portfolio_governance(
        company_id: str,
        project_id: str,
    ) -> CorporatePortfolioProjectView:
        """Return integrated portfolio governance for one project."""

        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        try:
            return corporate_portfolio.project_view(company_id, project_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/provisioning/websig",
        response_model=ProvisioningRequest,
        status_code=status.HTTP_202_ACCEPTED,
    )
    def provision_websig(payload: ProvisionWebSigPayload) -> ProvisioningRequest:
        """Request creation of a dedicated WEB SIG for a registered project."""

        try:
            request = provisioning.request_websig(payload.project_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return request

    @app.post(
        "/api/v1/companies/{company_id}/provisioning/project-stack",
        response_model=ProvisioningRequest,
        status_code=status.HTTP_202_ACCEPTED,
    )
    def provision_project_stack(company_id: str, payload: ProjectProvisioningSpec) -> ProvisioningRequest:
        """Provision a complete BIMSIG Enterprise project stack."""

        if payload.company.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provisioning company_id must match path company_id",
            )
        try:
            return provisioning_engine.provision_project_stack(payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/provisioning/project-stack/dry-run",
        response_model=ProvisioningRequest,
        status_code=status.HTTP_200_OK,
    )
    def dry_run_project_stack(company_id: str, payload: ProjectProvisioningSpec) -> ProvisioningRequest:
        """Return a project-stack provisioning plan without side effects."""

        if payload.company.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provisioning company_id must match path company_id",
            )
        try:
            return provisioning_engine.dry_run_project_stack(payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/provisioning/project-stack/execute",
        response_model=ProvisioningRequest,
        status_code=status.HTTP_202_ACCEPTED,
    )
    def execute_project_stack(company_id: str, payload: ProjectProvisioningSpec) -> ProvisioningRequest:
        """Execute project-stack provisioning through configured adapters."""

        return provision_project_stack(company_id, payload)

    @app.post(
        "/api/v1/companies/{company_id}/websig-factory/dry-run",
        response_model=ProvisioningRequest,
        status_code=status.HTTP_200_OK,
    )
    def dry_run_websig_factory(company_id: str, payload: ProjectProvisioningSpec) -> ProvisioningRequest:
        """Return a governed WEB SIG Factory plan without side effects."""

        if payload.company.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Factory company_id must match path company_id",
            )
        try:
            return provisioning_engine.dry_run_websig_factory(payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.post(
        "/api/v1/companies/{company_id}/websig-factory/execute",
        response_model=ProvisioningRequest,
        status_code=status.HTTP_202_ACCEPTED,
    )
    def execute_websig_factory(company_id: str, payload: ProjectProvisioningSpec) -> ProvisioningRequest:
        """Execute controlled WEB SIG Factory provisioning."""

        if payload.company.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Factory company_id must match path company_id",
            )
        try:
            return provisioning_engine.execute_websig_factory(payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get("/api/v1/provisioning/websig", response_model=list[ProvisioningRequest])
    def list_websig_provisioning_requests() -> list[ProvisioningRequest]:
        """List WEB SIG provisioning requests."""

        return provisioning.list_requests()

    @app.get("/api/v1/companies/{company_id}/provisioning/websig", response_model=list[ProvisioningRequest])
    def list_company_websig_provisioning_requests(company_id: str) -> list[ProvisioningRequest]:
        """List provisioning requests for one company."""

        if not companies.exists(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return provisioning.list_requests_for_company(company_id)

    @app.get("/api/v1/audit/events", response_model=list[AuditEvent])
    def list_audit_events(limit: int = 100) -> list[AuditEvent]:
        """List recent audit events."""

        return audit_repository.list(limit=limit)

    return app
