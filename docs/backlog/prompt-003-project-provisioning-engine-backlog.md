# PROMPT MASTER 003 Project Provisioning Engine Backlog

## Goal

Build Project Provisioning Engine inside BIMSIG Enterprise so a company project stack can be provisioned from Corporate Control Tower without creating independent applications.

## Milestone P3.1: Integrated Provisioning Orchestration

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| P3-101 | Add Project Provisioning Engine service | Done | ADR-0017 | One application service orchestrates company, project, users, roles, and infrastructure registry steps. |
| P3-102 | Add enterprise project-stack API | Done | ADR-0017 | API provisions a company-scoped project stack through `/api/v1/companies/{company_id}/provisioning/project-stack`. |
| P3-103 | Store auditable provisioning steps | Done | ADR-0013, ADR-0017 | Provisioning requests persist operation, tenant scope, and step document. |
| P3-104 | Mark provisioned project active | Done | ADR-0015, ADR-0017 | A successful project-stack provisioning updates project status to `active`. |

## Milestone P3.2: Infrastructure Adapter Execution

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| P3-201 | Add PostGIS execution adapter | Done | ADR-0008, ADR-0017 | Engine creates a project schema when `CONTROL_TOWER_POSTGIS_DATABASE_URL` is configured. |
| P3-202 | Add NAS execution adapter | Done | ADR-0007, ADR-0017 | Engine creates project NAS folders when `CONTROL_TOWER_NAS_ROOT` is configured. |
| P3-203 | Add GeoServer execution adapter | Done | ADR-0009, ADR-0017 | Engine can create a GeoServer workspace when endpoint configuration is present. |
| P3-204 | Add dashboard execution adapter | Planned | ADR-0015, ADR-0017 | Engine creates or validates dashboard registry/runtime reference. |
| P3-205 | Add document repository execution adapter | Done | ADR-0007, ADR-0017 | Engine creates configured document folders under the NAS root. |

## Milestone P3.3: Governance Hardening

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| P3-301 | Add dry-run endpoint | Done | ADR-0003, ADR-0017 | API returns planned steps without state changes. |
| P3-302 | Add approval workflow | Planned | ADR-0006, ADR-0017 | Only authorized roles can approve execution. |
| P3-303 | Add step retry/failure model | Planned | ADR-0011, ADR-0017 | Failed steps can be inspected and retried safely. |
| P3-304 | Enforce license limits during provisioning | Planned | ADR-0016, ADR-0017 | Project, WEB SIG, user, and module limits block provisioning when exceeded. |
