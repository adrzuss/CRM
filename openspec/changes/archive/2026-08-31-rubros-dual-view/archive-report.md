# Archive Report: Rubros Dual View + Sucursal Reorder

## Summary

Extended the dashboard gerencial's "Ventas por Rubro" section from a single revenue-only doughnut chart to a dual-view layout showing both revenue (monto) and units (cantidad) side by side. Reordered the "Ventas por Sucursal" table to full-width above the rubro sections for improved readability. All changes were purely frontend + one return dict field addition — no new endpoints, SQL queries, or database changes.

## Files Changed

| File | Action | Description |
|------|--------|-------------|
| `services/dashboard_gerencial.py` | Modified | Added `total_unidades` sum and included in `get_ventas_rubro()` return dict |
| `templates/dashboard-gerencial.html` | Modified | Reordered sucursal to full-width `col-12`, created dual rubro cards (`col-xl-6` each) |
| `static/js/dashboard-gerencial.js` | Modified | Added `chartRubrosCantidad` variable, new `crearGraficoRubrosCantidad()` function, updated `destruirCharts()`, `inicializarDashboard()`, `configurarDrillDownDoughnut()` (added `tableSelector` param), and HTMX `afterSwap` handlers |

## Key Decisions

1. **Server-side `total_unidades`**: Added to service return dict (1-line change) rather than computing client-side, maintaining consistency with existing `total_importe` pattern.

2. **Separate chart functions over parameterized factory**: Created `crearGraficoRubrosCantidad()` as a near-duplicate of `crearGraficoRubros()` rather than refactoring into a parameterized factory. This matched existing codebase patterns and avoided unnecessary refactoring risk for a display enhancement.

3. **`tableSelector` parameter on `configurarDrillDownDoughnut()`**: Added a second parameter instead of duplicating the function, keeping drill-down logic DRY.

4. **Layout reordering**: Moved sucursal from `col-xl-7` (side-by-side with rubros) to full-width `col-12` positioned before rubros, improving readability of the sucursal table.

## Issues Found and Resolved

None. Implementation matched the design exactly with no deviations.

## Verification Status

- ✅ Phases 1-3 (Backend, Template, JavaScript): All 24 tasks completed
- ⏳ Phase 4 (Manual verification): Pending — requires running dashboard in browser to verify:
  - Sucursal table renders full-width above rubros
  - Both rubro doughnut charts render side by side
  - Monto chart shows revenue, cantidad shows units
  - Drill-down highlights correct table in each chart
  - HTMX refresh destroys and recreates both charts
  - No CSP violations

## Spec Sync

Merged delta spec into main spec at `openspec/specs/dashboard-gerencial-stage1/spec.md`:
- **F7**: Added full-width (`col-12`) layout positioning before rubros, with new scenario "Sucursal full width antes de rubros"
- **F8**: Replaced single-view with dual-view (Monto + Cantidad), added 8 new scenarios covering both charts, drill-down, HTMX refresh, edge cases

## Archive Contents

- `proposal.md` ✅
- `specs/dashboard-gerencial-stage1/spec.md` ✅ (delta)
- `design.md` ✅
- `tasks.md` ✅ (24/32 tasks complete — Phase 4 manual verification pending)
- `apply-progress.md` ✅

## SDD Cycle Status

The change has been fully planned, implemented (Phases 1-3), and archived. Phase 4 (manual verification) remains pending for the user to validate in-browser behavior.
