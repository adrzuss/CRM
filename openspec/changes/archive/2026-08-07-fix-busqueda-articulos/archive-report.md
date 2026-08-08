# Archive Report

**Change**: fix-busqueda-articulos
**Archived on**: 2026-08-07
**Archived to**: `openspec/changes/archive/2026-08-07-fix-busqueda-articulos/`
**Mode**: openspec (file-based)
**Verify verdict**: PASS — 0 CRITICAL, 1 WARNING (semántica `recordsTotal`/`recordsFiltered`, comportamiento PREEXISTENTE, fuera de alcance; 1/7 escenarios partial, 6/7 compliant), 4 SUGGESTION

## Spec Sync (Delta → Main Specs)

**Una única delta syncada**: `specs/articulos-api-json/spec.md` (capability `articulos-api-json`).

No existía spec principal en `openspec/specs/` (directorio vacío) → la delta ES spec completa; se copió a:
`openspec/specs/articulos-api-json/spec.md`

- Requisito "Respuesta DataTables válida sin parámetro `order`" → ADDED (5 escenarios: carga inicial sin query string, búsqueda sin `order`, fallback a `'codigo'`, echo de `draw`, recuento de registros)
- Requisito "Guards de filtro vacío retornan la respuesta vacía" → ADDED (2 escenarios: `lst_precios` sin `idlista`; `lst_stock`/`lst_stock_faltantes` sin `idmarca`/`idrubro`)
- Total: 2 ADDED, 0 MODIFIED, 0 REMOVED

Normalización mínima al copiar (SOLO envoltura de delta, el texto de requisitos/escenarios queda verbatim):
- Cabecera `## ADDED Requirements` → `## Requirements` (los marcadores ADDED/MODIFIED/REMOVED son instrucciones de merge, no parte del contenido)
- Título interno alineado al nombre de la capability (`# Articulos API JSON`)

La WARNING del verify (conteo único post-filtro `recordsTotal`=`recordsFiltered`) NO se "corrige" en la spec: es comportamiento preexistente fuera de alcance y quedó documentada como breach documental + follow-up (no se debe reescribir la spec para que coincida con una implementación que no cumple el escenario).

## Follow-ups fuera de alcance (NO archivados en este cambio)

- **SUGGESTION 1 (documentado como futuro change)**: BUG LATENTE verificado en `routes/articulos.py:590-626` `api_lst_stock_sucursales` + `services/articulos/stock.py:119` (`obtener_stock_sucursales`): mismo patrón sin default `order_column` → `None+1` → TypeError → HTTP 500; y guard vacío (L606-612) sin `return`. Se creará un change separado: `fix-stock-sucursales-datatables`.
- **WARNING**: conteo `recordsTotal`/`recordsFiltered` con cuenta única post-filtro — decisión de usuario si la UI/counters lo requieren.
- **SUGGESTION 3**: aceptación manual en navegador (sin driver E2E en el proyecto).
- **SUGGESTION 4**: limpieza de working tree (`app.log` y el `.pyc` trackeados quedaron modificados; no staged).

## Archive Contents

- proposal.md ✅
- specs/articulos-api-json/spec.md ✅ (delta)
- design.md ✅
- tasks.md ✅ (13/13 `[x]`)
- verify-report.md ✅ (PASS)
- archive-report.md ✅ (este reporte)

## Verification of Archive

- [x] Spec principal actualizada: `openspec/specs/articulos-api-json/spec.md` (2 requisitos ADDED)
- [x] Change folder movido a `openspec/changes/archive/2026-08-07-fix-busqueda-articulos/`
- [x] Contiene todos los artefactos (proposal, specs, design, tasks, verify-report)
- [x] `openspec/changes/` ya no tiene el cambio activo
- [x] No se archivó con CRITICAL (verdict PASS)
- [x] Deltas syncadas ANTES del move

## Implementación y commit

- Commit único `eb59aaf` "fix(articulos): endpoints DataTables responden 200 sin parametro order" sobre HEAD `02ad8f0`.
- Archivos: `routes/articulos.py`, `services/articulos/reportes.py`, `services/articulos/precios.py`. Sin `app.log` ni `.pyc` en staging (patrón respetado).
- Nota: el hash reportado por el orquestador (`eb59b18`) difiere del hash real en git log (`eb59aaf`); se toma el repo como fuente de verdad.

## SDD Cycle Complete

Planificado (propose) → especificado (spec `articulos-api-json`) → diseñado (design) → implementado (apply, 13/13 tasks) → verificado (PASS, 49 pytest + harness 30/30) → archivado.

Ready for the next change.