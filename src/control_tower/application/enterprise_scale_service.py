"""Enterprise-scale portfolio data operations.

ADR references:
- ADR-0014: Enterprise multitenancy.
- ADR-0024: Corporate operating model.
- ADR-0025: Corporate Portfolio Domain.
"""

from __future__ import annotations

import math
import time
from collections import Counter

from pydantic import BaseModel, Field

from control_tower.application.enterprise_service import CompanyService
from control_tower.application.portfolio_service import CorporatePortfolioDomainService, PortfolioService
from control_tower.domain.enterprise import Company
from control_tower.domain.portfolio import (
    CorporateCustomer,
    CorporateProgram,
    PortfolioProject,
    ProjectLifecycleStage,
    ProjectStatus,
)


class EnterpriseScaleSeedRequest(BaseModel):
    """Controlled request to create a deterministic Enterprise demo dataset."""

    company_count: int = Field(default=5, ge=1, le=200)
    programs_per_company: int = Field(default=3, ge=1, le=50)
    projects_per_program: int = Field(default=20, ge=1, le=500)
    prefix: str = Field(default="ENT", min_length=2, max_length=16)


class EnterpriseScaleSeedResult(BaseModel):
    """Result of an Enterprise-scale seed operation."""

    companies: int
    customers: int
    programs: int
    projects: int
    duration_ms: float


class EnterpriseScaleProjectPage(BaseModel):
    """Paginated project page for large portfolio exploration."""

    total: int
    page: int
    page_size: int
    pages: int
    duration_ms: float
    items: list[PortfolioProject]


class EnterpriseScaleSearchResult(BaseModel):
    """Search result across companies, programs, and projects."""

    query: str
    companies: list[Company]
    programs: list[CorporateProgram]
    projects: list[PortfolioProject]
    duration_ms: float


class EnterpriseScaleSummary(BaseModel):
    """Aggregate metrics for Enterprise-scale data readiness."""

    companies: int
    customers: int
    programs: int
    projects: int
    projects_by_status: dict[str, int]
    projects_by_region: dict[str, int]
    duration_ms: float


class EnterpriseScaleIsolationReport(BaseModel):
    """Multi-company isolation validation report."""

    status: str
    checked_projects: int
    violations: list[str]
    duration_ms: float


