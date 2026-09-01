# Apply Progress: Rubros Dual View + Sucursal Reorder

## Summary

All implementation tasks (Phases 1-3) completed. Phase 4 (manual verification) pending.

## Completed Tasks

### Phase 1: Backend Service ✅
- [x] 1.1 Added `total_unidades` sum in `services/dashboard_gerencial.py` (line ~359)
- [x] 1.2 Updated return dict to include `'total_unidades': int(total_unidades)`

### Phase 2: Template Restructure ✅
- [x] 2.1 Moved Sucursal to full-width `col-12` BEFORE rubro section
- [x] 2.2 Wrapped Sucursal in its own `row mb-4` div
- [x] 2.3 Created new `row mb-4` div for rubro cards
- [x] 2.4 Created first rubro card `col-xl-6 col-lg-6` — "Ventas por Rubro — Monto"
- [x] 2.5 Canvas `#chartRubrosMonto`, table: Rubro | Importe | %
- [x] 2.6 Created second rubro card `col-xl-6 col-lg-6` — "Ventas por Rubro — Cantidad"
- [x] 2.7 Canvas `#chartRubrosCantidad`, table: Rubro | Unid. | %
- [x] 2.8 Both tables iterate `data.rubros.rubros`
- [x] 2.9 IDs: `seccion-rubros-monto` and `seccion-rubros-cantidad`

### Phase 3: JavaScript ✅
- [x] 3.1 Added `let chartRubrosCantidad = null;`
- [x] 3.2 Renamed canvas ref from `chartRubros` to `chartRubrosMonto`
- [x] 3.3 Added `crearGraficoRubrosCantidad()` — mirrors monto chart, uses `r.unidades`, tooltip `"X uds (Y%)"`
- [x] 3.4 Updated `destruirCharts()` to destroy `chartRubrosCantidad`
- [x] 3.5 Updated `inicializarDashboard()` — calls both chart creators + drill-down with selectors
- [x] 3.6 Updated monto drill-down call to pass `'#seccion-rubros-monto'`
- [x] 3.7 Modified `configurarDrillDownDoughnut(chart, tableSelector)` — param replaces hardcoded selector
- [x] 3.8 Updated HTMX `afterSwap` to handle both `seccion-rubros-monto` and `seccion-rubros-cantidad`
- [x] 3.9 Updated granularidad-btn handler to recreate both charts

## Files Changed

| File | Action | What Was Done |
|------|--------|---------------|
| `services/dashboard_gerencial.py` | Modified | Added `total_unidades` sum + included in return dict |
| `templates/dashboard-gerencial.html` | Modified | Reordered sucursal to full-width, created dual rubro cards |
| `static/js/dashboard-gerencial.js` | Modified | New chart variable, new function, updated lifecycle & HTMX |
| `openspec/changes/rubros-dual-view/tasks.md` | Modified | Marked Phases 1-3 tasks complete |

## Deviations from Design

None — implementation matches design exactly.

## Issues Found

None during implementation.

## Remaining Tasks

- [ ] 4.1 Manual: Load dashboard, verify sucursal table renders full-width above rubros
- [ ] 4.2 Manual: Verify both rubro doughnut charts render side by side
- [ ] 4.3 Manual: Verify monto chart shows revenue data, cantidad chart shows units data
- [ ] 4.4 Manual: Click monto doughnut segment → highlights correct row in monto table
- [ ] 4.5 Manual: Click cantidad doughnut segment → highlights correct row in cantidad table
- [ ] 4.6 Manual: Change date filter (HTMX refresh) → both charts destroy and recreate
- [ ] 4.7 Manual: Verify no CSP violations in browser console
- [ ] 4.8 Manual: Verify existing dashboard sections still work

## Status

24/32 tasks complete (Phases 1-3 done, Phase 4 manual verification pending). Ready for verify.
