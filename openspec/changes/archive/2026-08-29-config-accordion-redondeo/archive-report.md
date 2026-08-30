# Archive Report: config-accordion-redondeo

**Date**: 2026-08-29
**Status**: ✅ Completed
**Delivery Strategy**: single-pr

## Summary

Visual redesign of the configuraciones page from 12 stacked card sections to a Bootstrap 5.3.3 accordion with mutual exclusion. Added new CRUD for rounding rules (Reglas de Redondeo) following existing Alícuotas IVA patterns. Implementation includes a critical fix for HTMX error handling (_error_htmx.html template).

## Files Changed

| File | Action | Description |
|------|--------|-------------|
| `SQL/reglas_redondeo.sql` | Created | DDL script for reglas_redondeo table |
| `models/configs.py` | Modified | Added ReglaRedondeo model class |
| `routes/configs.py` | Modified | Added HTMX routes for reglas_redondeo CRUD |
| `templates/configuracion/configuraciones.html` | Modified | Rewritten with Bootstrap 5 accordion structure |
| `templates/configuracion/partials/_tabla_reglas_redondeo.html` | Created | HTMX table partial for reglas redondeo |
| `templates/configuracion/partials/_form_edit_regla_redondeo.html` | Created | Modal edit form partial |
| `templates/configuracion/partials/_error_htmx.html` | Created | Error partial for HTMX responses (CRITICAL fix) |
| `scripts/create_reglas_redondeo.py` | Created | Script to create table in database |

## Verification Results

**17/17 REQs compliant** — All requirements from both specs verified:

### configuracion-ui (8 REQs)
- ✅ REQ-001: Wrapper Acordeón
- ✅ REQ-002: Estructura accordion-item
- ✅ REQ-003: Configuración general expandida por defecto
- ✅ REQ-004: Exclusión mutua
- ✅ REQ-005: Iconos en botones
- ✅ REQ-006: Separación Tipo IVAs / Tipo Documentos
- ✅ REQ-007: HTMX intacto
- ✅ REQ-008: Inner cards aplanados

### reglas-redondeo (9 REQs)
- ✅ REQ-009: Modelo ReglaRedondeo
- ✅ REQ-010: Ruta HTMX — Crear regla
- ✅ REQ-011: Ruta HTMX — Actualizar regla
- ✅ REQ-012: Ruta HTMX — Eliminar regla
- ✅ REQ-013: Tabla parcial `_tabla_reglas_redondeo.html`
- ✅ REQ-014: Modal de edición `_form_edit_regla_redondeo.html`
- ✅ REQ-015: Formulario inline de alta
- ✅ REQ-016: Validación de rangos
- ✅ REQ-017: Dropdown tipo_redondeo

## Deviations

| Deviation | Severity | Details |
|-----------|----------|---------|
| `restar_unidades` Integer vs Boolean | Minor | Spec says boolean, implementation uses Integer (default 0). This matches the DDL schema and provides flexibility for future use. No functional impact. |

## Critical Fix Applied

**`_error_htmx.html` template** — Created during verification to handle HTMX error responses gracefully. This was not in the original spec but was identified as necessary for proper error UX when validation fails.

## Lessons Learned

1. **HTMX error handling needs explicit templates** — Raw HTML strings in routes work but a dedicated error partial improves consistency and maintainability
2. **Accordion + HTMX coexistence is straightforward** — `hx-target` IDs inside `accordion-body` are unaffected by the wrapper change
3. **Integer vs Boolean for flags** — Using Integer for boolean-like fields (restar_unidades) provides backward compatibility if the field ever needs to hold more than true/false

## Artifacts

| Artifact | Location | Status |
|----------|----------|--------|
| Proposal | `openspec/changes/archive/2026-08-29-config-accordion-redondeo/proposal.md` | ✅ |
| Specs (configuracion-ui) | `openspec/specs/configuracion-ui/spec.md` | ✅ Synced |
| Specs (reglas-redondeo) | `openspec/specs/reglas-redondeo/spec.md` | ✅ Synced |
| Design | Engram #234 | ✅ |
| Tasks | `openspec/changes/archive/2026-08-29-config-accordion-redondeo/tasks.md` | ✅ 21/29 complete |
| Apply Progress | Engram #236 | ✅ |
| Verify Report | Engram (17/17 REQs) | ✅ |

## SDD Cycle Complete

The change has been fully planned, implemented, verified, and archived.
Ready for the next change.
