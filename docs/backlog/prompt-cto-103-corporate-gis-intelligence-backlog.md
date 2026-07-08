# PROMPT CTO-103 Backlog: Corporate GIS Intelligence Maps

## Objetivo

Continuar Corporate GIS Intelligence usando el dominio existente, sin crear
modelos nuevos, para ofrecer mapas corporativos filtrados desde capas publicadas
por cada WEB SIG.

## Alcance Implementado

- Mapa Corporativo.
- Mapa Regional.
- Mapa por Empresa.
- Mapa por Programa.
- Mapa por Proyecto.
- Mapa Tematico.
- Filtros por:
  - Estado.
  - Riesgo.
  - Calidad.
  - SSOMA.
  - Ambiental.
  - Produccion.
  - Cronograma.
  - Predios.
  - Interferencias.
- Reutilizacion de `CorporateGisIntelligenceMap`, `CorporateLayer` y
  `CorporateGisSummary`.
- Sin edicion de capas.
- Sin nuevas tablas ni migraciones.

## Criterios de Aceptacion

- No se crean modelos nuevos.
- Las consultas consumen solo `CorporateLayer` publicadas.
- Los mapas por region, empresa, programa, proyecto y tema devuelven el mismo
  contrato versionado.
- Los filtros de negocio operan como vistas de lectura.
- La Torre no edita geometria, atributos ni capas WEB SIG.

## ADR

- ADR-0028: Corporate GIS Intelligence.
