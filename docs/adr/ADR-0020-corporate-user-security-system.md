# ADR-0020: Corporate User Security System

## Status

Accepted

## Context

PROMPT MASTER 006 requires a complete corporate user system for BIMSIG Enterprise.
The platform must administer users across companies and projects, with roles, specialties,
permissions, licenses, authentication, SSO, auditability, history, and enterprise security.

The architecture already separates domain, application ports, infrastructure adapters, and API
contracts. ADR-0006 defines authentication and authorization requirements. ADR-0014 defines
multi-company tenancy. ADR-0016 defines licensing. ADR-0019 defines NAS information governance.

## Decision

Corporate Control Tower REV12 will implement user security as a dedicated application service
backed by explicit repository ports and SQLAlchemy adapters.

The system will persist:

- Corporate specialties.
- User-specialty assignments.
- Project-scoped memberships.
- Role permissions by scope and action.
- Local, OIDC, and SAML authentication identities.
- User security history events.

The API will expose versioned endpoints for:

- Specialty management.
- User specialty assignment.
- Project membership assignment.
- Role permission grants.
- Authentication identity linking.
- SSO identity resolution.
- User history consultation.

The service stores only metadata and security records. It does not embed external SSO secrets or
replace the future identity provider. Production authentication must integrate through configured
identity provider adapters while this service remains the enterprise authorization and traceability
source inside the Tower.

## Consequences

- Users remain multi-company through company memberships and become multi-project through
  project memberships.
- Authorization checks can be evaluated by role, scope, action, company, and project.
- SSO identities can be resolved without coupling the domain to one provider.
- Security-sensitive changes are recorded in user history and global audit events.
- Migrations are required for every security table.

## Traceability

- PROMPT MASTER 006: Usuarios.
- ADR-0006: Authentication and authorization.
- ADR-0014: Enterprise multitenancy.
- ADR-0016: Enterprise licensing.
- ADR-0019: NAS Corporate Information Center.
