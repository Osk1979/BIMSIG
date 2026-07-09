# PROMPT CTO-104E - Portfolio Explorer Organization Navigator

ADR references:
- ADR-0014: Enterprise multitenancy.
- ADR-0015: Tower vs WEB SIG operational boundary.
- ADR-0025: Corporate Portfolio Domain.
- ADR-0030: Enterprise Wizard.

## Objetivo

Transformar Portfolio Explorer en un navegador corporativo de organizacion, no
una tabla tecnica. La experiencia debe permitir leer la estructura Empresa ->
Programa -> Proyecto -> WEB SIG -> Estado y acceder a Dashboard, GIS, NAS,
Reportes y Auditoria.

## Alcance Implementado

- Busqueda corporativa por empresa, programa, proyecto, WEB SIG, cliente,
  contrato, responsable, ubicacion y estado.
- Filtros ejecutivos: Todos, Activos, WEB SIG y Atencion.
- Arbol organizacional expandible visual: empresa, programas y proyectos.
- Seleccion persistente de proyecto con `localStorage`.
- Panel de detalle del proyecto seleccionado.
- Lectura de ciclo de vida, WEB SIG, GIS, NAS, usuarios, licencias, alertas,
  ultima actividad y readiness del dashboard.
- Acciones disponibles hacia Dashboard, GIS, NAS, Reportes, Auditoria y Wizard
  respetando RBAC existente.
- Estados sin datos y sin acceso.

## Fuera de Alcance

- No se crean nuevos dominios.
- No se modifica arquitectura ni ADR.
- No se implementa operacion WEB SIG.

## Criterios de Aceptacion

- El usuario entiende la jerarquia Empresa -> Programa -> Proyecto.
- El explorador se siente como mapa organizacional operativo.
- El detalle de proyecto permite decidir siguiente accion.
- La navegacion conecta con Dashboard, Wizard, GIS, Reportes y Auditoria.
