# PROMPT CTO-102 Backlog: Enterprise Wizard

## Objetivo

Construir el asistente principal de la Corporate Control Tower para crear y
activar proyectos nuevos de forma guiada, reanudable y auditable.

## Alcance Implementado

- Dominio `enterprise_wizard` con pasos oficiales CTO-102.
- Validacion independiente por paso.
- Guardado de avance parcial y reanudacion posterior.
- Persistencia SQLAlchemy y migracion Alembic `20260708_014`.
- API REST para iniciar, listar, reanudar, validar, guardar y activar.
- Activacion usando servicios existentes de Empresa, Usuarios, Portfolio y
  Corporate Workflow Engine.
- Registro de referencias WEB SIG, GIS y NAS sin ejecutar logica operativa de
  WEB SIG.
- Pruebas unitarias, contractuales e infraestructura.
- OpenAPI versionado.

## Criterios de Aceptacion

- Cada paso puede validarse sin completar los demas.
- El Wizard conserva avance parcial.
- Una sesion puede reanudarse por `wizard_id`.
- La activacion exige que todos los pasos sean validos.
- La activacion crea registros gobernados y workflow auditable.
- No se implementa logica operativa propia de WEB SIG.
- Las reglas de validacion viven en el dominio, no en la UI.

## Pendientes Futuros

- Pantalla visual del Wizard en el dashboard.
- Catalogos dinamicos de especialidades y plantillas WEB SIG.
- Politicas de aprobacion por rol para activacion.
- Vista de sesiones pausadas y bloqueadas.
- Integracion asincrona con Project Provisioning Engine para ejecucion
  controlada posterior.

## ADR

- ADR-0030: Enterprise Wizard.
