# REV11 to REV12 Traceability

Current master architecture baseline: REV13 adoption is recorded in `docs/adr/ADR-0024-adopt-rev13-corporate-governance-baseline.md`.

| REV11 Source | Mandate | REV12 Artifact |
| --- | --- | --- |
| Documento A | Corporate Control Tower governs portfolio | `src/control_tower/domain/portfolio` |
| Documento A | Tower creates and registers WEB SIG | `src/control_tower/domain/provisioning`, ADR-0003 |
| Documento A | WEB SIG Factory must remain integrated through Project Provisioning Engine | ADR-0017, ADR-0022 |
| Documento A | NAS + PostGIS + GeoServer information core | ADR-0007, ADR-0008, ADR-0009 |
| Documento A | Google Workspace integration during transition | ADR-0010 |
| Documento A | BIMSIG Field must remain integrated through Enterprise architecture boundaries | ADR-0022 |
| Documento B | F2 Corporate Control Tower | Repository scope and API scaffold |
| Documento B | Each phase is organized by controlled phases | `docs/backlog/f2-corporate-control-tower-backlog.md` |
| Documento B | Each phase produces documentation, code, tests, version | `docs/`, `src/`, `tests/`, `pyproject.toml` |
| Documento C | Register architecture decisions before code | `docs/adr/ADR-0001..0003` |
| Documento C | Register architecture decisions before code | `docs/adr/ADR-0005-persistence-strategy.md` |
| Documento C | Register architecture decisions before code | `docs/adr/ADR-0006..0012` |
| Documento C | Register architecture decisions before code | `docs/adr/ADR-0013-database-schema-and-migrations.md` |
| PROMPT MASTER 002 | Multiple companies, multiple projects, one WEB SIG per project | ADR-0014, `docs/architecture/prompt-002-enterprise-control-tower-architecture.md` |
| PROMPT MASTER 002 | Tower never directly operates projects | ADR-0015 |
| PROMPT MASTER 002 | Tower administers licenses | ADR-0016 |
| PROMPT MASTER 002 | Users, companies, licenses, portfolio, KPIs, alerts, provisioning, integrations, dashboard, AI, reports, security, audit | `docs/backlog/prompt-002-enterprise-build-backlog.md` |
| PROMPT MASTER 003 | Project Provisioning Engine integrated to BIMSIG Enterprise | ADR-0017, `src/control_tower/application/provisioning_service.py` |
| PROMPT MASTER 003 | Create company, project, WEB SIG, PostGIS, NAS, document structure, GeoServer, dashboard, users, roles, and catalogs | `POST /api/v1/companies/{company_id}/provisioning/project-stack`, `docs/backlog/prompt-003-project-provisioning-engine-backlog.md` |
| PROMPT MASTER 004 | Corporate executive dashboard with portfolio, map, KPIs, risks, production, schedule, environmental, SSOMA, quality, users, licenses, AI, alerts, and comparisons | ADR-0018, `GET /dashboard`, `GET /api/v1/companies/{company_id}/dashboard/executive` |
| PROMPT MASTER 005 | NAS as Corporate Information Center with versioning, snapshots, backups, Google Drive, GeoServer, PostGIS, Docker, file types, permissions, and metadata | ADR-0019, `src/control_tower/domain/nas`, `docs/backlog/prompt-005-nas-information-center-backlog.md` |
| PROMPT MASTER 006 | Corporate user system for companies, projects, roles, specialties, permissions, licenses, authentication, SSO, audit, history, multitenancy, and enterprise security | ADR-0020, `src/control_tower/domain/enterprise`, `docs/backlog/prompt-006-corporate-user-security-backlog.md` |
| PROMPT MASTER 007 | DevSecOps across GitHub, Docker, CI/CD, testing, versioning, releases, ADR, backups, logs, monitoring, observability, and security | ADR-0021, `.github/workflows/ci.yml`, `Dockerfile`, `docs/backlog/prompt-007-devsecops-backlog.md` |
| PROMPT MASTER 008 | Permanent rule to verify the Master Architecture before code, preserve Enterprise structure, integrate through corporate systems, and scale to hundreds of simultaneous projects | ADR-0022, `scripts/validate_architecture.py`, `docs/operations/architecture-verification-checklist.md` |
| PROMPT MASTER 009 | Corporate GIS Administration for GeoServer and PostGIS governance without WEB SIG operation | ADR-0023, `src/control_tower/domain/gis`, `docs/backlog/prompt-009-corporate-gis-administration-backlog.md` |
| PROMPT MASTER 010 | Adopt REV13 Corporate Governance System baseline and map REV13 ADR-0009 to local ADR-0024 | ADR-0024, `docs/traceability/rev13-adoption-traceability.md`, `docs/backlog/prompt-010-rev13-adoption-backlog.md` |
