# PROMPT CTO-104A - Corporate Home Operations Center

## Objetivo

Convertir la pantalla inicial de la Corporate Control Tower en el Centro de
Operaciones Corporativo que un Director puede abrir cada manana para revisar la
salud ejecutiva del portafolio.

## Alcance implementado

- Resumen ejecutivo de la manana.
- Tiles de estado: portafolio, alertas y readiness operacional.
- Accesos rapidos hacia Portafolio, Mapa Corporativo, Wizard y Reportes.
- Estado del portafolio, alertas, eventos recientes y acciones pendientes.
- Alertas prioritarias derivadas de workflow, GIS, NAS y WEB SIG.
- Actividad reciente alimentada desde auditoria cuando existe.
- Proximas acciones recomendadas segun datos existentes.
- Responsive para desktop, laptop y tablet.

## Restricciones

- No se crean dominios nuevos.
- No se modifica ADR.
- No se implementa logica operativa WEB SIG.
- La Home consume datos existentes de dashboard, portafolio, workflow, GIS,
  wizard, auditoria y reportes.

## Trazabilidad

- ADR-0018: Corporate executive dashboard.
- ADR-0025: Corporate Portfolio Domain.
- ADR-0027: Corporate Control Tower operational flow.
- ADR-0028: Corporate GIS Intelligence.
- ADR-0030: Enterprise Wizard.

## Criterios de aceptacion

- La Home no debe percibirse como un panel tecnico.
- Debe mostrar estado, alertas, actividad, accesos rapidos y resumen ejecutivo.
- Debe permitir navegar hacia los flujos principales de la Torre.
- Debe mantenerse dentro de Corporate Control Tower sin operar WEB SIG.
