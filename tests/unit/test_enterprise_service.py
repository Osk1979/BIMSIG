from datetime import date

import pytest

from control_tower.application.enterprise_service import CompanyService, LicensingService, UserService
from control_tower.domain.enterprise import Company, CompanyLicense, CompanyMembership, LicensePlan, User
from tests.unit.fakes import FakeAuditEventRepository


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


def test_company_service_registers_company_and_audits() -> None:
    audit = FakeAuditEventRepository()
    service = CompanyService(FakeCompanyRepository(), audit)

    company = service.register(
        Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG")
    )

    assert company.company_id == "CRTG"
    assert audit.events[0].action == "company.registered"


def test_user_service_assigns_membership_only_for_existing_company_and_user() -> None:
    audit = FakeAuditEventRepository()
    companies = CompanyService(FakeCompanyRepository(), audit)
    users = UserService(FakeUserRepository(), FakeMembershipRepository(), companies, audit)
    companies.register(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    users.register_user(User(user_id="USR-001", email="admin@example.com", display_name="Admin"))

    membership = users.add_membership(
        CompanyMembership(
            membership_id="MEM-001",
            company_id="CRTG",
            user_id="USR-001",
            role="portfolio_manager",
        )
    )

    assert membership.role == "portfolio_manager"
    assert "membership.assigned" in {event.action for event in audit.events}


def test_user_service_rejects_membership_for_missing_user() -> None:
    companies = CompanyService(FakeCompanyRepository())
    users = UserService(FakeUserRepository(), FakeMembershipRepository(), companies)
    companies.register(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))

    with pytest.raises(ValueError):
        users.add_membership(
            CompanyMembership(
                membership_id="MEM-001",
                company_id="CRTG",
                user_id="USR-MISSING",
                role="portfolio_manager",
            )
        )


def test_licensing_service_assigns_existing_plan_to_company() -> None:
    audit = FakeAuditEventRepository()
    companies = CompanyService(FakeCompanyRepository(), audit)
    licensing = LicensingService(
        FakeLicensePlanRepository(),
        FakeCompanyLicenseRepository(),
        companies,
        audit,
    )
    companies.register(Company(company_id="CRTG", legal_name="CRTG S.A.C.", display_name="CRTG"))
    licensing.create_plan(LicensePlan(plan_id="PLAN-ENTERPRISE", name="Enterprise"))

    assigned = licensing.assign_license(
        CompanyLicense(
            company_license_id="LIC-001",
            company_id="CRTG",
            plan_id="PLAN-ENTERPRISE",
            valid_from=date(2026, 7, 7),
        )
    )

    assert assigned.company_license_id == "LIC-001"
    assert "company_license.assigned" in {event.action for event in audit.events}