class EnterpriseScaleService:
    """Coordinates deterministic seed, search, paging, and isolation checks."""

    def __init__(
        self,
        companies: CompanyService,
        portfolio: PortfolioService,
        corporate_portfolio: CorporatePortfolioDomainService,
    ) -> None:
        self._companies = companies
        self._portfolio = portfolio
        self._corporate_portfolio = corporate_portfolio

    def seed(self, request: EnterpriseScaleSeedRequest) -> EnterpriseScaleSeedResult:
        """Create or update a deterministic demo dataset for Enterprise scale checks."""

        started = time.perf_counter()
        customers = 0
        programs = 0
        projects = 0
        for company_index in range(1, request.company_count + 1):
            company_id = f"{request.prefix}-C{company_index:03d}"
            self._companies.register(
                Company(
                    company_id=company_id,
                    legal_name=f"{request.prefix} Empresa {company_index:03d} S.A.C.",
                    display_name=f"{request.prefix} Empresa {company_index:03d}",
                )
            )
            customer_id = f"{company_id}-CLI-001"
            self._corporate_portfolio.register_customer(
                CorporateCustomer(
                    customer_id=customer_id,
                    company_id=company_id,
                    legal_name=f"Cliente principal {company_id}",
                    display_name=f"Cliente {company_index:03d}",
                )
            )
            customers += 1
            for program_index in range(1, request.programs_per_company + 1):
                program_id = f"{company_id}-PRG-{program_index:03d}"
                self._corporate_portfolio.register_program(
                    CorporateProgram(
                        program_id=program_id,
                        company_id=company_id,
                        customer_id=customer_id,
                        name=f"Programa {program_index:03d} {company_id}",
                    )
                )
                programs += 1
                for project_index in range(1, request.projects_per_program + 1):
                    project_id = f"{program_id}-PRJ-{project_index:04d}"
                    self._corporate_portfolio.register_project(
                        PortfolioProject(
                            project_id=project_id,
                            company_id=company_id,
                            customer_id=customer_id,
                            program_id=program_id,
                            name=f"Proyecto Enterprise {company_index:03d}-{program_index:03d}-{project_index:04d}",
                            cui=f"CUI-{company_index:03d}{program_index:03d}{project_index:04d}",
                            status=_seed_status(project_index),
                            lifecycle_stage=_seed_lifecycle(project_index),
                            websig_instance_id=f"WEB-{project_id}",
                            nas_root_uri=f"nas://{company_id}/{project_id}",
                            gis_binding_id=f"GIS-{project_id}",
                            country="PE",
                            region=_seed_region(company_index),
                            province=_seed_region(company_index),
                            district=f"Distrito {project_index:03d}",
                            location_source="enterprise_scale_seed",
                            location_validation_status="validated",
                        )
                    )
                    projects += 1
        return EnterpriseScaleSeedResult(
            companies=request.company_count,
            customers=customers,
            programs=programs,
            projects=projects,
            duration_ms=_elapsed_ms(started),
        )

    def project_page(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        company_id: str | None = None,
        program_id: str | None = None,
        customer_id: str | None = None,
        status: ProjectStatus | None = None,
        lifecycle_stage: ProjectLifecycleStage | None = None,
        region: str | None = None,
        query: str | None = None,
    ) -> EnterpriseScaleProjectPage:
        """Return paginated and filtered project data."""

        started = time.perf_counter()
        projects = self._portfolio.list_projects_for_company(company_id) if company_id else self._portfolio.list_projects()
        filtered = _filter_projects(
            projects,
            program_id=program_id,
            customer_id=customer_id,
            status=status,
            lifecycle_stage=lifecycle_stage,
            region=region,
            query=query,
        )
        filtered.sort(key=lambda item: (item.company_id, item.program_id or "", item.project_id))
        page_size = min(max(page_size, 1), 500)
        page = max(page, 1)
        total = len(filtered)
        offset = (page - 1) * page_size
        items = filtered[offset : offset + page_size]
        return EnterpriseScaleProjectPage(
            total=total,
            page=page,
            page_size=page_size,
            pages=math.ceil(total / page_size) if total else 0,
            duration_ms=_elapsed_ms(started),
            items=items,
        )

    def search(self, query: str, limit: int = 25) -> EnterpriseScaleSearchResult:
        """Search companies, programs, and projects by user-facing identifiers."""

        started = time.perf_counter()
        needle = query.lower().strip()
        limit = min(max(limit, 1), 100)
        companies = [
            company
            for company in self._companies.list_companies()
            if _contains(needle, company.company_id, company.legal_name, company.display_name)
        ][:limit]
        all_programs = [
            program
            for company in self._companies.list_companies()
            for program in self._corporate_portfolio.list_programs(company.company_id)
        ]
        programs = [
            program
            for program in all_programs
            if _contains(needle, program.program_id, program.company_id, program.name, program.customer_id)
        ][:limit]
        projects = [
            project
            for project in self._portfolio.list_projects()
            if _contains(needle, project.project_id, project.company_id, project.name, project.cui, project.program_id)
        ][:limit]
        return EnterpriseScaleSearchResult(
            query=query,
            companies=companies,
            programs=programs,
            projects=projects,
            duration_ms=_elapsed_ms(started),
        )

    def summary(self) -> EnterpriseScaleSummary:
        """Return aggregate Enterprise-scale readiness metrics."""

        started = time.perf_counter()
        companies = self._companies.list_companies()
        projects = self._portfolio.list_projects()
        customer_count = sum(len(self._corporate_portfolio.list_customers(company.company_id)) for company in companies)
        program_count = sum(len(self._corporate_portfolio.list_programs(company.company_id)) for company in companies)
        return EnterpriseScaleSummary(
            companies=len(companies),
            customers=customer_count,
            programs=program_count,
            projects=len(projects),
            projects_by_status=dict(Counter(project.status.value for project in projects)),
            projects_by_region=dict(Counter(project.region or "unassigned" for project in projects)),
            duration_ms=_elapsed_ms(started),
        )

    def validate_isolation(self) -> EnterpriseScaleIsolationReport:
        """Validate that projects do not cross company boundaries."""

        started = time.perf_counter()
        violations: list[str] = []
        projects = self._portfolio.list_projects()
        for project in projects:
            if not self._companies.exists(project.company_id):
                violations.append(f"{project.project_id}: company {project.company_id} does not exist")
                continue
            if project.program_id is not None:
                program = next(
                    (
                        item
                        for item in self._corporate_portfolio.list_programs(project.company_id)
                        if item.program_id == project.program_id
                    ),
                    None,
                )
                if program is None:
                    violations.append(f"{project.project_id}: program {project.program_id} is outside company scope")
            if project.customer_id is not None:
                customer = next(
                    (
                        item
                        for item in self._corporate_portfolio.list_customers(project.company_id)
                        if item.customer_id == project.customer_id
                    ),
                    None,
                )
                if customer is None:
                    violations.append(f"{project.project_id}: customer {project.customer_id} is outside company scope")
        return EnterpriseScaleIsolationReport(
            status="ok" if not violations else "violations",
            checked_projects=len(projects),
            violations=violations,
            duration_ms=_elapsed_ms(started),
        )


def _filter_projects(
    projects: list[PortfolioProject],
    *,
    program_id: str | None,
    customer_id: str | None,
    status: ProjectStatus | None,
    lifecycle_stage: ProjectLifecycleStage | None,
    region: str | None,
    query: str | None,
) -> list[PortfolioProject]:
    needle = query.lower().strip() if query else None
    region_value = region.lower().strip() if region else None
    return [
        project
        for project in projects
        if (program_id is None or project.program_id == program_id)
        and (customer_id is None or project.customer_id == customer_id)
        and (status is None or project.status == status)
        and (lifecycle_stage is None or project.lifecycle_stage == lifecycle_stage)
        and (region_value is None or (project.region or "").lower() == region_value)
        and (
            needle is None
            or _contains(needle, project.project_id, project.company_id, project.name, project.cui, project.program_id)
        )
    ]


def _contains(needle: str, *values: str | None) -> bool:
    return any(needle in value.lower() for value in values if value)


def _elapsed_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 2)


def _seed_status(project_index: int) -> ProjectStatus:
    cycle = project_index % 5
    if cycle == 0:
        return ProjectStatus.CLOSED
    if cycle == 1:
        return ProjectStatus.REGISTERED
    if cycle == 2:
        return ProjectStatus.PROVISIONING_REQUESTED
    if cycle == 3:
        return ProjectStatus.ACTIVE
    return ProjectStatus.SUSPENDED


def _seed_lifecycle(project_index: int) -> ProjectLifecycleStage:
    stages = [
        ProjectLifecycleStage.INTAKE,
        ProjectLifecycleStage.PLANNING,
        ProjectLifecycleStage.PROVISIONING,
        ProjectLifecycleStage.EXECUTION,
        ProjectLifecycleStage.CLOSURE,
        ProjectLifecycleStage.ARCHIVED,
    ]
    return stages[project_index % len(stages)]


def _seed_region(company_index: int) -> str:
    regions = ["Lima", "Arequipa", "Cusco", "Piura", "La Libertad", "Junin"]
    return regions[(company_index - 1) % len(regions)]
