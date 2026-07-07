# PROMPT MASTER 002 Enterprise Build Backlog

## Goal

Build Corporate Control Tower REV12 as a complete enterprise platform for multiple companies, each with multiple projects, each project with one WEB SIG.

## Milestone P2.1: Enterprise Tenant Foundation

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| P2-101 | Add company domain model | Done | ADR-0014 | Companies can be created, listed, and audited. |
| P2-102 | Add tenant-scoped project model | Done | ADR-0014, ADR-0015 | Projects belong to exactly one company. |
| P2-103 | Add tenant context middleware/dependency | Planned | ADR-0006, ADR-0014 | API resolves company context before data access. |
| P2-104 | Add company-scoped migrations | Done | ADR-0013, ADR-0014 | Company, membership, license, and project tables include tenant scope and indexes. |

## Milestone P2.2: Users and Security

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| P2-201 | Add user model | Done | ADR-0006 | Users can be registered and audited. |
| P2-202 | Add company memberships | Done | ADR-0006, ADR-0014 | Users can belong to companies with roles. |
| P2-203 | Add authorization policy service | Planned | ADR-0006 | Protected operations enforce role checks. |
| P2-204 | Add service account model | Planned | ADR-0006 | Integrations use scoped service identities. |

## Milestone P2.3: Licensing

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| P2-301 | Add license plans | Done | ADR-0016 | Plans define module entitlements and limits. |
| P2-302 | Add company license assignment | Done | ADR-0016 | Companies receive active license plans. |
| P2-303 | Add license usage counters | Planned | ADR-0016 | User, project, WEB SIG, AI, and report usage is tracked. |
| P2-304 | Enforce license policies | Planned | ADR-0016 | Restricted actions fail when license limits are exceeded. |

## Milestone P2.4: WEB SIG Registry and Provisioning

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| P2-401 | Add WEB SIG instance registry | Planned | ADR-0003, ADR-0015 | Each project can have one registered WEB SIG. |
| P2-402 | Add provisioning dry-run plans | Planned | ADR-0003 | API returns planned actions without side effects. |
| P2-403 | Add provisioning approval workflow | Planned | ADR-0003, ADR-0006 | Approved users can approve provisioning. |
| P2-404 | Add provisioning execution workflow | Planned | ADR-0003 | Execution records step outcomes and audit events. |

## Milestone P2.5: Enterprise Integrations

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| P2-501 | Add NAS adapter contract | Planned | ADR-0007 | Logical NAS references are validated and stored. |
| P2-502 | Add PostGIS adapter contract | Planned | ADR-0008 | Portfolio spatial metadata can be persisted. |
| P2-503 | Add GeoServer adapter contract | Planned | ADR-0009 | Workspaces/layer references can be tracked. |
| P2-504 | Add Google Drive adapter contract | Planned | ADR-0010 | Transitional Drive references can be tracked. |
| P2-505 | Add integration health endpoints | Planned | ADR-0007, ADR-0008, ADR-0009, ADR-0010 | Dashboard can show integration health. |

## Milestone P2.6: KPIs and Alerts

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| P2-601 | Add KPI catalog | Planned | ADR-0015 | KPI definitions are company-scoped. |
| P2-602 | Add KPI snapshot ingestion | Planned | ADR-0015 | WEB SIG consolidated KPI snapshots can be stored. |
| P2-603 | Add alert model | Planned | ADR-0015 | Alerts can be created, listed, acknowledged, and audited. |
| P2-604 | Add alert rules | Planned | ADR-0015 | Threshold-based alert rules can be evaluated. |

## Milestone P2.7: Executive Dashboard

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| P2-701 | Add dashboard read model | Planned | ADR-0015 | API returns executive summary for a company. |
| P2-702 | Add portfolio health rollups | Planned | ADR-0015 | Dashboard summarizes status, KPIs, alerts, and provisioning. |
| P2-703 | Add license and integration panels | Planned | ADR-0016 | Dashboard shows license usage and integration health. |

## Milestone P2.8: AI and Reports

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| P2-801 | Add AI interaction model | Planned | ADR-0006, ADR-0016 | AI usage is tenant-scoped, licensed, and audited. |
| P2-802 | Add portfolio AI summary endpoint | Planned | ADR-0006, ADR-0016 | Authorized users can request governed summaries. |
| P2-803 | Add report model | Planned | ADR-0007, ADR-0016 | Reports are generated, stored, and referenced. |
| P2-804 | Add corporate report endpoints | Planned | ADR-0016 | Authorized users can create and list reports. |

## Milestone P2.9: Operational Hardening

| ID | Item | Status | ADR | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| P2-901 | Add observability baseline | Planned | ADR-0011 | Logs, health checks, and errors are standardized. |
| P2-902 | Add database backup/restore procedure | Planned | ADR-0005 | Restore drill is documented and testable. |
| P2-903 | Add release checklist | Planned | ADR-0012 | Releases require tests, OpenAPI export, GitHub push, and USB backup. |
