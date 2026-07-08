# REV13 Adoption Traceability

| REV13 Source | Mandate | Repository Artifact |
| --- | --- | --- |
| Documento A | Corporate Control Tower is Corporate Governance System, not ERP and not simple dashboard | ADR-0024 |
| Documento A | REV13 ADR-0009 defines Tower governance scope | ADR-0024 maps REV13 ADR-0009 to local numbering |
| Documento A | WEB SIG SUITE operates each project | ADR-0015, ADR-0024 |
| Documento A | WEB SIG Factory creates new WEB SIG instances | ADR-0017, ADR-0024 |
| Documento A | NAS + PostGIS + GeoServer are information core | ADR-0007, ADR-0008, ADR-0009, ADR-0023 |
| Documento A | Google Workspace transition requires closure/permanence decision | ADR-0010, ADR-0024 |
| Documento A | BIMSIG Field PWA offline is a formal phase | ADR-0022, prompt-010 backlog |
| Documento A | Discipline Hub is a formal specialized workspace phase | prompt-010 backlog |
| Documento A | Corporate CDE, BIM Platform, PMO Digital, AI, Digital Twin, and Commercialization are formal phases | prompt-010 backlog |
| Documento B | F2 is Corporate Control Tower as Corporate Governance System | f2 backlog, ADR-0024 |
| Documento C | Prompt for F2 must include Corporate Governance System language | prompt-010 backlog |
| PROMPT MASTER 010 | Corporate Portfolio Domain governs companies, customers, programs, projects, lifecycle, WEB SIG Factory relationships, NAS, GIS, and dashboard references without operating WEB SIG | ADR-0025, prompt-010-corporate-portfolio-domain backlog, `src/control_tower/domain/portfolio/models.py` |
| PROMPT MASTER 011 | WEB SIG Factory controls dry-run, approval, execution, and portfolio references for new WEB SIG instances without operating project WEB SIG | ADR-0026, prompt-011-websig-factory-provisioning backlog, `src/control_tower/application/provisioning_service.py` |
| PROMPT MASTER 012 | Corporate Control Tower operational flow connects intake, governance, WEB SIG Factory, NAS, GIS, dashboard, audit, release, GitHub, and physical USB backup while preserving the Tower boundary | ADR-0027, prompt-012-operational-flow backlog, `docs/operations/corporate-control-tower-operational-flow.md` |
| PROMPT MASTER 013 | Corporate GIS Intelligence consumes WEB SIG GIS publications, registers corporate sources and layers, summarizes spatial portfolio indicators, and feeds the executive dashboard without editing project GIS | ADR-0028, prompt-013-corporate-gis-intelligence backlog, `src/control_tower/domain/corporate_gis_intelligence/models.py` |
| PROMPT CTO-101 | Corporate Workflow Engine orchestrates the official company-program-project-WEB SIG-NAS-PostGIS-GeoServer-dashboard-users-specialties-activation-operation-closure-archive process with auditable transitions and controlled rollback | ADR-0029, prompt-cto-101-corporate-workflow-engine backlog, `src/control_tower/domain/corporate_workflow/models.py` |
