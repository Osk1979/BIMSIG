# API Notes

The initial API is implemented with FastAPI and exposes OpenAPI at runtime.

The versioned OpenAPI contract is stored at `docs/api/openapi.yaml`.

## Endpoints

- `GET /health`: service health and REV marker.
- `GET /api/v1/operational/health`: operational service and database health.
- `GET /api/v1/operational/readiness`: readiness checks for CI/CD and orchestration.
- `GET /api/v1/operational/version`: deployable service version metadata.
- `GET /api/v1/companies`: list enterprise companies.
- `POST /api/v1/companies`: register an enterprise company.
- `GET /api/v1/companies/{company_id}`: get one enterprise company.
- `GET /api/v1/users`: list platform users.
- `POST /api/v1/users`: register a platform user.
- `GET /api/v1/companies/{company_id}/memberships`: list company memberships.
- `POST /api/v1/companies/{company_id}/memberships`: assign user role in company.
- `GET /api/v1/specialties`: list enterprise user specialties.
- `POST /api/v1/specialties`: create an enterprise user specialty.
- `GET /api/v1/users/{user_id}/specialties`: list specialties assigned to a user.
- `POST /api/v1/users/{user_id}/specialties`: assign a specialty to a user.
- `GET /api/v1/companies/{company_id}/projects/{project_id}/memberships`: list project memberships.
- `POST /api/v1/companies/{company_id}/projects/{project_id}/memberships`: assign a user role inside a project.
- `GET /api/v1/roles/{role}/permissions`: list permissions granted to an enterprise role.
- `POST /api/v1/roles/{role}/permissions`: grant a permission to an enterprise role.
- `GET /api/v1/users/{user_id}/auth-identities`: list authentication identities linked to a user.
- `POST /api/v1/users/{user_id}/auth-identities`: link an authentication identity to a user.
- `POST /api/v1/auth/sso/resolve`: resolve an SSO identity into a platform user.
- `GET /api/v1/users/{user_id}/history`: list user security history.
- `GET /api/v1/license-plans`: list license plans.
- `POST /api/v1/license-plans`: create a license plan.
- `GET /api/v1/companies/{company_id}/licenses`: list company licenses.
- `POST /api/v1/companies/{company_id}/licenses`: assign a license plan to company.
- `GET /dashboard`: integrated corporate executive dashboard UI.
- `GET /api/v1/companies/{company_id}/dashboard/executive`: company-scoped executive dashboard read model.
- `GET /api/v1/companies/{company_id}/nas/assets`: list Corporate Information Center assets.
- `POST /api/v1/companies/{company_id}/nas/assets`: register a Corporate Information Center asset.
- `GET /api/v1/nas/assets/{asset_id}`: get one information asset.
- `POST /api/v1/nas/assets/{asset_id}/versions`: register an information asset version.
- `GET /api/v1/nas/assets/{asset_id}/versions`: list information asset versions.
- `PATCH /api/v1/nas/assets/{asset_id}/metadata`: update information asset metadata.
- `PATCH /api/v1/nas/assets/{asset_id}/permissions`: set information asset permission.
- `PATCH /api/v1/nas/assets/{asset_id}/archive`: archive an information asset registry entry.
- `GET /api/v1/companies/{company_id}/nas/snapshots`: list information snapshots.
- `POST /api/v1/companies/{company_id}/nas/snapshots`: create an information snapshot.
- `GET /api/v1/companies/{company_id}/nas/backups`: list information backups.
- `POST /api/v1/companies/{company_id}/nas/backups`: register an information backup.
- `GET /api/v1/companies/{company_id}/portfolio/summary`: company-scoped portfolio counts.
- `GET /api/v1/companies/{company_id}/projects`: list company-scoped projects.
- `POST /api/v1/companies/{company_id}/projects`: register a project inside a company.
- `GET /api/v1/companies/{company_id}/projects/{project_id}`: get one company-scoped project.
- `PATCH /api/v1/companies/{company_id}/projects/{project_id}/governance-status`: change company-scoped project governance status.
- `POST /api/v1/companies/{company_id}/provisioning/project-stack`: provision a complete BIMSIG Enterprise project stack.
- `POST /api/v1/companies/{company_id}/provisioning/project-stack/dry-run`: preview project-stack provisioning steps without state changes.
- `POST /api/v1/companies/{company_id}/provisioning/project-stack/execute`: execute project-stack provisioning through configured adapters.
- `GET /api/v1/companies/{company_id}/provisioning/websig`: list provisioning requests for one company.
- `GET /api/v1/portfolio/summary`: portfolio counts by governance status.
- `GET /api/v1/projects`: list portfolio projects.
- `POST /api/v1/projects`: register a project in the portfolio.
- `GET /api/v1/projects/{project_id}`: get one portfolio project.
- `PATCH /api/v1/projects/{project_id}/governance-status`: change project governance status.
- `POST /api/v1/provisioning/websig`: request WEB SIG provisioning for a registered project.
- `GET /api/v1/provisioning/websig`: list WEB SIG provisioning requests.
- `GET /api/v1/audit/events`: list recent audit events.

## ADR References

- ADR-0001 defines REV11 as the architecture baseline.
- ADR-0002 defines the layered module structure.
- ADR-0003 defines provisioning as a port.
- ADR-0005 defines PostgreSQL/PostGIS as the production persistence direction.
- ADR-0006 defines actor and authorization requirements for protected operations.
- ADR-0014 defines enterprise multitenancy.
- ADR-0015 defines the Tower vs WEB SIG operational boundary.
- ADR-0016 defines enterprise licensing.
- ADR-0013 defines the first durable portfolio/provisioning schema.
- ADR-0017 defines the integrated Project Provisioning Engine.
- ADR-0018 defines the Corporate Executive Dashboard.
- ADR-0019 defines the NAS Corporate Information Center.
- ADR-0020 defines the Corporate User Security System.
- ADR-0021 defines the DevSecOps operating model.

## Configuration

The API reads `CONTROL_TOWER_DATABASE_URL`.

Project Provisioning Engine adapter configuration:

- `CONTROL_TOWER_NAS_ROOT`: enables NAS and document folder creation.
- `CONTROL_TOWER_POSTGIS_DATABASE_URL`: enables PostGIS schema creation.
- `CONTROL_TOWER_GEOSERVER_URL`: enables GeoServer workspace creation.
- `CONTROL_TOWER_GEOSERVER_USER` and `CONTROL_TOWER_GEOSERVER_PASSWORD`: optional GeoServer basic auth.

Default local development value:

```text
sqlite:///./control_tower.db
```

Production target:

```text
postgresql+psycopg://<user>:<password>@<host>:5432/<database>
```

Schema changes are managed through Alembic:

```bash
python -m alembic upgrade head
```

Regenerate the versioned OpenAPI contract:

```bash
python scripts/export_openapi.py
```
