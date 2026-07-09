# WEB SIG Factory Template Adapter

## Objetivo

Conectar Corporate Control Tower con la plantilla independiente
`WEB_SIG_ENTERPRISE_REPOSITORY_REV02_FACTORY_TEMPLATE_WEB-SIG-001` sin absorber
logica operativa de WEB SIG.

## Implementado

- Adapter `WebSigFactoryTemplateProvisioningAdapter`.
- Configuracion por variables:
  - `CONTROL_TOWER_WEBSIG_FACTORY_TEMPLATE_PATH`
  - `CONTROL_TOWER_WEBSIG_FACTORY_OUTPUT_ROOT`
- Copia controlada de plantilla durante `websig_factory/execute`.
- Generacion de `websig.config.json` por instancia.
- Slots de WMS, WFS, WMTS y Vector Tiles preparados en el contrato.
- Metadatos de frontera Torre / WEB SIG.
- Prueba unitaria de creacion de instancia desde plantilla.

## Pendiente

- Ejecutar contra la ruta fisica final de la plantilla cuando exista en disco.
- Registrar checksum de plantilla fuente.
- Validar `websig.config.schema.json` de la plantilla.
- Publicar health report de la instancia para verificacion desde la Torre.
- Agregar limpieza o versionado controlado de instancias previas.

## Criterios de aceptacion

- Dry-run no genera efectos fisicos.
- Execute requiere `approved_by`.
- La instancia copia el template y genera contrato de configuracion.
- La Torre conserva rol de gobierno/provisioning/monitoreo.
- WEB SIG conserva rol de operacion de proyecto.
