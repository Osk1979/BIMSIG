# PROMPT CTO-104D - Enterprise Wizard Product Experience

ADR references:
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0025: Corporate Portfolio Domain.
- ADR-0029: Corporate Workflow Engine.
- ADR-0030: Enterprise Wizard.

## Objetivo

Convertir el Enterprise Wizard en un asistente corporativo de producto para
crear, pausar, reanudar y activar proyectos gobernados por Corporate Control
Tower sin crear dominios nuevos ni operar la WEB SIG.

## Alcance Implementado

- Centro de mando del Wizard con progreso visible.
- Diez pasos oficiales: Empresa, Programa, Proyecto, Ubicacion administrativa,
  Especialidades, WEB SIG, GIS, NAS, Usuarios y Activacion.
- Detalle de paso seleccionado con proposito, fuente, estado, datos y faltantes.
- Validacion independiente por paso con mensajes ejecutivos.
- Inicio de sesion real contra `/api/v1/enterprise-wizard`.
- Guardado parcial real por paso contra la API existente.
- Reanudacion desde la sesion persistida mas reciente.
- Resumen antes de activar con trazabilidad hacia Workflow, Portfolio, GIS, NAS,
  Auditoria y WEB SIG.
- Activacion final solo cuando la sesion esta `ready`.
- Estados bloqueados por permisos usando la matriz RBAC existente.
- Auditoria visual consumida desde eventos existentes.

## Fuera de Alcance

- No se crean dominios nuevos.
- No se modifica arquitectura ni ADR.
- No se implementa operacion WEB SIG.
- No se edita GIS ni geometria.

## Criterios de Aceptacion

- El usuario puede iniciar una sesion del Wizard desde la pantalla.
- El usuario puede guardar avance parcial y reanudar una sesion existente.
- Cada paso muestra datos minimos, estado y faltantes sin lenguaje tecnico
  excesivo.
- El Wizard expone el resumen de activacion antes de confirmar.
- La activacion mantiene trazabilidad en Workflow, Portfolio, GIS, NAS y
  Auditoria mediante servicios existentes.
- La experiencia es responsive para desktop, laptop y tablet.
