# PROMPT CTO-107 - Corporate Reporting & Print Engine

## Objetivo

Construir el motor corporativo de reportes imprimibles de la Corporate Control
Tower REV13, consumiendo informacion ya gobernada por los dominios existentes.

## Alcance

- Plantillas corporativas versionables para portafolio, empresa, proyecto, GIS y
  auditoria.
- Emision de reporte HTML listo para impresion.
- Manifiesto auditable con fuente de datos, checksum y URI logica NAS.
- API para listar plantillas, previsualizar, emitir y obtener HTML imprimible.
- Evento de auditoria por cada emision formal.

## Restricciones

- No se crea un nuevo flujo operativo de WEB SIG.
- No se editan geometrias ni capas GIS.
- No se almacenan binarios en base de datos.
- El reporte referencia NAS mediante URI logica; la persistencia fisica queda en
  el Centro Corporativo de Informacion NAS.

## Criterios de aceptacion

- La API expone plantillas y emision de reportes.
- El reporte contiene estado ejecutivo, KPIs, portafolio y ubicacion
  administrativa.
- Cada emision produce checksum SHA-256 y evento de auditoria.
- El contrato OpenAPI queda versionado en `docs/api/openapi.yaml`.
- Existen pruebas unitarias y contractuales.
