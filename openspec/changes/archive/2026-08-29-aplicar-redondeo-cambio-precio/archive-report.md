# Archive Report: aplicar-redondeo-cambio-precio

## Final Status

**Change**: aplicar-redondeo-cambio-precio
**Archived to**: `openspec/changes/archive/2026-08-29-aplicar-redondeo-cambio-precio/`
**Date**: 2026-08-29
**Status**: COMPLETE ✅

## Summary

Implemented commercial rounding rules application during price calculation in the `obtenerArticulosMarcaRubro()` endpoint. Created a pure-function module (`redondeo.py`) that applies configurable rounding rules (arriba/abajo/cercano) with integer multiples and optional unit subtraction.

## Files Changed

| File | Action | Description |
|------|--------|-------------|
| `services/articulos/redondeo.py` | NEW | Pure rounding functions: `aplicar_redondeo()` and `calcular_precio_comercial()` |
| `services/articulos/articulos.py` | MODIFIED | Query rules once before loop, apply rounding per article |
| `services/articulos/__init__.py` | MODIFIED | Added exports: `aplicar_redondeo`, `calcular_precio_comercial` |
| `tests/test_redondeo.py` | NEW | Unit tests for rounding functions (13 tests) |
| `tests/test_services_articulos.py` | MODIFIED | Added integration tests for rounding in price calculation |

**Total files changed**: 5

## Test Results

- **Total tests**: 81
- **Passed**: 81 ✅
- **Failed**: 0
- **Skipped**: 0

### Test Coverage Breakdown
- `tests/test_redondeo.py`: 13 unit tests (pure functions)
- `tests/test_services_articulos.py`: 68 tests (existing + 13 new integration tests for rounding)

## Spec Compliance

**Compliance**: 9/9 scenarios ✅

| Requirement | Scenario | Test | Status |
|-------------|----------|------|--------|
| REQ-001 | SCE-001 — Redondeo arriba con multiplo=100 | `test_aplicar_redondeo_arriba` | ✅ COMPLIANT |
| REQ-001 | SCE-002 — Redondeo abajo con multiplo=100 | `test_aplicar_redondeo_abajo` | ✅ COMPLIANT |
| REQ-001 | SCE-003 — Redondeo cercano con multiplo=100 | `test_aplicar_redondeo_cercano` | ✅ COMPLIANT |
| REQ-001 | SCE-004 — Redondeo arriba con restar=10 | `test_aplicar_redondeo_con_restar` | ✅ COMPLIANT |
| REQ-002 | Regla encontrada se aplica | `test_calcular_precio_comercial_regla_encontrada` | ✅ COMPLIANT |
| REQ-002 | Sin regla aplicable, precio original se mantiene | `test_calcular_precio_comercial_sin_regla` | ✅ COMPLIANT |
| REQ-003 | SCE-007 — Sin reglas activas en DB | `test_obtener_articulos_sin_reglas_mantiene_calculo_original` | ✅ COMPLIANT |
| REQ-004 | SCE-006 — Múltiples artículos con distintos precios | `test_calcular_precio_comercial_multiples_reglas` | ✅ COMPLIANT |
| REQ-005 | Funciones importables desde paquete | Manual import verification | ✅ COMPLIANT |

## Deviations

**None**. Implementation matches spec exactly.

### Minor Observations (non-blocking)
1. **SCE-006 integration coverage**: The multiple-articles scenario (REQ-004) is covered by unit tests for `calcular_precio_comercial` with multiple rules, but lacks a full integration test with multiple articles and multiple rules in DB. The scenario is functionally correct.
   - **Recommendation**: Add integration test with 3 articles and 2 rules to fully verify SCE-006 (optional, low priority).

## Design Decisions Preserved

1. **Pure functions in separate module**: `redondeo.py` with no DB dependency — trivially testable
2. **Query rules once, convert to dicts**: Single query before loop, list comprehension to decouple from SQLAlchemy
3. **Fallback passthrough**: No matching rule → `round(precio_teorico, 2)` unchanged (backward compatible)
4. **math.ceil/math.floor with float conversion**: Sufficient precision for integer multiples and 2-decimal prices

## Lessons Learned

1. **Pure function extraction works well**: Separating rounding logic from ORM/query logic made testing straightforward and kept the module focused
2. **Dict conversion decouples layers**: Converting ORM objects to dicts before passing to business logic avoids SQLAlchemy dependency in pure functions
3. **Fallback passthrough is critical**: Backward compatibility when no rules exist prevented regressions during implementation
4. **Edge cases matter**: Multiplo=0, precio exacto en multiplo, and restar > resultado scenarios required careful handling

## Artifacts in Archive

- `proposal.md` ✅
- `specs/redondeo-cambio-precio/spec.md` ✅
- `design.md` ✅
- `tasks.md` ✅ (8/8 tasks complete)
- `verify-report.md` ✅
- `archive-report.md` ✅ (this file)

## Source of Truth Updated

The main spec now reflects the new behavior:
- `openspec/specs/redondeo-cambio-precio/spec.md`

## SDD Cycle Complete

The change has been fully planned, implemented, verified, and archived.
Ready for the next change.
