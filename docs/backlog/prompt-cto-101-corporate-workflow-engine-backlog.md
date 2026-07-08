# PROMPT CTO-101 Backlog: Corporate Workflow Engine

## Objetivo

Implementar el motor corporativo que orquesta el flujo oficial de la Corporate
Control Tower sin incorporar logica operativa propia de la WEB SIG.

## Alcance Implementado

- Dominio `corporate_workflow` con stages oficiales REV13.
- Servicio `CorporateWorkflowEngine` para iniciar, avanzar, consultar y hacer
  rollback controlado.
- Persistencia SQLAlchemy y migracion Alembic `20260708_013`.
- API REST versionada para workflows corporativos y transiciones auditables.
- Auditoria de cada transicion y rollback.
- Integracion minima con Portfolio Domain para activar, cerrar y archivar
  proyectos desde etapas corporativas.
- Pruebas unitarias, contractuales e infraestructura.
- OpenAPI versionado en `docs/api/openapi.yaml`.

## Criterios de Aceptacion

- No se permite saltar etapas del flujo oficial.
- Cada avance genera una transicion persistente.
- Cada rollback genera una transicion marcada como `rollback=true`.
- El rollback solo vuelve a la etapa previamente completada.
- El workflow se mantiene scoping por `company_id`.
- La Torre no ejecuta logica interna de WEB SIG.
- El API expone inicio, listado, detalle, avance, rollback y transiciones.

## Pendientes Futuros

- Panel visual del workflow en el dashboard ejecutivo.
- Politicas configurables por rol para aprobar transiciones sensibles.
- Reglas de prerequisitos por etapa contra NAS, GIS, PostGIS y GeoServer.
- Ejecucion asincrona controlada por etapa usando los adaptadores existentes.
- Reporte corporativo de workflows abiertos, bloqueados y archivados.

## ADR

- ADR-0029: Corporate Workflow Engine.
