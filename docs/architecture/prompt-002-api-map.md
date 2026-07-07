# PROMPT MASTER 002 API Map

## Existing API Groups

- `GET /health`
- `GET /api/v1/operational/health`
- `GET /api/v1/portfolio/summary`
- `GET /api/v1/projects`
- `POST /api/v1/projects`
- `GET /api/v1/projects/{project_id}`
- `PATCH /api/v1/projects/{project_id}/governance-status`
- `POST /api/v1/provisioning/websig`
- `GET /api/v1/provisioning/websig`
- `GET /api/v1/audit/events`

## Planned Enterprise API Groups

### Companies

- `GET /api/v1/companies`
- `POST /api/v1/companies`
- `GET /api/v1/companies/{company_id}`
- `PATCH /api/v1/companies/{company_id}`

Implemented first cut:

- `GET /api/v1/companies`
- `POST /api/v1/companies`
- `GET /api/v1/companies/{company_id}`

### Users and Memberships

- `GET /api/v1/users`
- `POST /api/v1/users`
- `GET /api/v1/companies/{company_id}/memberships`
- `POST /api/v1/companies/{company_id}/memberships`
- `PATCH /api/v1/companies/{company_id}/memberships/{membership_id}`

Implemented first cut:

- `GET /api/v1/users`
- `POST /api/v1/users`
- `GET /api/v1/companies/{company_id}/memberships`
- `POST /api/v1/companies/{company_id}/memberships`

### Licenses

- `GET /api/v1/license-plans`
- `POST /api/v1/license-plans`
- `GET /api/v1/companies/{company_id}/licenses`
- `POST /api/v1/companies/{company_id}/licenses`
- `GET /api/v1/companies/{company_id}/license-usage`

Implemented first cut:

- `GET /api/v1/license-plans`
- `POST /api/v1/license-plans`
- `GET /api/v1/companies/{company_id}/licenses`
- `POST /api/v1/companies/{company_id}/licenses`

### Portfolio and Projects

- `GET /api/v1/companies/{company_id}/portfolio/summary`
- `GET /api/v1/companies/{company_id}/projects`
- `POST /api/v1/companies/{company_id}/projects`
- `GET /api/v1/companies/{company_id}/projects/{project_id}`
- `PATCH /api/v1/companies/{company_id}/projects/{project_id}/governance-status`

Implemented first cut:

- `GET /api/v1/companies/{company_id}/portfolio/summary`
- `GET /api/v1/companies/{company_id}/projects`
- `POST /api/v1/companies/{company_id}/projects`
- `GET /api/v1/companies/{company_id}/projects/{project_id}`
- `PATCH /api/v1/companies/{company_id}/projects/{project_id}/governance-status`

### WEB SIG Registry

- `GET /api/v1/companies/{company_id}/websig-instances`
- `GET /api/v1/companies/{company_id}/projects/{project_id}/websig`
- `PATCH /api/v1/companies/{company_id}/projects/{project_id}/websig`

### Provisioning

- `POST /api/v1/companies/{company_id}/provisioning/project-stack`
- `POST /api/v1/companies/{company_id}/provisioning/project-stack/dry-run`
- `POST /api/v1/companies/{company_id}/provisioning/project-stack/execute`
- `POST /api/v1/companies/{company_id}/provisioning/websig/dry-run`
- `POST /api/v1/companies/{company_id}/provisioning/websig`
- `GET /api/v1/companies/{company_id}/provisioning/websig`
- `GET /api/v1/companies/{company_id}/provisioning/websig/{request_id}`
- `POST /api/v1/companies/{company_id}/provisioning/websig/{request_id}/approve`
- `POST /api/v1/companies/{company_id}/provisioning/websig/{request_id}/execute`

Implemented first cut:

- `POST /api/v1/companies/{company_id}/provisioning/project-stack`
- `POST /api/v1/companies/{company_id}/provisioning/project-stack/dry-run`
- `POST /api/v1/companies/{company_id}/provisioning/project-stack/execute`
- `GET /api/v1/companies/{company_id}/provisioning/websig`

### KPIs

- `GET /api/v1/companies/{company_id}/kpis/catalog`
- `POST /api/v1/companies/{company_id}/kpis/snapshots`
- `GET /api/v1/companies/{company_id}/kpis/snapshots`
- `GET /api/v1/companies/{company_id}/projects/{project_id}/kpis`

### Alerts

- `GET /api/v1/companies/{company_id}/alerts`
- `POST /api/v1/companies/{company_id}/alerts`
- `PATCH /api/v1/companies/{company_id}/alerts/{alert_id}`
- `POST /api/v1/companies/{company_id}/alerts/{alert_id}/acknowledge`

### Integrations

- `GET /api/v1/companies/{company_id}/integrations/health`
- `GET /api/v1/companies/{company_id}/integrations/nas/references`
- `GET /api/v1/companies/{company_id}/integrations/postgis/status`
- `GET /api/v1/companies/{company_id}/integrations/geoserver/status`
- `GET /api/v1/companies/{company_id}/integrations/google-drive/status`

### Executive Dashboard

- `GET /api/v1/companies/{company_id}/dashboard/executive`
- `GET /api/v1/companies/{company_id}/dashboard/portfolio`
- `GET /api/v1/companies/{company_id}/dashboard/integrations`

### AI

- `POST /api/v1/companies/{company_id}/ai/portfolio-summary`
- `POST /api/v1/companies/{company_id}/ai/alert-explanation`
- `POST /api/v1/companies/{company_id}/ai/report-draft`
- `GET /api/v1/companies/{company_id}/ai/interactions`

### Reports

- `POST /api/v1/companies/{company_id}/reports`
- `GET /api/v1/companies/{company_id}/reports`
- `GET /api/v1/companies/{company_id}/reports/{report_id}`

### Security and Audit

- `GET /api/v1/companies/{company_id}/security/roles`
- `GET /api/v1/companies/{company_id}/audit/events`
- `GET /api/v1/companies/{company_id}/audit/export`

## API Design Rules

- Company-scoped routes must include `company_id`.
- State-changing endpoints must create audit events.
- Protected endpoints must enforce authentication and authorization.
- AI endpoints must not bypass tenant, role, license, or audit policies.
- WEB SIG operational commands must remain WEB SIG-owned.
