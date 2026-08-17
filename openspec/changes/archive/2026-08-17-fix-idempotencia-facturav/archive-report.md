# Archive Report

**Change**: fix-idempotencia-facturav
**Archived on**: 2026-08-17
**Archived to**: `openspec/changes/archive/2026-08-17-fix-idempotencia-facturav/`
**Mode**: openspec (file-based)
**Verify verdict**: PASS WITH WARNINGS — 0 CRITICAL, 2 WARNING (tareas 3.1/3.4/3.5 PENDING-MANUAL en prod; rama de duplicados de REQ-3 cubierta solo estáticamente). Las WARNING no son defectos de implementación: son verificaciones manuales de prod no ejecutables desde el entorno de verify.

## Spec Sync (Delta → Main Specs)

**Delta syncada**: `specs/ventas-idempotencia/spec.md` (dominio `ventas-idempotencia`).

La main spec **NO existía**: `openspec/specs/ventas-idempotencia/spec.md` fue creada a partir de la delta (contrato del skill: "si la main spec no existe, la delta es spec completo — copiarla"). La delta es **ADDED-only** sobre el dominio:

- **4 requisitos ADDED** (copiados verbatim con sus escenarios): Esquema de base de datos de idempotencia (2 escenarios), Aplicación idempotente de la migración (1 escenario), Pre-check de correlativos duplicados (2 escenarios), Estado de alembic_version consistente (2 escenarios).
- **0 MODIFIED, 0 REMOVED** — sin cambios destructivos (`rules.archive` de `config.yaml`: no aplica warning de merge destructivo).
- Se añadió sección **Propósito** (patrón de main specs del repo, ej. `articulos-api-json/spec.md`) y una **nota de merge** documentando que la main spec no existía y que los requisitos de aplicación (aceptación de `_idempotency_key`, detección de duplicados, late assignment, constraint compuesta) viven en la delta del cambio `idempotencia-en-ventas`, **aún activo** — se mergearán cuando ese cambio se archive.

## Pendiente de merge futuro (NO archivado como requirement)

- Los requisitos de aplicación de `idempotencia-en-ventas` (`openspec/changes/idempotencia-en-ventas/specs/ventas-idempotencia/spec.md`, cambio aún activo) NO se incluyeron en la main spec: le corresponden a ese cambio en su propio archive. Nota registrada en la main spec.

## Verificación manual pendiente en prod (carry-forward post-deploy)

Las tareas 3.1, 3.4 y 3.5 quedan PENDING-MANUAL — se ejecutan en prod tras el deploy, NO son defectos de implementación:

1. **3.1 Pre-flight `alembic_version`** (antes del deploy): `SELECT version_num FROM alembic_version;` → esperado `806cfc3bfdf2`. Si es `cc3c7d6e8978` (pyc huérfano): confirmar esquema real con DBA y `UPDATE alembic_version SET version_num = '806cfc3bfdf2';`. Pre-check de duplicados opcional: `SELECT punto_vta, nro_comprobante, idtipocomprobante, COUNT(*) FROM facturav GROUP BY 1,2,3 HAVING COUNT(*) > 1;` → 0 filas = se crea `idx_uq_comprobante`; >0 = queda diferido (avisar DBA).
2. **3.4 Smoke venta**: POST con `_idempotency_key` (UUID v4) sin error 1054; POST duplicado retorna la factura existente sin duplicar.
3. **3.5 Smoke regresión**: recibo cta cte (`services/ventas/ventas.py:333,367`), remito (`services/ventas/remitos.py:38`), listado `facturas-cli.html` (`routes/clientes.py:216,229`), NC (`routes/ventas.py:123`, key `None`).
4. **Post-deploy esquema (3.3 en prod)**: `SHOW COLUMNS FROM facturav LIKE 'idempotency_key';`, `SHOW INDEX FROM facturav;` (deben listarse `idx_uq_idempotency` e `idx_uq_comprobante`), `SELECT version_num FROM alembic_version;` (debe ser `c2d3df6d5f32`).

## Implementación y commit

- Revisión Alembic `migrations/versions/c2d3df6d5f32_add_idempotency_facturav.py` (`down_revision='806cfc3bfdf2'`): columna `idempotency_key` VARCHAR(36) NULL + `idx_uq_idempotency` + `idx_uq_comprobante`, existence-checked (`inspect()`), gate de duplicados (skip+warning, D3).
- Commit real: `9e8a33d` `feat(ventas): migración Alembic de idempotencia en facturav` (solo migración + artefactos openspec; SQL gitignored, no incluido). Nota: tasks.md 4.1 referencia `7bbef6d` (commit colgante); el commit verificado es `9e8a33d` (SUGGESTION del verify, se deja constancia aquí).
- Evidencia runtime local (BD espejo): no-op doble aplicación, fresh-create, downgrade preservando 3717 filas, esquema vía information_schema, single head.

## Archive Contents

- proposal.md ✅
- specs/ventas-idempotencia/spec.md ✅ (delta)
- design.md ✅
- tasks.md ✅ (11/14 `[x]`; 3.1, 3.4, 3.5 PENDING-MANUAL prod)
- exploration.md ✅
- verify-report.md ✅ (PASS WITH WARNINGS)
- archive-report.md ✅ (este reporte)

## Verification of Archive

- [x] Main spec creada: `openspec/specs/ventas-idempotencia/spec.md` (4 ADDED, copia de la delta + Propósito + nota de merge)
- [x] Change folder movido a `openspec/changes/archive/2026-08-17-fix-idempotencia-facturav/`
- [x] Contiene todos los artefactos (proposal, specs, design, tasks, exploration, verify-report)
- [x] `openspec/changes/` ya no tiene `fix-idempotencia-facturav/` activo
- [x] No se archiva con CRITICAL (verdict PASS WITH WARNINGS — WARNING son PENDING-MANUAL prod, no defectos)
- [x] Delta syncada ANTES del move
- [x] Merge no destructivo (0 MODIFIED, 0 REMOVED)

## SDD Cycle Complete

Planificado (propose) → explorado (exploration) → especificado (delta `ventas-idempotencia`) → diseñado (design) → implementado (apply, migración `c2d3df6d5f32`, commit `9e8a33d`) → verificado (PASS WITH WARNINGS, runtime local) → archivado (spec syncada en la main, 4 requisitos de esquema).

**Post-deploy pendiente**: verificación manual en prod (tareas 3.1, 3.4, 3.5 + esquema 3.3) — ver "Verificación manual pendiente en prod" arriba.

Ready for the next change.