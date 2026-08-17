# Ventas Idempotencia

## Propósito

Requisitos de esquema de base de datos y comportamiento de migración para la idempotencia de ventas: la tabla `facturav` debe incluir la columna `idempotency_key` y los índices únicos `idx_uq_idempotency` e `idx_uq_comprobante`, con una revisión Alembic idempotente (existence-checked) y un pre-check de correlativos duplicados. Los requisitos de aplicación (aceptación de `_idempotency_key`, detección de duplicados, late assignment del correlativo, constraint compuesta) están especificados en la delta del cambio `idempotencia-en-ventas` (`openspec/changes/idempotencia-en-ventas/specs/ventas-idempotencia/spec.md`, aún sin archivar) y se integrarán a este spec cuando ese cambio se archive.

> Nota de merge (sdd-archive): este spec se creó a partir de la delta del cambio `fix-idempotencia-facturav` (único dominio `ventas-idempotencia`), que agregó SOLO requisitos de esquema/migración. La main spec no existía previamente en `openspec/specs/`.

## Requirements

### Requirement: Esquema de base de datos de idempotencia

La tabla `facturav` MUST incluir la columna `idempotency_key` (String(36), nullable) y los índices únicos `idx_uq_idempotency` (sobre `idempotency_key`) e `idx_uq_comprobante` (sobre `punto_vta`, `nro_comprobante`, `idtipocomprobante`).

#### Scenario: Columna e índices creados

- GIVEN una base de datos cuya tabla `facturav` no tiene columna `idempotency_key`
- WHEN se aplica la revisión Alembic del cambio
- THEN la columna `idempotency_key` SHALL existir en `facturav`
- AND los índices `idx_uq_idempotency` e `idx_uq_comprobante` SHALL existir

#### Scenario: Sin alteración de datos existentes

- GIVEN `facturav` contiene filas históricas
- WHEN se aplica la migración
- THEN ninguna fila existente SHALL modificarse ni eliminarse

### Requirement: Aplicación idempotente de la migración

La revisión Alembic MUST verificar la existencia previa de la columna y los índices antes de crearlos, de modo que aplicar la migración sobre un esquema ya migrado manualmente no falle ni duplique objetos.

#### Scenario: Doble aplicación (manual + Alembic)

- GIVEN la columna `idempotency_key` ya existe por aplicación manual previa
- WHEN la revisión Alembic se ejecuta
- THEN la migración SHALL completarse sin error
- AND no SHALL crearse la columna ni los índices por segunda vez

### Requirement: Pre-check de correlativos duplicados

La creación de `idx_uq_comprobante` MUST estar condicionada a un pre-check que confirme la ausencia de duplicados de (`punto_vta`, `nro_comprobante`, `idtipocomprobante`) en `facturav`.

#### Scenario: Sin duplicados

- GIVEN el pre-check no detecta duplicados
- WHEN se aplica la revisión
- THEN `idx_uq_comprobante` SHALL crearse en la misma migración

#### Scenario: Duplicados históricos presentes

- GIVEN el pre-check detecta al menos un duplicado
- WHEN se aplica la revisión
- THEN `idx_uq_comprobante` SHALL NOT crearse en esta migración
- AND la columna e `idx_uq_idempotency` SHALL crearse de todos modos
- AND la creación de `idx_uq_comprobante` SHALL diferirse a una migración posterior

### Requirement: Estado de alembic_version consistente

La revisión MUST partir de `alembic_version = 806cfc3bfdf2` y MUST dejar `alembic_version` en la nueva revisión tras aplicarse.

#### Scenario: Cadena de revisión normal

- GIVEN `alembic_version` apunta a `806cfc3bfdf2`
- WHEN se aplica la migración
- THEN `alembic_version` SHALL quedar en la nueva revisión

#### Scenario: Revisión huérfana detectada

- GIVEN `alembic_version` apunta a la revisión huérfana `cc3c7d6e8978` (pyc sin `.py` commiteado)
- WHEN se verifica el esquema real antes del deploy
- THEN `version_num` SHALL repararse al valor correcto antes de aplicar la migración