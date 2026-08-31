# Proposal: Rubro-Sucursal Comparison Table

## Intent

Management needs to see how each sucursal's sales mix differs from the overall average—e.g., does "Central" under-index in "Electro" while over-indexing in "Blanco"? This cross-tab comparison reveals sucursal-specific strengths and weaknesses across product categories.

## Scope

### In Scope
- New service function `get_rubro_sucursal_comparacion(desde, hasta)` that returns cross-tab data (rubros as rows, sucursales as columns) with participation percentages and comparison indicators.
- New HTMX API endpoint `/api/dashboard-gerencial/rubro-sucursal`.
- New full-width template section below existing Sucursales y Rubros cards, rendering a responsive cross-tab table.
- CSS for indicator arrows (↑ green, ↓ red) and grouped column headers.
- Extension of `get_datos_dashboard()` to include the new data.

### Out of Scope
- JavaScript interactivity (table is server-rendered with Jinja2).
- Changes to existing Sucursales or Rubros tables.
- New database tables or stored procedures.

## Capabilities

### New Capabilities
- `rubro-sucursal-comparison`: Cross-tab table showing rubro participation by sucursal with comparison indicators.

### Modified Capabilities
- `dashboard-gerencial-stage1`: Adds new section to the dashboard layout.

## Approach

Single SQL query grouping by `(rubro, sucursal)` using the same JOIN chain as `get_ventas_rubro`. Python pivots into cross-tab, calculates per-cell participation vs. benchmark (sucursal's overall share). Indicator: ↑ if cell% > benchmark%, ↓ if lower. When only 1 sucursal exists, hide indicator column.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `services/dashboard_gerencial.py` | Modified | Add `get_rubro_sucursal_comparacion()` (~70 lines), extend `get_datos_dashboard()` |
| `routes/dashboard_gerencial.py` | Modified | Import new function, add API endpoint (~8 lines) |
| `templates/dashboard-gerencial.html` | Modified | Add new full-width row after line 313 (~70 lines Jinja2) |
| `static/css/dashboard-gerencial.css` | Modified | Indicator arrow styles (~30 lines) |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Performance with many sucursales/rubros | Low | Single query, result set ≤300 rows, same pattern as existing functions |
| 1 sucursal makes comparison meaningless | Medium | Hide indicator column when `len(sucursales_headers) == 1` |
| Horizontal overflow on mobile | Medium | Use `table-responsive` wrapper (existing pattern) |

## Rollback Plan

Remove the new service function, API endpoint, template section, and CSS rules. No data migration required; revert is pure code removal.

## Dependencies

None.

## Success Criteria

- [ ] Cross-tab table renders with correct data for multi-sucursal scenarios.
- [ ] Indicators show ↑ when sucursal over-indexes, ↓ when under-indexes.
- [ ] Table hidden or indicator column hidden when only 1 sucursal exists.
- [ ] Empty state shown when no rubro data available.
- [ ] Responsive on mobile (horizontal scroll).
- [ ] CSP nonce applied to any inline scripts.