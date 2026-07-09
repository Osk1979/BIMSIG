# PROMPT HARDENING-002 - RBAC UI Permissions

## Objetivo

Implementar permisos finos por usuario/rol en UI y API para Corporate Control
Tower, sin depender solo de ocultamiento visual.

## Implementado

- Matriz RBAC compartida en `RbacPolicy`.
- Roles corporativos:
  - `platform_admin`
  - `portfolio_manager`
  - `project_operator`
  - `auditor`
  - `service_account`
- Evaluacion por scope:
  - platform
  - company
  - project
  - nas
  - dashboard
  - provisioning
- Evaluacion por accion:
  - read
  - write
  - approve
  - execute
  - admin
- Endpoint `GET /api/v1/auth/permissions/matrix`.
- Middleware API con bloqueo `403` cuando `CONTROL_TOWER_AUTH_REQUIRED=true`.
- Auditoria `auth.permission.denied` para intentos bloqueados.
- UI con `data-rbac-scope` y `data-rbac-action`.
- Estado visual de acceso Enterprise/local.
- Pruebas unitarias y contractuales.

## Restricciones

- El modo local sigue sin bloqueo mientras `CONTROL_TOWER_AUTH_REQUIRED` no este
  activo.
- No se implementa todavia login visual.
- No se implementa logica WEB SIG.

## Pendiente

- Login/logout visual en dashboard.
- Politicas por endpoint mas granulares.
- Persistir politicas custom por empresa.
- Pantallas de "sin acceso" por seccion.
- Integrar firmas/aprobaciones digitales.
