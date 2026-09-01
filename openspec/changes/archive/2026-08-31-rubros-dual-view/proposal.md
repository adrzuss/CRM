# Proposal: Rubros Dual View + Sucursal Reorder

## Intent

The dashboard gerencial shows "Ventas por Sucursal" and "Ventas por Rubro" side by side, but the rubro section only displays revenue (monto). Users need to analyze rubro performance by quantity (units) as well. Additionally, the sucursal table gets cramped at `col-xl-7` — moving it full-width above the rubros improves readability.

## Scope

### In Scope
1. Move "Ventas por Sucursal" above rubros at full width (`col-12`)
2. Add second "Ventas por Rubro — Cantidad" doughnut + table showing units per rubro
3. Both rubro sections side by side (`col-xl-6` each)
4. Backend: add `total_unidades` to `get_ventas_rubro()` return dict

### Out of Scope
- No new SQL queries or endpoints
- No new files — all changes extend existing files
- No changes to route layer or `get_datos_dashboard()`
- No new CSS classes (reuse existing `card-header2`, `table-dashboard`, `chart-pie`)

## Capabilities

### New Capabilities
None — this is a layout + data display enhancement to existing capabilities.

### Modified Capabilities
- `dashboard-gerencial-stage1` (F8: Ventas por Rubro): extend table to show two separate views (monto + cantidad) with independent doughnut charts; reorder sucursal section above rubros

## Approach

### Backend (1 line change)
`services/dashboard_gerencial.py` line 373: add `total_unidades` to return dict.

```python
total_unidades = sum(int(row.unidades or 0) for row in result)
return {'rubros': rubros, 'total_importe': total_importe, 'total_unidades': total_unidades}
```

### Template (`templates/dashboard-gerencial.html`)
Restructure lines 210-313:
1. Sucursal div: change `col-xl-7 col-lg-7` → `col-12`, move BEFORE rubros
2. New `div.row.mb-4` wrapping two rubro cards side by side:
   - **Monto**: `col-xl-6 col-lg-6` — canvas `#chartRubrosMonto`, table columns: Rubro | Importe | %
   - **Cantidad**: `col-xl-6 col-lg-6` — canvas `#chartRubrosCantidad`, table columns: Rubro | Unid. | %
3. Rename `#chartRubros` → `#chartRubrosMonto`
4. Rename `#seccion-rubros` → `#seccion-rubros-monto`, add `#seccion-rubros-cantidad`

### JavaScript (`static/js/dashboard-gerencial.js`)
1. Add `let chartRubrosCantidad = null;` (line 26)
2. New function `crearGraficoRubrosCantidad(rubros)` — same as `crearGraficoRubros` but uses `r.unidades` for data, tooltip shows `"X uds (Y%)"` where `pct = unidades / total_unidades * 100`
3. Update `destruirCharts()` to destroy `chartRubrosCantidad`
4. Update `inicializarDashboard()` to call both chart creators
5. Update `configurarDrillDownDoughnut()` to accept table selector param; monto targets `#seccion-rubros-monto`, cantidad targets `#seccion-rubros-cantidad`
6. Update HTMX `afterSwap` to re-parse both `#seccion-rubros-monto` and `#seccion-rubros-cantidad`
7. All inline scripts use `{{ g.nonce }}` for CSP

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `services/dashboard_gerencial.py:373` | Modified | Add `total_unidades` to return dict |
| `templates/dashboard-gerencial.html:210-313` | Modified | Reorder sections + add second rubro card |
| `static/js/dashboard-gerencial.js` | Modified | New chart instance, updated lifecycle handlers |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Chart.js doughnut color mismatch between two charts | Low | Both use same `PALETA` array, same rubro order — colors stay consistent |
| HTMX swap breaks second chart | Medium | `destruirCharts()` destroys both; `afterSwap` recreates both from `dataset.json` |
| Percentage calculation wrong for units chart | Low | Use `total_unidades` (not `total_importe`) for Cantidad chart percentage |

## Rollback Plan

Revert the 3 files to their pre-change state via `git checkout`. No database migrations, no new endpoints — pure frontend + one return dict field. Zero risk to data integrity.

## Dependencies

- Chart.js 4.4.1 (already in use)
- Bootstrap 5.3.3 (already in use)
- HTMX lifecycle (already wired)

## Success Criteria

- [ ] Sucursal table displays full-width above rubros
- [ ] Two rubro doughnut charts render side by side
- [ ] Monto chart shows revenue per rubro (same data as before)
- [ ] Cantidad chart shows units per rubro
- [ ] Drill-down click highlights correct table in both charts
- [ ] Filter refresh (HTMX) destroys and recreates both charts correctly
- [ ] No CSP violations (all inline scripts use nonce)
