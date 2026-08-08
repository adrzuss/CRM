# Archive Report

**Change**: fix-stock-sucursales-datatables
**Archived on**: 2026-08-07
**Archived to**: `openspec/changes/archive/2026-08-07-fix-stock-sucursales-datatables/`
**Mode**: openspec (file-based)
**Verify verdict**: PASS WITH WARNINGS — 0 CRITICAL, 1 WARNING (coordinación de entrega: commit `461fabd` en `style/table-header-colors`), 3 SUGGESTION. La WARNING de entrega fue resuelta por el orquestador vía branch surgery (commits movidos a `fix/stock-sucursales-datatables`, PR #3 abierto) ANTES de este archive.

## Spec Sync (Delta → Main Specs)

**Delta syncada**: `specs/articulos-api-json/spec.md` (capability `articulos-api-json`).

La main spec YA existía: `openspec/specs/articulos-api-json/spec.md` (creada por el archive de `fix-busqueda-articulos`, cubría 4 endpoints). La delta es **MODIFY** sobre esa main spec → merge, no copia:

- **Propósito**: actualizado de "4 endpoints" a **"5 endpoints"** — agrega `api_lst_stock_sucursales` a la enumeración (requisito del archive note).
- **Requisito "Guards de filtro vacío retornan la respuesta vacía" → MODIFIED**: ahora cubre también `api_lst_stock_sucursales` ("y también en `api_lst_stock_sucursales`") y agrega el escenario "Stock por sucursal sin filtros seleccionados". Se quita la anotación de delta `(Previously: …)` (metadata de merge, no contenido).
- **Requisito "Contrato DataTables de `api_lst_stock_sucursales`" → ADDED** (5 escenarios: carga inicial sin query string, búsqueda sin `order[0][column]`, respuesta plana con `id` oculto, orden por última sucursal, orden fuera de rango).
- **Requisito "Respuesta DataTables válida sin parámetro `order`" → PRESERVADO verbatim** (5 escenarios intactos, no mencionado en la delta).

Total: **1 ADDED, 1 MODIFIED, 0 REMOVED** — sin cambios destructivos (`rules.archive` de `config.yaml`: no aplica warning de merge destructivo).

## Follow-ups fuera de alcance (NO archivados como requirements)

Las SUGGESTION del verify NO se pliegan a la spec (siguen como follow-ups):

- **SUGGESTION 1**: typo `responso` en `routes/articulos.py` L618/L624 (define y usa, funcional) — sweep futuro.
- **SUGGESTION 2**: falta pytest dedicado para los escenarios de borde de orden (última sucursal / fuera de rango) — opcional, congelar el guard `order_by`.
- **SUGGESTION 3**: limpieza del working tree (`app.log` y `.pyc` trackeados quedaron modificados; no stageados).
- (Nota histórica del archivo hermano: WARNING previa de `recordsTotal`/`recordsFiltered` con cuenta única — sigue como decisión de usuario de ese cambio, ajena a la scope de este.)

## Implementación y commit

- Commit único `461fabd` (post-cherry-pick del orquestador: `be7498b`) → hoy en la rama `fix/stock-sucursales-datatables`, PR #3 abierto. La rama de origen (`style/table-header-colors`) quedó saneada.
- Archivos: `routes/articulos.py` (L595 default `draw`, L602 default `order_column`, L613 `return` en guard), `services/articulos/stock.py` L119 (guard `order_column is not None and order_column+1 < len(columns_names)`), + tests en `tests/test_articulos.py` (nuevos `test_api_lst_stock_sucursales_sin_parametros`, `test_api_lst_stock_sucursales_sin_order_column`).
- Evidencia: 51/51 pytest verde; runtime handler+guard 11/11 PASS.

## Archive Contents

- proposal.md ✅
- specs/articulos-api-json/spec.md ✅ (delta)
- design.md ✅
- tasks.md ✅ (12/12 `[x]` — Fase 1: 1.1–1.4, Fase 2: 2.1–2.3, Fase 3: 3.1–3.5)
- verify-report.md ✅ (PASS WITH WARNINGS)
- archive-report.md ✅ (este reporte)

## Verification of Archive

- [x] Main spec actualizada: `openspec/specs/articulos-api-json/spec.md` (Propósito 5 endpoints; 1 ADDED + 1 MODIFIED — merge sobre la main existente)
- [x] Change folder movido a `openspec/changes/archive/2026-08-07-fix-stock-sucursales-datatables/`
- [x] Contiene todos los artefactos (proposal, specs, design, tasks, verify-report)
- [x] `openspec/changes/` ya no tiene `fix-stock-sucursales-datatables/` activo
- [x] No se archiva con CRITICAL (verdict PASS WITH WARNINGS, WARNING de entrega resuelta antes)
- [x] Deltas syncadas ANTES del move
- [x] Merge no destructivo: contenido existente de la main preservado verbatim

## SDD Cycle Complete

Planificado (propose) → especificado (spec delta `articulos-api-json`) → diseñado (design) → implementado (apply, tasks completas) → verificado (PASS WITH WARNINGS, 51 pytest + runtime 11/11) → archivado (spec syncada en la main, 5 endpoints).

Ready for the next change.