# Tasks: Aplicar Redondeo en Cambio de Precio

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 160–200 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | single-pr |
| Chain strategy | size-exception |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Full change: redondeo module + integration + tests | PR 1 | Single PR, well under 400 lines |

## Phase 1: New Module — Pure Rounding Functions

- [x] 1.1 Create `services/articulos/redondeo.py` with `aplicar_redondeo(precio_base, multiplo, tipo, restar)` — handles arriba/abajo/cercano rounding with integer multiplo, passthrough when multiplo <= 0
- [x] 1.2 Add `calcular_precio_comercial(precio_lista, porcentaje, reglas_db)` to same file — computes precio_nuevo, finds matching rule by desde_precio/hasta_precio range, applies rounding or returns raw value

## Phase 2: Integration — Wire Into obtenerArticulosMarcaRubro

- [x] 2.1 Modify `services/articulos/articulos.py` — import `calcular_precio_comercial` from `.redondeo`
- [x] 2.2 Modify `obtenerArticulosMarcaRubro()` (line 290–312) — query `ReglaRedondeo.query.filter_by(activo=True).all()` once before loop, convert to `list[dict]`, replace L305–L310 calculation with `calcular_precio_comercial()` call per article
- [x] 2.3 Update `services/articulos/__init__.py` — add `aplicar_redondeo, calcular_precio_comercial` to imports from `.redondeo`

## Phase 3: Testing

- [x] 3.1 Create `tests/test_redondeo.py` — unit tests for `aplicar_redondeo()`: arriba (SCE-001), abajo (SCE-002), cercano (SCE-003), restar (SCE-004), edge cases (multiplo=0 passthrough, precio exacto en multiplo)
- [x] 3.2 Add unit tests for `calcular_precio_comercial()` — rule found within range, no matching rule (passthrough), multiple rules selecting correct one by range
- [x] 3.3 Add integration test in `tests/test_services_articulos.py` — mock `ReglaRedondeo.query`, verify `obtenerArticulosMarcaRubro()` applies rounding when rules exist and preserves raw prices when no rules active (SCE-007)
