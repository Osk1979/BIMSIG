# PROMPT HARDENING-001 - Enterprise Auth & SSO

## Objetivo

Reemplazar el modo local/sistema por autenticacion Enterprise preparada para
SSO real, manteniendo la frontera definida por ADR-0006 y ADR-0020.

## Implementado

- Modelo `AuthenticatedPrincipal`.
- Modelo `AuthSession`.
- Modelo `SsoProviderConfig` para preparacion OIDC/SAML.
- Servicio `EnterpriseAuthService` con tokens HMAC firmados.
- Login por identidad local/OIDC/SAML registrada.
- Logout con revocacion en memoria del proceso.
- Claims corporativos:
  - usuario
  - email
  - proveedor
  - subject
  - empresas
  - proyectos
  - roles
- Middleware de resolucion Bearer token.
- Modo estricto `CONTROL_TOWER_AUTH_REQUIRED=true`.
- Auditoria de creacion y revocacion de sesion.
- Pruebas unitarias, contractuales y de middleware.

## Restricciones

- No se implementa proveedor externo OIDC/SAML todavia.
- No se guardan secretos en codigo.
- No se implementa logica WEB SIG.
- El dashboard local sigue funcionando sin bloqueo mientras el modo estricto no
  este habilitado.

## Pendiente

- Persistir sesiones/revocaciones en repositorio durable.
- Validar discovery OIDC y metadata SAML real.
- Agregar CSRF/cookies seguras si se adopta sesion browser-cookie.
- Aplicar permisos finos por endpoint en HARDENING-002.
- Integrar login visual en la UI.
