# Tasks: Rubros Dual View + Sucursal Reorder

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~85 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Delivery strategy | single-pr |
| Suggested split | Not needed |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Backend + Template + JS changes | PR 1 | All changes are tightly coupled; single PR keeps atomic scope |

## Phase 1: Backend Service

- [x] 1.1 Add `total_unidades` sum in `services/dashboard_gerencial.py` after line 358 (after `total_importe` sum)
- [x] 1.2 Update return dict at line 373 to include `total_unidades` key

## Phase 2: Template Restructure

- [x] 2.1 Move Sucursal div (lines 213-264) to be BEFORE rubro section, change class from `col-xl-7 col-lg-7` to `col-12`
- [x] 2.2 Wrap Sucursal in its own `row mb-4` div (full width row)
- [x] 2.3 Create new `row mb-4` div for rubro cards
- [x] 2.4 Inside new row, create first rubro card `col-xl-6 col-lg-6` with header "Ventas por Rubro — Monto"
- [x] 2.5 Inside first card: canvas `#chartRubrosMonto`, table columns: Rubro | Importe | %
- [x] 2.6 Inside new row, create second rubro card `col-xl-6 col-lg-6` with header "Ventas por Rubro — Cantidad"
- [x] 2.7 Inside second card: canvas `#chartRubrosCantidad`, table columns: Rubro | Unid. | %
- [x] 2.8 Both tables iterate over `data.rubros.rubros` (same data source)
- [x] 2.9 Update IDs: first card div `id="seccion-rubros-monto"`, second `id="seccion-rubros-cantidad"`

## Phase 3: JavaScript

- [x] 3.1 Add `let chartRubrosCantidad = null;` after line 26
- [x] 3.2 Rename canvas reference in `crearGraficoRubros()` from `'chartRubros'` to `'chartRubrosMonto'`
- [x] 3.3 Add new function `crearGraficoRubrosCantidad(rubros)` mirroring `crearGraficoRubros` but using `r.unidades` for data and tooltip showing `"X uds (Y%)"` with `pct = (unidades / rubros.total_unidades) * 100`
- [x] 3.4 Update `destruirCharts()` to also destroy `chartRubrosCantidad`
- [x] 3.5 Update `inicializarDashboard()` to call `crearGraficoRubrosCantidad(datos.rubros)` and `configurarDrillDownDoughnut(chartRubrosCantidad, '#seccion-rubros-cantidad')`
- [x] 3.6 Update existing `configurarDrillDownDoughnut(chartRubros)` call to pass `'#seccion-rubros-monto'` as second argument
- [x] 3.7 Modify `configurarDrillDownDoughnut(chart, tableSelector)` to accept `tableSelector` param and use it instead of hardcoded `#seccion-rubros`
- [x] 3.8 Update HTMX `afterSwap` handler to check both `el.id === 'seccion-rubros-monto'` and `el.id === 'seccion-rubros-cantidad'` and recreate respective charts

## Phase 4: Verification

- [ ] 4.1 Manual: Load dashboard, verify sucursal table renders full-width above rubros
- [ ] 4.2 Manual: Verify both rubro doughnut charts render side by side
- [ ] 4.3 Manual: Verify monto chart shows revenue data, cantidad chart shows units data
- [ ] 4.4 Manual: Click monto doughnut segment → highlights correct row in monto table
- [ ] 4.5 Manual: Click cantidad doughnut segment → highlights correct row in cantidad table
- [ ] 4.6 Manual: Change date filter (HTMX refresh) → both charts destroy and recreate
- [ ] 4.7 Manual: Verify no CSP violations in browser console (nonce used for inline scripts)
- [ ] 4.8 Manual: Verify existing dashboard sections (evolution, alerts, KPIs) still work
