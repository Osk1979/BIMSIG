# PROMPT CTO-104C - Corporate GIS Executive Viewer

## Objetivo

Convertir Corporate GIS Dashboard en un visor ejecutivo geoespacial corporativo
para lectura directiva del portafolio, sin editar geometria ni operar WEB SIG.

## Alcance implementado

- Lectura geoespacial ejecutiva del portafolio.
- Vistas ejecutivas:
  - Nacional.
  - Regional.
  - Empresa.
  - Programa.
  - Proyecto.
- Vistas tematicas:
  - Estado.
  - Riesgo.
  - Produccion.
  - Cronograma.
  - Calidad.
  - Ambiental.
  - SSOMA.
  - Predios.
  - Interferencias.
- Resumen espacial del portafolio.
- Comparativos espaciales entre proyectos.
- Panel de capas corporativas publicadas.
- Leyenda ejecutiva por capa y servicio.
- Detalle de proyecto seleccionado con region, provincia y distrito.
- Sincronizacion entre Radar Corporativo, Mapa GIS y Mapa Administrativo Peru.
- Slots WMS, WFS, WMTS y Vector Tiles preparados.

## Restricciones

- No se crean dominios nuevos.
- No se modifica arquitectura.
- No se modifica ADR.
- No se captura campo.
- No se editan geometrías.
- No se opera WEB SIG Enterprise.
- Solo se consumen Corporate Layers existentes o slots gobernados.

## Trazabilidad

- ADR-0018: Corporate executive dashboard.
- ADR-0023: Corporate GIS Administration.
- ADR-0028: Corporate GIS Intelligence.
- ADR-0025: Corporate Portfolio Domain.

## Criterios de aceptacion

- El visor explica donde estan los proyectos.
- El detalle indica region, provincia y distrito.
- Cada KPI visible se comunica con una capa GIS corporativa.
- La lectura es ejecutiva y no requiere herramientas GIS tecnicas.
- La separacion Corporate Control Tower / WEB SIG Enterprise se mantiene.
