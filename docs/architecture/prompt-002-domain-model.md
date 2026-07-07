# PROMPT MASTER 002 Domain Model

## Core Entities

### Company

Represents an enterprise tenant.

Fields:

- `company_id`
- `legal_name`
- `display_name`
- `tax_id`
- `status`
- `created_at`
- `updated_at`

Relationships:

- Has many users through memberships.
- Has one or more licenses.
- Has many projects.
- Has integration settings.

### User

Represents a person or service identity.

Fields:

- `user_id`
- `email`
- `display_name`
- `identity_provider_subject`
- `status`

Relationships:

- Has many company memberships.
- Has role assignments.

### Company Membership

Represents user access to a company.

Fields:

- `membership_id`
- `company_id`
- `user_id`
- `role`
- `status`

### License Plan

Defines commercial entitlements.

Fields:

- `plan_id`
- `name`
- `max_users`
- `max_projects`
- `max_websig_instances`
- `enabled_modules`
- `ai_enabled`
- `reporting_enabled`

### Company License

Assigns a plan to a company.

Fields:

- `company_license_id`
- `company_id`
- `plan_id`
- `valid_from`
- `valid_to`
- `status`

### Project

Represents a portfolio project governed by the Tower.

Fields:

- `project_id`
- `company_id`
- `name`
- `cui`
- `status`
- `health_status`
- `websig_instance_id`

### WEB SIG Instance

Represents the operational system for one project.

Fields:

- `websig_instance_id`
- `company_id`
- `project_id`
- `base_url`
- `revision`
- `status`
- `provisioned_at`

### KPI Snapshot

Stores consolidated KPI values consumed by the Tower.

Fields:

- `kpi_snapshot_id`
- `company_id`
- `project_id`
- `kpi_code`
- `value`
- `unit`
- `period_start`
- `period_end`
- `source_system`

### Alert

Represents a consolidated alert event.

Fields:

- `alert_id`
- `company_id`
- `project_id`
- `severity`
- `category`
- `title`
- `status`
- `source_system`

### Provisioning Plan

Represents a dry-run or executable plan for WEB SIG creation.

Fields:

- `plan_id`
- `company_id`
- `project_id`
- `request_id`
- `status`
- `steps`

### Integration Reference

Stores external system references.

Fields:

- `integration_reference_id`
- `company_id`
- `project_id`
- `system`
- `resource_type`
- `resource_uri`
- `status`

### Report

Represents generated corporate output.

Fields:

- `report_id`
- `company_id`
- `project_id`
- `report_type`
- `status`
- `output_uri`
- `generated_by`

### AI Interaction

Stores governed AI usage metadata.

Fields:

- `ai_interaction_id`
- `company_id`
- `user_id`
- `purpose`
- `input_reference`
- `output_reference`
- `approved_action_id`

### Audit Event

Records state-changing events.

Fields:

- `event_id`
- `company_id`
- `actor`
- `action`
- `entity_type`
- `entity_id`
- `detail`
- `created_at`

## Aggregate Boundaries

- Company is the tenant root.
- Project belongs to exactly one company.
- WEB SIG instance belongs to exactly one project.
- KPI and alert records are consolidated read-side records.
- Audit is append-only.
- License enforcement is checked before creating users, projects, WEB SIG instances, AI actions, and reports.
