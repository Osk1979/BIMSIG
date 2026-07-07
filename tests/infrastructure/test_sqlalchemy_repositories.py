from control_tower.domain.portfolio import PortfolioProject
from control_tower.domain.provisioning import ProvisioningRequest
from control_tower.infrastructure.database import (
    SqlAlchemyPortfolioProjectRepository,
    SqlAlchemyProvisioningRequestRepository,
    SqlAlchemySessionProvider,
    create_database_engine,
    initialize_database,
)


def test_sqlalchemy_project_repository_persists_records(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'repository.db'}"
    engine = create_database_engine(database_url)
    initialize_database(engine)
    sessions = SqlAlchemySessionProvider(engine)
    repository = SqlAlchemyPortfolioProjectRepository(sessions)

    repository.save(PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"))
    reloaded_repository = SqlAlchemyPortfolioProjectRepository(SqlAlchemySessionProvider(engine))

    assert reloaded_repository.exists("PSZ-2026")
    assert reloaded_repository.list()[0].name == "Proyecto Suiza"
    assert reloaded_repository.list_by_company("CRTG")[0].project_id == "PSZ-2026"


def test_sqlalchemy_provisioning_repository_persists_requests(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'provisioning.db'}"
    engine = create_database_engine(database_url)
    initialize_database(engine)
    sessions = SqlAlchemySessionProvider(engine)
    projects = SqlAlchemyPortfolioProjectRepository(sessions)
    requests = SqlAlchemyProvisioningRequestRepository(sessions)
    projects.save(PortfolioProject(project_id="PSZ-2026", company_id="CRTG", name="Proyecto Suiza"))

    saved = requests.save(ProvisioningRequest(request_id="PPE-001", project_id="PSZ-2026"))

    assert saved.request_id == "PPE-001"
    assert saved.project_id == "PSZ-2026"
