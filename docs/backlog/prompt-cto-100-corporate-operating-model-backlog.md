# PROMPT CTO-100 Backlog: Corporate Operating Model

## Objetivo

Iniciar Fase 3 de Corporate Control Tower con arquitectura por dominios estable.
El foco deja de ser crear dominios nuevos y pasa a construir funcionamiento
operativo, procesos de negocio y experiencia de usuario.

## Regla Operativa

- No crear nuevos dominios salvo autorizacion mediante ADR.
- Reutilizar dominios existentes: Portfolio, Provisioning, Workflow, Wizard,
  NAS, GIS, GIS Intelligence, Dashboard, Audit y DevSecOps.
- Toda nueva funcionalidad debe conectar dominios existentes y producir valor
  operativo visible en la Torre.

## Alcance Implementado

- Modelo operativo corporativo dentro del dominio existente `operations`.
- Endpoint `GET /api/v1/companies/{company_id}/operations/model`.
- Integracion del modelo operativo al dashboard ejecutivo.
- Carriles operativos:
  - Intake corporativo.
  - Provisioning controlado.
  - Gobierno ejecutivo.
  - Inteligencia corporativa.
  - Continuidad y auditoria.
- Capacidades operativas:
  - Enterprise Wizard.
  - Corporate Workflow Engine.
  - Gobierno de Portafolio.
  - WEB SIG Factory.
  - NAS Corporate Information Center.
  - GIS Corporativo.
  - Auditoria y Continuidad.
- Acciones prioritarias calculadas desde controles pendientes.

## Criterios de Aceptacion

- No se crea un dominio nuevo.
- El modelo operativo usa datos de dominios existentes.
- El dashboard muestra el Modelo Operativo Corporativo.
- El API expone carriles, capacidades y acciones prioritarias.
- Las pruebas contractuales cubren el endpoint y dashboard.
- La implementacion referencia ADR-0027.

## ADR

- ADR-0027: Corporate Control Tower Operational Flow.
