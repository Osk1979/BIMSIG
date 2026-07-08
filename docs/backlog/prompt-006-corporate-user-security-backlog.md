# PROMPT MASTER 006 - Corporate User Security Backlog

## Scope

Build the Corporate User System for BIMSIG Enterprise without creating independent applications.
All user governance remains integrated into Corporate Control Tower REV12.

## Items

| ID | Item | Status | Traceability |
| --- | --- | --- | --- |
| P6-001 | Model corporate specialties | Done | ADR-0020 |
| P6-002 | Register user-specialty assignments | Done | ADR-0020 |
| P6-003 | Scope user memberships by company and project | Done | ADR-0014, ADR-0020 |
| P6-004 | Define role permissions by scope and action | Done | ADR-0006, ADR-0020 |
| P6-005 | Link local, OIDC, and SAML identities | Done | ADR-0006, ADR-0020 |
| P6-006 | Resolve SSO identity references through the API | Done | ADR-0020 |
| P6-007 | Persist user security history | Done | ADR-0020 |
| P6-008 | Audit specialty, membership, permission, and identity changes | Done | ADR-0020 |
| P6-009 | Add Alembic migration for security tables | Done | ADR-0013, ADR-0020 |
| P6-010 | Add unit and contract tests | Done | ADR-0020 |

## Deferred Enterprise Integrations

- External identity provider callback validation.
- SAML metadata ingestion.
- OIDC discovery document validation.
- License quota enforcement during user assignment.
- Fine-grained policy engine for compound conditions.
